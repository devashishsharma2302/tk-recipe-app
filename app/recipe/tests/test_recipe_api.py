"""
Test for recipe API methods.
"""
import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Recipe, Ingredient)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(name="Sample Recipe", description="Sample Recipe Description."):
    """Create and return a sample recipe object."""
    return Recipe.objects.create(name=name, description=description)


def create_ingredient(recipe, name="Sample Ingredient Name"):
    """Create and return a new ingredient object."""
    return Ingredient.objects.create(name=name,
                                     recipe=recipe)


class PublicRecipeApiTests(TestCase):
    """Unauthenticated Recipe API tests"""

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

    def test_list_recipes(self):
        """Test retrieving a list of recipes."""

        # Creating recipes
        recipe_1 = create_recipe(name="Recipe 1", )
        recipe_2 = create_recipe(name="Recipe 2")

        # Creating Ingredients
        create_ingredient(recipe=recipe_1, name="Cheese")
        create_ingredient(recipe=recipe_2)
        create_ingredient(recipe=recipe_2)

        res = self.client.get(RECIPES_URL)

        # Check response structure
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0].get('name'), "Recipe 1")
        self.assertEqual(res.data[1].get('name'), "Recipe 2")
        self.assertEqual(res.data[0].get('description'), "Sample Recipe Description.")
        self.assertEqual(len(res.data[0].get('ingredients')), 1)
        self.assertEqual(len(res.data[1].get('ingredients')), 2)
        self.assertEqual(res.data[0].get('ingredients')[0].get('name'), "Cheese")

    def test_list_recipes_search_by_name(self):
        """Test retrieving a list of recipes filtered successfully by name substring."""

        # Creating recipes
        recipe_1 = create_recipe(name="Pizza", )
        recipe_2 = create_recipe(name="Pasta")

        # Test search for Pi
        res = self.client.get(RECIPES_URL, {'name': 'Pi'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get('name'), "Pizza")
        self.assertEqual(res.data[0].get('id'), recipe_1.id)

        # Test search for Pi, case-insensitive
        res = self.client.get(RECIPES_URL, {'name': 'pi'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0].get('name'), "Pizza")
        self.assertEqual(res.data[0].get('id'), recipe_1.id)

        # Test search for P
        res = self.client.get(RECIPES_URL, {'name': 'P'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        # Test search not found
        res = self.client.get(RECIPES_URL, {'name': 'Lasagna'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_recipe_details(self):
        """Test retrieving detailed view of a recipe."""

        # Creating recipe
        recipe_1 = create_recipe(name="Recipe 1", )

        # Creating Ingredients
        create_ingredient(recipe=recipe_1, name="Cheese")

        res = self.client.get(detail_url(recipe_1.id))

        # Check response structure
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data.get('name'), "Recipe 1")
        self.assertEqual(res.data.get('description'), "Sample Recipe Description.")
        self.assertEqual(len(res.data.get('ingredients')), 1)
        self.assertEqual(res.data.get('ingredients')[0].get('name'), "Cheese")

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'name': 'New Recipe',
            'description': "Some description",
            'ingredients': [{"name": "dough"}, {"name": "cheese"}, {"name": "tomato"}]
        }

        res = self.client.post(RECIPES_URL, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])

        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        self.assertEqual(recipe.ingredients.count(), 3)
        self.assertEqual(recipe.ingredients.first().name, "dough")
        self.assertEqual(recipe.ingredients.last().name, "tomato")

    def test_patch_recipe(self):
        """Test update of a recipe fields."""
        # Creating recipe
        recipe = create_recipe(name="Recipe Name", description="Recipe Description.")

        # Creating Ingredients
        ingredient_1 = create_ingredient(recipe=recipe, name="Cheese")
        ingredient_2 = create_ingredient(recipe=recipe, name="Tomato")

        payload = {'name': 'New recipe name', 'ingredients': [{'name': "Yeast"}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, json.dumps(payload), content_type='application/json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        # Test that original description field is unchanged
        self.assertEqual(recipe.description, "Recipe Description.")

        # Test that the recipe has been updated in db and new ingredient is created.
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertEqual(recipe.ingredients.first().name, "Yeast")

        # Test that old ingredient objects are deleted
        self.assertEqual(Ingredient.objects.filter(recipe=recipe).count(), 1)
        self.assertFalse(Ingredient.objects.filter(id=ingredient_1.id).exists())
        self.assertFalse(Ingredient.objects.filter(id=ingredient_2.id).exists())

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe()

        ingredient_1 = create_ingredient(recipe=recipe, name="Cheese")

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())
        self.assertFalse(Ingredient.objects.filter(id=ingredient_1.id).exists())
