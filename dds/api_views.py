from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    OperationStatus, OperationType, Category, Subcategory, Operation
)
from .serializers import (
    OperationStatusSerializer, OperationTypeSerializer,
    CategorySerializer, SubcategorySerializer, OperationSerializer
)
from .filters import OperationFilter


class OperationStatusViewSet(viewsets.ModelViewSet):
    """
    CRUD по справочнику статусов.
    GET /api/statuses/ — список (поиск: ?search=...)
    POST /api/statuses/ — создание
    GET /api/statuses/{id}/ — деталь
    PATCH/PUT /api/statuses/{id}/ — обновление
    DELETE /api/statuses/{id}/ — удаление
    """
    queryset = OperationStatus.objects.all()
    serializer_class = OperationStatusSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class OperationTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD по типам операций.
    Поддерживает поиск по name (?search=...).
    """
    queryset = OperationType.objects.all()
    serializer_class = OperationTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD по категориям.
    Фильтрация по типу: ?type={type_id}
    Поиск по name: ?search=...
    """
    # select_related('type') — чтобы не делать отдельный запрос за типом категории
    queryset = Category.objects.select_related('type').all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type']  # фильтр по ID типа
    search_fields = ['name']


class SubcategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD по подкатегориям.
    Фильтрация по категории: ?category={category_id}
    Поиск по name: ?search=...
    """
    queryset = Subcategory.objects.select_related('category', 'category__type').all()
    serializer_class = SubcategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']  # фильтр по ID категории
    search_fields = ['name']


class OperationViewSet(viewsets.ModelViewSet):
    """
    CRUD по записям ДДС.
    - Фильтры (OperationFilter): ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD&
                                status={id}&type={id}&category={id}&subcategory={id}
    - Поиск по комментарию: ?search=текст
    - Пагинация — стандарт DRF (PAGE_SIZE в settings).
    """
    queryset = (
        Operation.objects
        .select_related('status', 'type', 'category', 'subcategory')  # чтобы не дергать БД на каждом объекте
        .all()
    )
    serializer_class = OperationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = OperationFilter
    search_fields = ['comment']