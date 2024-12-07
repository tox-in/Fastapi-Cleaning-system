from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models import Group, User
from app.database import get_db
from app.schemas import (
    GroupCreate, 
    GroupResponse, 
    GroupBase,
    RoleType,
    SpecializationType
)
from sqlalchemy.sql import func

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)

@router.get("/", response_model=List[GroupResponse])
def list_groups(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
    specialization: Optional[SpecializationType] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Group)
    if specialization:
        query = query.filter(Group.specialization == specialization)
    groups = query.offset(skip).limit(limit).all()
    return groups

@router.get("/all", response_model=List[GroupResponse])
async def get_all_groups(
    db: Session = Depends(get_db)
):
    groups = db.query(Group).all()
    
    response_groups = []
    for group in groups:
        group_dict = {
            "id": group.id,
            "name": group.name,
            "specialization": group.specialization,
            "rating": group.rating,
            "chief_id": group.chief_id,
            "member_ids": [member.id for member in group.members]  # Extract just the IDs
        }
        response_groups.append(group_dict)
    
    return response_groups

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.post("/", response_model=GroupResponse)
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db)
):
    try:
        if db.query(Group).filter(Group.name == group.name).first():
            raise HTTPException(
                status_code=400,
                detail="Group with this name already exists"
            )

        chief = None
        if group.chief_id:
            chief = db.query(User).filter(
                User.id == group.chief_id,
                User.role == RoleType.CHIEF
            ).first()
            if not chief:
                raise HTTPException(
                    status_code=400,
                    detail="Chief not found or invalid role"
                )

        if len(group.member_ids) > 5:
            raise HTTPException(
                status_code=400,
                detail="A group cannot have more than 5 members"
            )

        members = db.query(User).filter(
            User.id.in_(group.member_ids),
            User.role == RoleType.MEMBER
        ).all()
        if len(members) != len(group.member_ids):
            raise HTTPException(
                status_code=400,
                detail="Some members not found or invalid role"
            )

        new_group = Group(
            name=group.name,
            specialization=group.specialization,
            chief_id=chief.id if chief else None,
            rating=group.rating
        )
        new_group.members = members
        
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return new_group

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database integrity error occurred"
        )

@router.put("/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int = Path(..., gt=0),
    group: GroupCreate = None,
    db: Session = Depends(get_db)
):
    existing_group = db.query(Group).filter(Group.id == group_id).first()
    if not existing_group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        if group.name != existing_group.name:
            if db.query(Group).filter(Group.name == group.name).first():
                raise HTTPException(
                    status_code=400,
                    detail="Group with this name already exists"
                )

        if group.chief_id:
            chief = db.query(User).filter(
                User.id == group.chief_id,
                User.role == RoleType.CHIEF
            ).first()
            if not chief:
                raise HTTPException(
                    status_code=400,
                    detail="Chief not found or invalid role"
                )
            existing_group.chief_id = chief.id

        if len(group.member_ids) > 5:
            raise HTTPException(
                status_code=400,
                detail="A group cannot have more than 5 members"
            )

        members = db.query(User).filter(
            User.id.in_(group.member_ids),
            User.role == RoleType.MEMBER
        ).all()
        if len(members) != len(group.member_ids):
            raise HTTPException(
                status_code=400,
                detail="Some members not found or invalid role"
            )
        
        existing_group.members = members
        existing_group.name = group.name
        existing_group.specialization = group.specialization
        existing_group.rating = group.rating

        db.commit()
        db.refresh(existing_group)
        return existing_group

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Database integrity error occurred"
        )

@router.delete("/{group_id}")
def delete_group(
    group_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    try:
        db.delete(group)
        db.commit()
        return {"message": "Group deleted successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Cannot delete group due to existing references"
        )
@router.get("/list", response_model=List[GroupResponse])
async def get_all_groups(
    db: Session = Depends(get_db)
):
    groups = db.query(Group).all()
    return groups
