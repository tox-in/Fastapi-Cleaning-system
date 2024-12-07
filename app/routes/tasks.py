from fastapi import APIRouter, Depends, HTTPException, Request, Query, Path
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime
from app.database import get_db
from app.models import Reservation, Group, User, SpecializationType, RoleType
from app.schemas import (
    ReservationResponse,
    TaskListResponse,
    TaskStatusUpdate
)
from app.dependencies import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)

templates = Jinja2Templates(directory="app/templates")

def check_user_role(user: User, allowed_roles: List[str]):
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
        )

@router.get("/list", response_model=List[TaskListResponse])
async def task_list(
    status: Optional[str] = Query(None, enum=["pending", "in_progress", "completed"]),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of tasks based on user role and filters
    """
    query = db.query(Reservation)

    if current_user.role == RoleType.CHIEF:
        query = query.filter(Reservation.assigned_group.has(chief_id=current_user.id))
    elif current_user.role == RoleType.MEMBER:
        query = query.filter(Reservation.assigned_group_id.in_(
            db.query(Group.id).filter(Group.members.any(id=current_user.id))
        ))
    elif current_user.role == RoleType.CLIENT:
        query = query.filter(Reservation.client_id == current_user.id)
    
    if status:
        query = query.filter(Reservation.status == status)
    
    if date_from:
        query = query.filter(Reservation.cleaning_date >= date_from)
    if date_to:
        query = query.filter(Reservation.cleaning_date <= date_to)
    
    tasks = query.order_by(
        Reservation.priority.desc(),
        Reservation.cleaning_date
    ).all()
    
    return tasks

@router.put("/{task_id}/status", response_model=TaskListResponse)
async def update_task_status(
    task_id: int = Path(..., gt=0),
    status_update: TaskStatusUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update task status (Chief only)
    """
    check_user_role(current_user, [RoleType.CHIEF])
    
    task = (
        db.query(Reservation)
        .filter(
            Reservation.id == task_id,
            Reservation.assigned_group.has(chief_id=current_user.id)
        )
        .first()
    )
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = status_update.status
    if status_update.notes:
        task.notes = status_update.notes
    
    db.commit()
    db.refresh(task)
    return task

@router.get("/statistics")
async def task_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get task statistics based on user role
    """
    check_user_role(current_user, [RoleType.CHIEF, RoleType.ADMIN])
    
    query = db.query(Reservation)
    
    if current_user.role == RoleType.CHIEF:
        query = query.filter(Reservation.assigned_group.has(chief_id=current_user.id))
    
    total_tasks = query.count()
    completed_tasks = query.filter(Reservation.status == "completed").count()
    pending_tasks = query.filter(Reservation.status == "pending").count()
    in_progress_tasks = query.filter(Reservation.status == "in_progress").count()
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "in_progress_tasks": in_progress_tasks,
        "completion_rate": round(completion_rate, 2)
    }

@router.get("/calendar")
async def task_calendar(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get calendar view of tasks
    """
    query = db.query(Reservation)
    
    if current_user.role == RoleType.CHIEF:
        query = query.filter(Reservation.assigned_group.has(chief_id=current_user.id))
    elif current_user.role == RoleType.MEMBER:
        query = query.filter(Reservation.assigned_group_id.in_(
            db.query(Group.id).filter(Group.members.any(id=current_user.id))
        ))
    elif current_user.role == RoleType.CLIENT:
        query = query.filter(Reservation.client_id == current_user.id)
    
    if month and year:
        query = query.filter(
            func.extract('month', Reservation.cleaning_date) == month,
            func.extract('year', Reservation.cleaning_date) == year
        )
    
    tasks = query.order_by(Reservation.cleaning_date).all()
    
    calendar_data = {}
    for task in tasks:
        date_str = task.cleaning_date.strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        calendar_data[date_str].append(task)
    
    return calendar_data

@router.get("/workload")
async def group_workload(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get workload statistics for groups (Admin/Chief only)
    """
    check_user_role(current_user, [RoleType.ADMIN, RoleType.CHIEF])
    
    query = (
        db.query(
            Group.name,
            func.count(Reservation.id).label('total_tasks'),
            func.count(case([(Reservation.status == 'completed', 1)])).label('completed_tasks')
        )
        .outerjoin(Reservation)
        .group_by(Group.id)
    )
    
    if current_user.role == RoleType.CHIEF:
        query = query.filter(Group.chief_id == current_user.id)
    
    workload_stats = query.all()
    
    return [
        {
            "group_name": stats.name,
            "total_tasks": stats.total_tasks,
            "completed_tasks": stats.completed_tasks,
            "completion_rate": round((stats.completed_tasks / stats.total_tasks * 100), 2) if stats.total_tasks > 0 else 0
        }
        for stats in workload_stats
    ]
