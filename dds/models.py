from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class OperationStatus(models.Model):
    """
    Статус/контекст операции.
    Примеры: «Бизнес», «Личное», «Налог».
    """
    # Уникальное имя статуса, используется в UI и отчетах
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ['name']  # удобная сортировка по алфавиту в админке/списках

    def __str__(self):
        return self.name


class OperationType(models.Model):
    """
    Тип операции: направление движения денег.
    Примеры: «Пополнение» (приход), «Списание» (расход).
    """
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = "Тип операции"
        verbose_name_plural = "Типы операций"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Категория затрат/доходов, привязанная к конкретному типу операции.
    Например:
      Тип «Пополнение»: категория «Инфраструктура»
      Тип «Списание»:   категория «Маркетинг»
    """
    name = models.CharField(max_length=64)
    # Связь с типом определяет валидную область применения категории
    type = models.ForeignKey(OperationType, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        # Запрещаем дублировать одинаковые названия в рамках одного типа
        unique_together = ('name', 'type')
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        # Сортировка сначала по типу, затем по названию — удобнее в выпадающих списках
        ordering = ['type__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.type})"


class Subcategory(models.Model):
    """
    Подкатегория, принадлежит конкретной категории.
    Например: категория «Маркетинг» → подкатегории «Avito», «Farpost».
    """
    name = models.CharField(max_length=64)
    # При удалении категории — удаляются и ее подкатегории (CASCADE),
    # что логично для иерархического справочника
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    class Meta:
        unique_together = ('name', 'category')
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"
        ordering = ['category__type__name', 'category__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"


class Operation(models.Model):
    """
    Основная сущность ДДС — учетная запись.
    Обязательные связи: статус, тип, категория, подкатегория.
    """
    # Дата по умолчанию — сегодня; значение можно поменять в UI
    date = models.DateField(default=timezone.now)

    # Связи на словари.
    # PROTECT — нельзя удалить значение из справочника, если есть записи, которые на него ссылаются.
    status = models.ForeignKey(OperationStatus, on_delete=models.PROTECT, related_name='operations')
    type = models.ForeignKey(OperationType, on_delete=models.PROTECT, related_name='operations')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='operations')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='operations')

    # Денежная сумма: 10 целых + 2 знака после запятой (в сумме max_digits=12)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Необязательное текстовое поле
    comment = models.TextField(blank=True)

    # Технические поля аудита
    created_at = models.DateTimeField(auto_now_add=True)  # устанавливается при создании
    updated_at = models.DateTimeField(auto_now=True)      # обновляется при каждом сохранении

    class Meta:
        verbose_name = "Запись ДДС"
        verbose_name_plural = "Записи ДДС"
        # Сначала свежие по дате, внутри — по убыванию id
        ordering = ['-date', '-id']

    def clean(self) -> None:
        """
        Централизованная валидация бизнес-правил.
        Метод вызывается:
          - вручную (в DRF сериализаторе — через full_clean() на временном объекте),
          - а также может вызываться вручную перед save() в иной логике.
        """
        # 1) Сумма должна быть положительной
        if self.amount is None or self.amount <= Decimal('0'):
            raise ValidationError({'amount': 'Сумма должна быть положительной.'})

        # 2) Категория должна относиться к выбранному типу
        if self.category and self.type and self.category.type_id != self.type_id:
            raise ValidationError({'category': 'Категория должна соответствовать выбранному типу.'})

        # 3) Подкатегория должна относиться к выбранной категории
        if self.subcategory and self.category and self.subcategory.category_id != self.category_id:
            raise ValidationError({'subcategory': 'Подкатегория должна соответствовать выбранной категории.'})

    def __str__(self):
        return f"{self.date} {self.type}/{self.category}/{self.subcategory} {self.amount}"
