from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.models import Menu, MenuItem, User
from app.services.menu_service import MenuService
from app.dependencies import get_verified_user, get_restaurant_owner
from app.logger import logger # ייבוא הלוגר המרכזי

router = APIRouter()

# --- PUBLIC ENDPOINTS (Customers & Owners) ---

@router.get("/", tags=["Public - Menus"])
async def get_all_menus(response: Response):
    """
    Returns all active menus for customers to browse.
    Returns 204 if no menus are found.
    """
    logger.info("Fetching all active menus")
    try:
        menus = await Menu.find(Menu.is_active == True).to_list()
        if not menus:
            logger.info("No active menus found in database")
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        return menus
    except Exception as e:
        logger.error(f"Error fetching menus: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{menu_id}", tags=["Public - Menus"])
async def get_single_menu(menu_id: str):
    """Retrieve a specific menu by ID."""
    logger.info(f"Fetching menu with ID: {menu_id}")
    menu = await Menu.get(menu_id)
    if not menu:
        logger.warning(f"Menu {menu_id} not found")
        raise HTTPException(status_code=404, detail="Menu not found")
    return menu

# --- PROTECTED ENDPOINTS (Restaurant Owners Only) ---

@router.post("/create", tags=["Owner - Menus"], status_code=status.HTTP_201_CREATED)
async def create_menu(
    title: str, 
    restaurant_id: str, 
    current_user: User = Depends(get_verified_user)
):
    """Creates a new menu for a specific restaurant."""
    logger.info(f"User {current_user.email} is creating menu '{title}' for restaurant {restaurant_id}")
    try:
        menu = await MenuService.create_menu(
            title=title, 
            owner_id=str(current_user.id),
            restaurant_id=restaurant_id
        )
        logger.info(f"Menu created successfully with ID: {menu.id}")
        return menu
    except Exception as e:
        logger.error(f"Failed to create menu: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not create menu. Check if restaurant_id is valid.")

@router.get("/my-menus", tags=["Owner - Menus"], response_model=List[Menu])
async def get_my_menus(response: Response, current_user: User = Depends(get_restaurant_owner)):
    """Returns all menus belonging to the authenticated owner."""
    logger.info(f"Fetching menus for owner: {current_user.email}")
    try:
        menus = await MenuService.get_owner_menus(str(current_user.id))
        if not menus:
            logger.info(f"Owner {current_user.email} has no menus")
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        return menus
    except Exception as e:
        logger.error(f"Error fetching owner menus: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{menu_id}/categories", tags=["Owner - Menus"])
async def add_category(
    menu_id: str, 
    category_name: str,
    current_user: User = Depends(get_restaurant_owner)
):
    """Adds a new category to a specific menu."""
    logger.info(f"Adding category '{category_name}' to menu {menu_id}")
    menu = await MenuService.add_category(
        menu_id=menu_id, 
        category_name=category_name, 
        user_id=str(current_user.id)
    )
    if not menu:
        logger.error(f"Failed to add category to menu {menu_id}")
        raise HTTPException(status_code=400, detail="Failed to add category. Check ownership.")
    return menu

@router.post("/{menu_id}/items", tags=["Owner - Menus"])
async def add_dish(
    menu_id: str, 
    category_name: str, 
    item: MenuItem,
    current_user: User = Depends(get_restaurant_owner)
):
    """Adds a dish to a category in a specific menu."""
    logger.info(f"Adding dish '{item.name}' to category '{category_name}' in menu {menu_id}")
    menu = await MenuService.add_item_to_category(
        menu_id=menu_id, 
        category_name=category_name, 
        item=item, 
        user_id=str(current_user.id)
    )
    return menu

@router.delete("/{menu_id}", tags=["Owner - Menus"])
async def delete_menu(
    menu_id: str, 
    current_user: User = Depends(get_restaurant_owner)
):
    """Deletes a specific menu."""
    logger.info(f"Attempting to delete menu {menu_id} by user {current_user.email}")
    success = await MenuService.delete_menu(menu_id, str(current_user.id))
    if success:
        logger.info(f"Menu {menu_id} deleted successfully")
        return {"status": "success", "message": "Menu deleted successfully"}
    
    logger.warning(f"Delete failed for menu {menu_id} - not found or unauthorized")
    raise HTTPException(status_code=404, detail="Menu not found or you don't have permission")