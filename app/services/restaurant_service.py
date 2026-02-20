# app/services/restaurant_service.py
from app.models import Restaurant, Menu
from typing import List

class RestaurantService:
    @classmethod
    async def create_restaurant(cls, name: str, location: str, owner_id: str, image_url: str = None):
        restaurant = Restaurant(
            name=name,
            location=location,
            owner_id=owner_id,
            image_url=image_url
        )
        await restaurant.insert()
        return restaurant

    @classmethod
    async def get_owner_restaurants(cls, owner_id: str) -> List[Restaurant]:
        return await Restaurant.find(Restaurant.owner_id == owner_id).to_list()

    @classmethod
    async def toggle_menu_status(cls, menu_id: str, restaurant_id: str, owner_id: str, active: bool):
        menu = await Menu.get(menu_id)
        if menu and menu.restaurant_id == restaurant_id and menu.owner_id == owner_id:
            menu.is_active = active
            await menu.save()
            return menu
        return None