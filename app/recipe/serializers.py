"""
Serializers for recipe APIs
"""

from django.db import transaction
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

    def create(self, validated_data):
        """Create a recipe."""
        ingredients = validated_data.pop('ingredients', [])
        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)

            # Create ingredient objects
            Ingredient.objects.bulk_create([Ingredient(name=ingredient.get('name'), recipe=recipe) for ingredient in
                                            ingredients])
        return recipe
