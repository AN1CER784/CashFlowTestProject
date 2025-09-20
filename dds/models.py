from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class OperationStatus(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ['name']

    def __str__(self): return self.name


class OperationType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"
        ordering = ['name']

    def __str__(self): return self.name


class Category(models.Model):
    name = models.CharField(max_length=64)
    type = models.ForeignKey(OperationType, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        unique_together = ('name', 'type')
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['type__name', 'name']

    def __str__(self): return f"{self.name} ({self.type})"


class Subcategory(models.Model):
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        unique_together = ('name', 'category')
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ['category__type__name', 'category__name', 'name']

    def __str__(self): return f"{self.name} ({self.category})"


class Operation(models.Model):
    date = models.DateField(default=timezone.now)
    status = models.ForeignKey(OperationStatus, on_delete=models.PROTECT, related_name='operations')
    type = models.ForeignKey(OperationType, on_delete=models.PROTECT, related_name='operations')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='operations')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='operations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Запись ДДС"
        verbose_name_plural = "Записи ДДС"
        ordering = ['-date', '-id']

    def clean(self):
        if self.amount is None or self.amount <= Decimal('0'):
            raise ValidationError({'amount': 'Сумма должна быть положительной.'})
        if self.category and self.type and self.category.type_id != self.type_id:
            raise ValidationError({'category': 'Категория должна соответствовать выбранному типу.'})
        if self.subcategory and self.category and self.subcategory.category_id != self.category_id:
            raise ValidationError({'subcategory': 'Подкатегория должна соответствовать выбранной категории.'})

    def __str__(self):
        return f"{self.date} {self.type}/{self.category}/{self.subcategory} {self.amount}"
