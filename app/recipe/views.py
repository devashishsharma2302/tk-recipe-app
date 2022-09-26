from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
)

from core.models import (
    Recipe,
)
from recipe import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'name',
                OpenApiTypes.STR,
                description='Filter recipes by name substring, case-insensitive',
            )]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        """Retrieve recipes with possible search by name."""
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset
