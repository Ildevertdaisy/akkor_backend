
import asyncio
from decouple import config
from typing import Optional
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from motor.motor_asyncio import AsyncIOMotorClient

from routers.users import router as users_router
from routers.hotels import router as hotels_router
from routers.bookings import router as bookings_router

from models import HotelDB

DB_URL = config('DB_URL', cast=str)
DB_NAME = config('DB_NAME', cast=str)


# define origins
origins = [
    "http://localhost",
    "http://localhost:3000",
]

# instantiate the app
app = FastAPI()

# add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(DB_URL)
    app.mongodb = app.mongodb_client[DB_NAME]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(hotels_router, prefix="/hotels", tags=["hotels"])
app.include_router(bookings_router, prefix="/bookings", tags=["bookings"])


@app.get("/")
async def home():
    return {"message": "Welcome to the AKKOR Backend API!"}

@app.get("/test")
async def home():
    return {"message": "test"}

@app.get("/search", response_description="Search hotels by name")
async def hotels_by_name(request: Request, name: str = Query(..., min_length=1)):
    print(name) 
    hotels = request.app.mongodb["hotels"].find({"name": {"$regex": f".*{name}.*", "$options": "i"}})
    results = [HotelDB(**raw_hotel) async for raw_hotel in hotels]
    print(results)
    asyncio.sleep(50)
    return results
   
  