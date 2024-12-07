from fastapi import APIRouter, Depends, HTTPException, Query, Path, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, select
from typing import List, Optional, Dict, Any
import logging
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import Reservation, Group, User, SpecializationType, RoleType
from app.schemas import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
    PriorityType
)
from app.dependencies import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/reservations",
    tags=["reservations"]
)

templates = Jinja2Templates(directory="app/templates")

def check_user_role(user: User, allowed_roles: List[str]):
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
        )

@router.post("/create", response_model=ReservationResponse)
async def create_reservation(
    reservation: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reservation for a client"""
    check_user_role(current_user, [RoleType.CLIENT])

    assigned_group = (
        db.query(Group)
        .filter(Group.specialization == reservation.cleaning_type)
        .order_by(Group.rating.desc())
        .first()
    )

    if not assigned_group:
        raise HTTPException(
            status_code=400,
            detail=f"No group available for {reservation.cleaning_type}"
        )

    new_reservation = Reservation(
        client_id=current_user.id,
        assigned_group_id=assigned_group.id,
        cleaning_type=reservation.cleaning_type,
        address=reservation.address,
        house_number=reservation.house_number,
        cleaning_date=reservation.cleaning_date,
        price=reservation.price,
        priority=reservation.priority
    )

    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation

@router.get("/dashboard/client", response_model=List[ReservationResponse])
async def client_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reservations for the current client"""
    check_user_role(current_user, [RoleType.CLIENT])
    
    reservations = (
        db.query(Reservation)
        .filter(Reservation.client_id == current_user.id)
        .order_by(Reservation.cleaning_date)
        .all()
    )
    return reservations

@router.get("/dashboard/admin", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard with statistics"""
    check_user_role(current_user, [RoleType.ADMIN])

    total_groups = db.query(func.count(Group.id)).scalar()
    total_members = db.query(func.count(User.id)).filter(User.role == RoleType.MEMBER).scalar()
    total_reservations = db.query(func.count(Reservation.id)).scalar()
    total_clients = db.query(func.count(User.id)).filter(User.role == RoleType.CLIENT).scalar()

    recent_reservations = (
        db.query(Reservation)
        .order_by(Reservation.reservation_date.desc())
        .limit(10)
        .all()
    )

    monthly_stats = (
        db.query(
            extract('month', Reservation.cleaning_date).label('month'),
            func.count(Reservation.id).label('count')
        )
        .group_by(extract('month', Reservation.cleaning_date))
        .all()
    )

    top_groups = (
        db.query(Group)
        .order_by(Group.rating.desc())
        .limit(5)
        .all()
    )

    context = {
        "request": request,
        "total_groups": total_groups,
        "total_members": total_members,
        "total_reservations": total_reservations,
        "total_clients": total_clients,
        "recent_reservations": recent_reservations,
        "monthly_stats": monthly_stats,
        "top_groups": top_groups
    }

    return templates.TemplateResponse("dashboard/admin_dashboard.html", context)

@router.get("/dashboard/chief")
async def chief_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reservations assigned to the chief's group"""
    check_user_role(current_user, [RoleType.CHIEF])
    
    reservations = (
        db.query(Reservation)
        .join(Group)
        .filter(Group.chief_id == current_user.id)
        .order_by(Reservation.cleaning_date)
        .all()
    )
    return reservations

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def reservation_detail(
    reservation_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific reservation"""
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    if (current_user.role == RoleType.CLIENT and reservation.client_id != current_user.id and
        current_user.role not in [RoleType.ADMIN, RoleType.CHIEF]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return reservation

@router.put("/{reservation_id}/approve")
async def approve_reservation(
    reservation_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a reservation (admin only)"""
    check_user_role(current_user, [RoleType.ADMIN])
    
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    reservation.approved_by_admin = True
    db.commit()
    return {"message": "Reservation approved successfully"}

@router.put("/{reservation_id}/rate")
async def rate_group(
    reservation_id: int,
    rating: int = Query(..., ge=1, le=5),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a group for a completed reservation"""
    check_user_role(current_user, [RoleType.CLIENT])
    
    reservation = (
        db.query(Reservation)
        .filter(
            Reservation.id == reservation_id,
            Reservation.client_id == current_user.id
        )
        .first()
    )
    
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    group = reservation.assigned_group
    group.rating = (group.rating + rating) / 2
    db.commit()
    
    return {"message": "Rating submitted successfully"}

from fastapi import Query

@router.get("", response_model=List[ReservationResponse])
async def get_all_reservations(
    db: Session = Depends(get_db),
):
    """
    Retrieve all reservations without authentication, limited to 50 rows at a time.
    """
    stmt = (
        select(
            Reservation.id,
            Reservation.cleaning_type,
            Reservation.address,
            Reservation.house_number,
            Reservation.cleaning_date,
            Reservation.price,
            Reservation.priority,
            Reservation.client_id,
            Reservation.assigned_group_id,
            Reservation.approved_by_client,
            Reservation.approved_by_admin
        )
        .limit(500000)
    )
    
    result = db.execute(stmt)
    reservations = result.all()
    
    # print(reservations)
    
    try:
        return [
            {
                "id": r.id,
                "cleaning_type": r.cleaning_type,
                "address": r.address,
                "house_number": r.house_number,
                "cleaning_date": r.cleaning_date,
                "price": r.price,
                "approved_by_client": r.approved_by_client,
                "approved_by_admin": r.approved_by_admin,
                "priority": r.priority.value,
                "client_id": r.client_id,
                "assigned_group_id": r.assigned_group_id
            }
            for r in reservations
        ]
    except Exception as e:
        logging.error(f"Error processing reservations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching reservations")


@router.get("/statistics", response_model=Dict[str, Any])
async def get_reservation_statistics(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive statistics about reservations
    """
    query = db.query(Reservation)
    
    if start_date:
        query = query.filter(Reservation.cleaning_date >= start_date)
    if end_date:
        query = query.filter(Reservation.cleaning_date <= end_date)
    
    total_count = query.count()
    total_revenue = db.query(func.sum(Reservation.price)).scalar() or 0
    
    pending_count = query.filter(Reservation.approved_by_admin == False).count()
    approved_count = query.filter(Reservation.approved_by_admin == True).count()
    
    priority_stats = (
        query.with_entities(
            Reservation.priority,
            func.count(Reservation.id)
        )
        .group_by(Reservation.priority)
        .all()
    )
    
    cleaning_type_stats = (
        query.with_entities(
            Reservation.cleaning_type,
            func.count(Reservation.id)
        )
        .group_by(Reservation.cleaning_type)
        .all()
    )
    
    monthly_stats = (
        query.with_entities(
            func.strftime('%Y-%m', Reservation.cleaning_date),
            func.count(Reservation.id),
            func.sum(Reservation.price)
        )
        .group_by(func.strftime('%Y-%m', Reservation.cleaning_date))
        .all()
    )
    
    return {
        "total_reservations": total_count,
        "total_revenue": float(total_revenue),
        "status_breakdown": {
            "pending": pending_count,
            "approved": approved_count
        },
        "priority_breakdown": {
            priority: count for priority, count in priority_stats
        },
        "cleaning_type_breakdown": {
            c_type: count for c_type, count in cleaning_type_stats
        },
        "monthly_breakdown": [
            {
                "month": month,
                "count": count,
                "revenue": float(revenue or 0)
            }
            for month, count, revenue in monthly_stats
        ]
    }
