from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, Group, Reservation, RoleType, SpecializationType, PriorityType
from faker import Faker
import random
from datetime import datetime, timedelta
import bcrypt
from tqdm import tqdm

fake = Faker()

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_reservations(db: Session, num_reservations=500000, batch_size=1000):
    # Get client and group IDs once at the start
    client_ids = [id[0] for id in db.query(User.id).filter(User.role == RoleType.CLIENT).all()]
    group_ids = [id[0] for id in db.query(Group.id).all()]
    
    if not client_ids:
        raise Exception("No clients available")
    if not group_ids:
        raise Exception("No groups available")
    
    print(f"Found {len(client_ids)} clients and {len(group_ids)} groups")
    print(f"Creating {num_reservations} reservations in batches of {batch_size}...")
    
    # Pre-generate common data
    street_addresses = [fake.street_address() for _ in range(1000)]
    house_numbers = [str(random.randint(1, 999)) for _ in range(100)]
    priorities = list(PriorityType)
    specializations = list(SpecializationType)
    
    total_batches = num_reservations // batch_size
    
    for batch in tqdm(range(total_batches)):
        reservations = []
        for _ in range(batch_size):
            cleaning_date = datetime.now() + timedelta(days=random.randint(1, 365))
            
            reservation = Reservation(
                client_id=random.choice(client_ids),
                cleaning_type=random.choice(specializations),
                address=random.choice(street_addresses),
                house_number=random.choice(house_numbers),
                cleaning_date=cleaning_date,
                price=round(random.uniform(50.0, 200.0), 2),
                approved_by_client=True,
                approved_by_admin=random.choice([True, False]),
                priority=random.choice(priorities),
                assigned_group_id=random.choice(group_ids)
            )
            reservations.append(reservation)
        
        db.bulk_save_objects(reservations)
        db.commit()
    
    # Handle remaining reservations
    remaining = num_reservations % batch_size
    if remaining:
        reservations = []
        for _ in range(remaining):
            cleaning_date = datetime.now() + timedelta(days=random.randint(1, 365))
            
            reservation = Reservation(
                client_id=random.choice(client_ids),
                cleaning_type=random.choice(specializations),
                address=random.choice(street_addresses),
                house_number=random.choice(house_numbers),
                cleaning_date=cleaning_date,
                price=round(random.uniform(50.0, 200.0), 2),
                approved_by_client=True,
                approved_by_admin=random.choice([True, False]),
                priority=random.choice(priorities),
                assigned_group_id=random.choice(group_ids)
            )
            reservations.append(reservation)
        
        db.bulk_save_objects(reservations)
        db.commit()
    
    return num_reservations

def main():
    print("Starting reservation creation process...")
    db = SessionLocal()
    try:
        total_created = create_reservations(db, num_reservations=500000)
        
        # Get summary statistics
        total_count = db.query(Reservation).count()
        unique_clients = db.query(Reservation.client_id).distinct().count()
        unique_groups = db.query(Reservation.assigned_group_id).distinct().count()
        
        print("\nSummary:")
        print(f"Total reservations created: {total_count}")
        print(f"Unique clients used: {unique_clients}")
        print(f"Unique groups assigned: {unique_groups}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()