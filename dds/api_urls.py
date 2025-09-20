from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .api_views import OperationStatusViewSet, OperationTypeViewSet, CategoryViewSet, SubcategoryViewSet, OperationViewSet

router = DefaultRouter()
router.register('statuses', OperationStatusViewSet)
router.register('types', OperationTypeViewSet)
router.register('categories', CategoryViewSet)
router.register('subcategories', SubcategoryViewSet)
router.register('operations', OperationViewSet)

urlpatterns = [ path('', include(router.urls)), ]
