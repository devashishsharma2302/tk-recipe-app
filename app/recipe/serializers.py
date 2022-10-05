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

    def update(self, instance, validated_data):
        """Update recipe."""
        ingredients = validated_data.pop('ingredients', None)

        if ingredients is not None:
            with transaction.atomic():
                # Delete old ingredient objects
                instance.ingredients.all().delete()

                # Create new ingredient objects
                Ingredient.objects.bulk_create(
                    [Ingredient(name=ingredient.get('name'), recipe=instance) for ingredient in
                     ingredients])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
