from typing import Optional, List # <--- השורה הזו הייתה חסרה!
from fastapi import APIRouter, Depends, HTTPException
from app.models import Restaurant, User
from app.services.restaurant_service import RestaurantService
from app.dependencies import get_restaurant_owner

router = APIRouter()

@router.post("/", tags=["Restaurants"])
async def create_restaurant(
    name: str, 
    location: str, 
    image_url: Optional[str] = None, # עכשיו Optional מוגדר
    current_user: User = Depends(get_restaurant_owner)
):
    """Creates a new restaurant for the authenticated owner."""
    return await RestaurantService.create_restaurant(
        name=name, 
        location=location, 
        owner_id=str(current_user.id), 
        image_url=image_url
    )

@router.get("/my-restaurants", tags=["Restaurants"], response_model=List[Restaurant])
async def get_my_restaurants(current_user: User = Depends(get_restaurant_owner)):
    """Returns all restaurants belonging to the owner."""
    return await RestaurantService.get_owner_restaurants(str(current_user.id))

@router.patch("/{restaurant_id}/menus/{menu_id}/status", tags=["Restaurants"])
async def set_menu_status(
    restaurant_id: str,
    menu_id: str,
    active: bool,
    current_user: User = Depends(get_restaurant_owner)
):
    """Activates or deactivates a menu for a specific restaurant."""
    updated_menu = await RestaurantService.toggle_menu_status(
        menu_id=menu_id, 
        restaurant_id=restaurant_id, 
        owner_id=str(current_user.id), 
        active=active
    )
    if not updated_menu:
        raise HTTPException(status_code=404, detail="Menu or Restaurant not found/not yours")
    return updated_menu