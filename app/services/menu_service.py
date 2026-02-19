# app/services/menu_service.py
from app.models import Menu, MenuCategory, MenuItem
from beanie import PydanticObjectId
from typing import List, Optional

class MenuService:
    @classmethod
    async def create_menu(cls, title: str, owner_id: str) -> Menu:
        """Creates a new empty menu for a specific user"""
        new_menu = Menu(title=title, owner_id=owner_id)
        await new_menu.insert()
        return new_menu

    @classmethod
    async def get_user_menus(cls, owner_id: str) -> List[Menu]:
        """Retrieves all menus belonging to a specific user"""
        return await Menu.find(Menu.owner_id == owner_id).to_list()

    @classmethod
    async def add_category(cls, menu_id: str, category_name: str, user_id: str):
        """
        Adds a category ONLY if the user_id matches the menu owner_id.
        """
        menu = await Menu.get(menu_id)
        
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")
            
        # Ownership Check: Compare the requester's ID with the menu owner's ID
        if menu.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this menu"
            )

        menu.categories.append(MenuCategory(name=category_name))
        await menu.save()
        return menu

    @classmethod
    async def add_item_to_category(cls, menu_id: str, category_name: str, item: MenuItem, user_id: str):
        """
        Adds an item ONLY if the user_id matches the menu owner_id.
        """
        menu = await Menu.get(menu_id)
        
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")

        # Ownership Check
        if menu.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this menu"
            )
            
        for category in menu.categories:
            if category.name == category_name:
                category.items.append(item)
                await menu.save()
                return menu
                
        raise HTTPException(status_code=404, detail="Category not found")
    @classmethod
    async def get_owner_menus(cls, owner_id: str) -> List[Menu]:
        """
        Retrieves all menus created by a specific owner.
        Useful for the owner's management dashboard.
        """
        # We search the 'menus' collection where owner_id matches the user's ID
        return await Menu.find(Menu.owner_id == owner_id).to_list()

    @classmethod
    async def delete_menu(cls, menu_id: str, user_id: str) -> bool:
        """
        Permanently deletes a menu only if the requester is the owner.
        """
        menu = await Menu.get(menu_id)
        
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")
            
        # Security Check: Ensure the person deleting is the owner
        if menu.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to delete this menu"
            )
            
        await menu.delete()
        return True