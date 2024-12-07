from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Group, Reservation, RoleType, SpecializationType, PriorityType
from faker import Faker
import random
from datetime import datetime, timedelta
from passlib.context import CryptContext

fake = Faker()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_seed_data():
    db = SessionLocal()
    try:
        users = create_users(db)
        groups = create_groups(db, users)
        create_reservations(db, users, groups)
        
        db.commit()
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

def create_users(db: Session, num_users=150):
    users = []
    
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=pwd_context.hash("admin123"),
        role=RoleType.ADMIN
    )
    users.append(admin)
    
    for i in range(20):
        chief = User(
            username=f"chief_{fake.unique.user_name()}",
            email=fake.unique.email(),
            password_hash=pwd_context.hash("password123"),
            role=RoleType.CHIEF
        )
        users.append(chief)
    
    for i in range(50):
        member = User(
            username=f"member_{fake.unique.user_name()}",
            email=fake.unique.email(),
            password_hash=pwd_context.hash("password123"),
            role=RoleType.MEMBER
        )
        users.append(member)
    
    for i in range(79):
        client = User(
            username=f"client_{fake.unique.user_name()}",
            email=fake.unique.email(),
            password_hash=pwd_context.hash("password123"),
            role=RoleType.CLIENT
        )
        users.append(client)
    
    db.add_all(users)
    db.commit()
    return users

def create_groups(db: Session, users, num_groups=25):
    groups = []
    chiefs = [u for u in users if u.role == RoleType.CHIEF]
    members = [u for u in users if u.role == RoleType.MEMBER]
    
    for i in range(num_groups):
        chief = chiefs[i % len(chiefs)]
        group_members = random.sample(members, random.randint(2, 5))
        
        group = Group(
            name=f"Team {fake.unique.company()}",
            specialization=random.choice(list(SpecializationType)),
            rating=round(random.uniform(3.0, 5.0), 1),
            chief_id=chief.id,
            members=group_members
        )
        groups.append(group)
    
    db.add_all(groups)
    db.commit()
    return groups

def create_reservations(db: Session, users, groups, num_reservations=200):
    reservations = []
    clients = [u for u in users if u.role == RoleType.CLIENT]
    
    start_date = datetime.now() - timedelta(days=90)
    
    for i in range(num_reservations):
        client = random.choice(clients)
        group = random.choice(groups)
        
        random_days = random.randint(0, 180)
        cleaning_date = start_date + timedelta(days=random_days)
        
        reservation_date = cleaning_date - timedelta(days=random.randint(1, 30))
        
        reservation = Reservation(
            client_id=client.id,
            cleaning_type=group.specialization,
            address=fake.street_address(),
            house_number=str(random.randint(1, 999)),
            cleaning_date=cleaning_date.date(),
            reservation_date=reservation_date,
            price=round(random.uniform(50.0, 500.0), 2),
            approved_by_client=random.choice([True, False]),
            approved_by_admin=random.choice([True, False]),
            priority=random.choice(list(PriorityType)),
            assigned_group_id=group.id
        )
        reservations.append(reservation)
    
    db.add_all(reservations)
    db.commit()
    return reservations

def main():
    print("Starting database seeding...")
    
    Base.metadata.create_all(bind=engine)
    
    create_seed_data()
    
    print("Database seeding completed!")

if __name__ == "__main__":
    main() 