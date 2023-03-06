

from typing import List, Optional

from fastapi import APIRouter, Request, Body, status, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from models import BookingBase, BookingDB

from authentication import AuthHandler

router = APIRouter()


#instantiate the Auth Handler
auth_handler = AuthHandler()


@router.post("/", response_description="Add new booking")
async def create_booking(request: Request, booking: BookingBase = Body(...), userId=Depends(auth_handler.auth_wrapper)):
    booking = jsonable_encoder(booking)
    booking["customer"] = userId
    new_booking = await request.app.mongodb["bookings"].insert_one(booking)
    created_booking = await request.app.mongodb["bookings"].find_one(
        {"_id": new_booking.inserted_id}
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_booking)


@router.get("/", response_description="List all bookings")
async def list_all_cars(request: Request, userId=Depends(auth_handler.auth_wrapper)):
    bookings = request.app.mongodb["bookings"].find({"customer": userId})
    results = [BookingDB(**raw_booking) async for raw_booking in bookings]
    return results


@router.get("/{id}", response_description="Get a single booking")
async def show_booking(id: str, request: Request):
    if (booking := await request.app.mongodb["bookings"].find_one({"_id": id})) is not None:
        return BookingDB(**booking)
    return HTTPException(status_code=404, detail=f"Booking with {id} not found.")


@router.delete("/{id}", response_description="Delete Booking")
async def delete_boonking(id: str, request: Request, userId=Depends(auth_handler.auth_wrapper)):
    findBooking = await request.app.mongodb["bookings"].find_one({"_id": id})

    if findBooking["customer"] != userId:
        raise HTTPException(status_code=401, detail="Only the reliable customer can delete the car")
    
    delete_result = await request.app.mongodb["bookings"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    
    raise HTTPException(status_code=404, detail=f"Booking with {id} not found.")




