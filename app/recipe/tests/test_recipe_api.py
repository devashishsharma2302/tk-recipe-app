"""
Test for recipe API methods.
"""

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

    def setUp(self):
        self.client = APIClient()

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
