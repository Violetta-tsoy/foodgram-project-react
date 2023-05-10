from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()

router.register(
    'recipes',
    views.RecipeViewSet,
    basename='recipes',
)
router.register(
    'tags',
    views.TagViewSet,
    basename='tags',
)
router.register(
    'ingredients',
    views.IngredientViewSet,
)
router.register(
    'users',
    views.CustomUserViewSet,
    basename='users',
)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
