from typing import Optional, List 
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.models import Restaurant, User
from app.services.restaurant_service import RestaurantService
from app.dependencies import get_restaurant_owner


router = APIRouter()

# --- Public Routes (נתיבים ציבוריים - ללא צורך בטוקן) ---

@router.get("/", tags=["Public - Restaurants"])
async def get_all_restaurants(response: Response):
    """
    מאחזר את כל המסעדות. אם אין מסעדות, מחזיר 204 No Content.
    """
    try:
        restaurants = await RestaurantService.get_all_restaurants()
        
        if not restaurants:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None # בסטטוס 204 לא מחזירים Body
            
        return restaurants
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable"
        )

# --- Protected Routes ---

@router.get("/my-restaurants", tags=["Owner - Restaurants"])
async def get_my_restaurants(
    response: Response, 
    current_user: User = Depends(get_restaurant_owner)
):
    """
    מאחזר מסעדות של בעלים. אם אין, מחזיר 204.
    """
    try:
        restaurants = await RestaurantService.get_owner_restaurants(str(current_user.id))
        
        if not restaurants:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
            
        return restaurants
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

        
@router.post("/", tags=["Owner - Restaurants"])
async def create_restaurant(
    name: str, 
    location: str, 
    image_url: Optional[str] = None,
    current_user: User = Depends(get_restaurant_owner)
):
    """Creates a new restaurant for the authenticated owner."""
    return await RestaurantService.create_restaurant(
        name=name, 
        location=location, 
        owner_id=str(current_user.id), 
        image_url=image_url
    )



@router.patch("/{restaurant_id}/menus/{menu_id}/status", tags=["Owner - Restaurants"])
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