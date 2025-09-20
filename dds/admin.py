from django.contrib import admin

from .models import OperationStatus, OperationType, Category, Subcategory, Operation


@admin.register(OperationStatus)
class OperationStatusAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(OperationType)
class OperationTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']
    list_filter = ['type']
    search_fields = ['name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'get_type']
    list_filter = ['category__type', 'category']
    search_fields = ['name']

    def get_type(self, obj): return obj.category.type

    get_type.short_description = 'Тип'


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ['date', 'status', 'type', 'category', 'subcategory', 'amount']
    list_filter = ['date', 'status', 'type', 'category', 'subcategory']
    search_fields = ['comment']
