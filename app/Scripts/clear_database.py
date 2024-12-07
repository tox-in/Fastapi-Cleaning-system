from app.database import SessionLocal, engine, Base
from app.models import User, Group, Reservation

def clear_database():
    print("Clearing database...")
    db = SessionLocal()
    try:
        db.query(Reservation).delete()
        db.query(Group).delete()
        db.query(User).delete()
        db.commit()
        print("Database cleared successfully!")
    except Exception as e:
        print(f"Error clearing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_database() 