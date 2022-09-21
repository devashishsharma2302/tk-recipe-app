"""
Test for models.
"""

from django.test import TestCase

from core import models


def create_recipe(name="Sample Recipe Name", description="Sample Description."):
    """Create and return a new Recipe object."""
    return models.Recipe.objects.create(name=name,
                                        description=description)


def create_ingredient(recipe, name="Sample Ingredient Name"):
    """Create and return a new ingredient object."""
    return models.Ingredient.objects.create(name=name,
                                            recipe=recipe)


class ModelTests(TestCase):
    """Test models."""

    def test_create_recipe(self):
        """Test that creating a Recipe object is successful."""
        sample_name = "Pizza"
        sample_description = "Some description about Pizza."
        recipe = create_recipe(name=sample_name, description=sample_description)

        # Test object
        self.assertEqual(recipe.name, sample_name)
        self.assertEqual(recipe.description, sample_description)

        # Check stringification
        self.assertEqual(str(recipe), sample_name)

    def test_create_ingredient(self):
        """Test that creating an Ingredient object is successful."""
        recipe = create_recipe()
        sample_ingredient_name = "Cheese"
        ingredient = models.Ingredient.objects.create(name=sample_ingredient_name,
                                                      recipe=recipe)

        # Test object
        self.assertEqual(ingredient.name, sample_ingredient_name)
        self.assertEqual(ingredient.recipe, recipe)

        # Check stringification
        self.assertEqual(str(ingredient), sample_ingredient_name)

    def test_ingredient_cascade_delete(self):
        """Test that ingredient objects are deleted if the linked recipe is deleted."""

        # Creating recipe objects
        sample_recipe_1 = create_recipe(name="Recipe 1")
        sample_recipe_2 = create_recipe(name="Recipe 2")

        # Creating ingredients
        create_ingredient(recipe=sample_recipe_1)
        create_ingredient(recipe=sample_recipe_1)
        create_ingredient(recipe=sample_recipe_2)

        # Test Ingredients are created
        self.assertEqual(models.Ingredient.objects.all().count(), 3)
        self.assertEqual(models.Ingredient.objects.filter(recipe=sample_recipe_1).count(), 2)

        # Delete Recipe 1
        models.Recipe.objects.filter(id=sample_recipe_1.id).delete()

        # Test recipe is deleted
        self.assertEqual(models.Recipe.objects.filter(id=sample_recipe_1.id).count(), 0)

        # Test related ingredients are deleted
        self.assertEqual(models.Ingredient.objects.filter(recipe=sample_recipe_1).count(), 0)

        # Test unrelated ingredients are not deleted
        self.assertEqual(models.Ingredient.objects.filter(recipe=sample_recipe_2).count(), 1)
