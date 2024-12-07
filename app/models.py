from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean, Date, DECIMAL, DateTime, func, Table, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class RoleType(str, enum.Enum):
    CHIEF = "Chief"
    MEMBER = "Member"
    CLIENT = "Client"
    ADMIN = "Admin"

class PriorityType(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class SpecializationType(str, enum.Enum):
    SALON = "Salon Cleaning"
    KITCHEN = "Kitchen Cleaning"
    GARDENING = "Gardening Cleaning"
    BACKYARD = "Backyard Cleaning"
    POULTRY = "Poultry Cleaning"
    GLASS = "Glass Cleaning"
    LAUNDRY = "Laundry Cleaning"

group_members = Table(
    'group_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(Enum(RoleType))
    password_hash = Column(String)
    
    reservations = relationship("Reservation", back_populates="client")
    group_members = relationship("Group", secondary=group_members, back_populates="members" )
    group_as_chief = relationship("Group", back_populates="chief", uselist=False)

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    specialization = Column(Enum(SpecializationType))
    rating = Column(Float, default=0.0)
    chief_id = Column(Integer, ForeignKey("users.id"))

    chief = relationship("User", back_populates="group_as_chief")
    members = relationship("User", secondary=group_members, back_populates="group_members")
    reservations = relationship("Reservation", back_populates="assigned_group")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    cleaning_type = Column(String)
    address = Column(String)
    house_number = Column(String)
    cleaning_date = Column(DateTime)
    reservation_date = Column(DateTime, default=func.now())
    price = Column(Float)
    approved_by_client = Column(Boolean, default=False)
    approved_by_admin = Column(Boolean, default=False)
    priority = Column(Enum(PriorityType), default=PriorityType.MEDIUM)
    client_id = Column(Integer, ForeignKey('users.id'))
    assigned_group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    
    client = relationship("User", back_populates="reservations")
    assigned_group = relationship("Group", back_populates="reservations")
