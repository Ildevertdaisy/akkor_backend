

from typing import List, Optional

from fastapi import APIRouter, Request, Body, status, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from models import HotelBase, HotelDB, HotelUpdate

from authentication import AuthHandler

router = APIRouter()


#instantiate the Auth Handler
auth_handler = AuthHandler()

@router.post("/", response_description="Add new hotel")
async def create_hotel(request: Request, hotel: HotelBase = Body(...), userId=Depends(auth_handler.auth_wrapper)):
    hotel = jsonable_encoder(hotel)
    # check if the user try to creating a hotel is an admin:

    user = await request.app.mongodb["users"].find_one({"_id": userId})

    if user["role"] != "ADMIN":
        raise HTTPException(status_code=401, detail="Only the owner or an admin can create an hotel.")

    hotel["owner"] = userId
    new_hotel = await request.app.mongodb["hotels"].insert_one(hotel)
    created_hotel = await request.app.mongodb["hotels"].find_one(
        {"_id": new_hotel.inserted_id}
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_hotel)


@router.get("/{id}", response_description="Get a single hotel")
async def show_hotel(id: str, request: Request):
    if (hotel := await request.app.mongodb["hotels"].find_one({"_id": id})) is not None:
        return HotelDB(**hotel)
    return HTTPException(status_code=404, detail=f"Hotel with {id} not found.")


@router.patch("/{id}", response_description="Update hotel")
async def update_hotel(
    id : str,
    request: Request,
    hotel: HotelUpdate = Body(...),
    userId=Depends(auth_handler.auth_wrapper)
):
    
    user = await request.app.mongodb["users"].find_one({"_id": userId})
    findHotel = await request.app.mongodb["hotels"].find_one({"_id": id})

    if(findHotel["owner"] != userId) and user["role"] != "ADMIN":
        raise HTTPException(status_code=401, detail="Only the owner or an admin can update the hotel.")
    await request.app.mongodb["hotels"].update_one(
        {"_id": id}, {"$set": hotel.dict(exclude_unset=True)}
    )

    if (hotel := await request.app.mongodb["hotels"].find_one({"_id": id})) is not None:
        return HotelDB(**hotel)
    raise HTTPException(status_code=404, detail=f"Hotel with {id} not found")


@router.delete("/{id}", response_description="Delete Hotel")
async def delete_hotel(id: str, request: Request, userId=Depends(auth_handler.auth_wrapper)):
    findHotel = await request.app.mongodb["hotels"].find_one({"_id": id})

    if findHotel["owner"] != userId:
        raise HTTPException(status_code=401, detail="Only the owner can delete the car")
    
    delete_result = await request.app.mongodb["hotels"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
    
    raise HTTPException(status_code=404, detail=f"Hotel with {id} not found.")




