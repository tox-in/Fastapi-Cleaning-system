from fastapi import FastAPI
from app.routes import users, groups, reservations
from app.database import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(groups.router)
app.include_router(reservations.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Cleaning System API",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }