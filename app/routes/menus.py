from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Menu, MenuItem, User
from app.services.menu_service import MenuService
from app.dependencies import get_verified_user, get_restaurant_owner

router = APIRouter()

# --- PUBLIC ENDPOINTS (Customers & Owners) ---

@router.get("/", tags=["Menus"], response_model=List[Menu])
async def get_all_menus():
    """
    Returns all active menus for customers to browse.
    No authentication required for browsing.
    """
    return await Menu.find(Menu.is_active == True).to_list()

@router.get("/{menu_id}", tags=["Menus"])
async def get_single_menu(menu_id: str):
    """
    Retrieve a specific menu by ID.
    Used by customers to view restaurant details and prices.
    """
    menu = await Menu.get(menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

# --- PROTECTED ENDPOINTS (Restaurant Owners Only) ---

@router.post("/create", tags=["Menus"], status_code=status.HTTP_201_CREATED)
async def create_menu(
    title: str, 
    current_user: User = Depends(get_restaurant_owner) # Restricted to Owners
):
    """
    Creates a new menu. 
    Only users with the 'owner' role can create menus.
    """
    menu = await MenuService.create_menu(title, str(current_user.id))
    return {"status": "success", "data": menu}

@router.post("/{menu_id}/categories", tags=["Menus"])
async def add_category(
    menu_id: str, 
    category_name: str,
    current_user: User = Depends(get_restaurant_owner) # Restricted to Owners
):
    """
    Adds a new category. 
    Verified for 'owner' role AND verified for menu ownership in Service.
    """
    menu = await MenuService.add_category(
        menu_id=menu_id, 
        category_name=category_name, 
        user_id=str(current_user.id)
    )
    return menu

@router.post("/{menu_id}/items", tags=["Menus"])
async def add_dish(
    menu_id: str, 
    category_name: str, 
    item: MenuItem,
    current_user: User = Depends(get_restaurant_owner) # Restricted to Owners
):
    """
    Adds a dish to a category. 
    Only the restaurant owner who owns this specific menu can add items.
    """
    menu = await MenuService.add_item_to_category(
        menu_id=menu_id, 
        category_name=category_name, 
        item=item, 
        user_id=str(current_user.id)
    )
    return menu
@router.get("/my-menus", tags=["Menus"], response_model=List[Menu])
async def get_my_menus(current_user: User = Depends(get_restaurant_owner)):
    """
    Returns a list of all menus belonging to the authenticated owner.
    """
    # current_user.id is automatically provided by the dependency
    return await MenuService.get_owner_menus(str(current_user.id))

# app/routes/menus.py

@router.delete("/{menu_id}", tags=["Menus"])
async def delete_menu(
    menu_id: str, 
    current_user: User = Depends(get_restaurant_owner)
):
    """
    Deletes a specific menu. 
    Requires 'owner' role and verified ownership of the specific menu.
    """
    success = await MenuService.delete_menu(menu_id, str(current_user.id))
    if success:
        return {"status": "success", "message": "Menu deleted successfully"}