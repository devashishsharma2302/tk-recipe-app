"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import (
    Recipe,
    Ingredient
)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'description', 'ingredients',
        ]
        read_only_fields = ['id']
