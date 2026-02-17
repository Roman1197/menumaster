from fastapi import APIRouter, Depends, HTTPException, status
from app.models import Menu, MenuItem, User
from app.services.menu_service import MenuService
from app.dependencies import get_verified_user

router = APIRouter()

@router.post("/create", tags=["Menus"], status_code=status.HTTP_201_CREATED)
async def create_menu(
    title: str, 
    current_user: User = Depends(get_verified_user)
):
    """
    Creates a new menu for the authenticated and verified user.
    The owner_id is derived directly from the JWT.
    """
    menu = await MenuService.create_menu(title, str(current_user.id))
    return {"status": "success", "data": menu}

@router.post("/{menu_id}/categories", tags=["Menus"])
async def add_category(
    menu_id: str, 
    category_name: str,
    current_user: User = Depends(get_verified_user)
):
    """
    Adds a new category to a specific menu.
    Ownership is verified within the MenuService using current_user.id.
    """
    # Passing current_user.id to ensure only the owner can modify this menu
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
    current_user: User = Depends(get_verified_user)
):
    """
    Adds a dish to a specific category.
    Ownership is verified within the MenuService using current_user.id.
    """
    # Passing current_user.id to ensure only the owner can modify this menu
    menu = await MenuService.add_item_to_category(
        menu_id=menu_id, 
        category_name=category_name, 
        item=item, 
        user_id=str(current_user.id)
    )
    return menu