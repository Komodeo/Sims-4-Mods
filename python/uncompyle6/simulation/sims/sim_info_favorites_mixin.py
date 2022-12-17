# uncompyle6 version 3.8.0
# Python bytecode 3.7.0 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\sim_info_favorites_mixin.py
# Compiled at: 2021-09-01 10:58:18
# Size of source mod 2**32: 1744 bytes
import services, sims4.resources

class SimInfoFavoriteMixin:

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._favorite_recipes = []

    def get_favorite_recipe(self, recipe_tags):
        if not self._favorite_recipes:
            return
        else:
            return recipe_tags or self._favorite_recipes[0]
        for recipe in self._favorite_recipes:
            if recipe.recipe_tags & recipe_tags:
                return recipe

    def set_favorite_recipe(self, recipe):
        if recipe not in self._favorite_recipes:
            self._favorite_recipes.append(recipe)

    def save_favorite(self, favorite_data):
        for recipe in self._favorite_recipes:
            favorite_data.recipe_ids.append(recipe.guid64)

    def load_favorite(self, favorite_data):
        recipe_manager = services.get_instance_manager(sims4.resources.Types.RECIPE)
        for recipe_id in favorite_data.recipe_ids:
            recipe = recipe_manager.get(recipe_id)
            if recipe is not None:
                self.set_favorite_recipe(recipe)