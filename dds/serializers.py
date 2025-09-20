from rest_framework import serializers
from .models import OperationStatus, OperationType, Category, Subcategory, Operation


class OperationStatusSerializer(serializers.ModelSerializer):
    """Сериализатор статуса/контекста операции (id, name)."""
    class Meta:
        model = OperationStatus
        fields = ['id', 'name']


class OperationTypeSerializer(serializers.ModelSerializer):
    """Сериализатор типа операции (id, name)."""
    class Meta:
        model = OperationType
        fields = ['id', 'name']


class CategorySerializer(serializers.ModelSerializer):
    """
    Категория: на чтение — вложенный type,
    на запись — отдельное поле type_id (write_only) для связи по первичному ключу.
    """
    # В ответе отдаем вложенный объект
    type = OperationTypeSerializer(read_only=True)
    # В запросе ожидаем id типа
    type_id = serializers.PrimaryKeyRelatedField(
        source='type',
        queryset=OperationType.objects.all(),
        write_only=True
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'type_id']


class SubcategorySerializer(serializers.ModelSerializer):
    """
    Подкатегория: аналогичный прием с category/category_id.
    """
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True
    )

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category', 'category_id']


class OperationSerializer(serializers.ModelSerializer):
    """
    Запись ДДС.
    Read: вложенные словари (status/type/category/subcategory).
    Write: *_id поля с ссылками по PK.
    """
    status = OperationStatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        source='status', queryset=OperationStatus.objects.all(), write_only=True
    )

    type = OperationTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        source='type', queryset=OperationType.objects.all(), write_only=True
    )

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=Category.objects.all(), write_only=True
    )

    subcategory = SubcategorySerializer(read_only=True)
    subcategory_id = serializers.PrimaryKeyRelatedField(
        source='subcategory', queryset=Subcategory.objects.all(), write_only=True
    )

    class Meta:
        model = Operation
        fields = [
            'id', 'date',
            'status', 'status_id',
            'type', 'type_id',
            'category', 'category_id',
            'subcategory', 'subcategory_id',
            'amount', 'comment',
            'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        """
        Выполняем бизнес-валидацию модели через full_clean().
        Используем временный объект (tmp), чтобы учесть:
         - создание (нет instance) и
         - частичное обновление (PATCH) — берем недостающие поля из self.instance.
        Это гарантирует единое место проверки правил (Operation.clean()).
        """
        status = attrs.get('status', getattr(self.instance, 'status', None))
        op_type = attrs.get('type', getattr(self.instance, 'type', None))
        category = attrs.get('category', getattr(self.instance, 'category', None))
        subcategory = attrs.get('subcategory', getattr(self.instance, 'subcategory', None))
        amount = attrs.get('amount', getattr(self.instance, 'amount', None))
        date = attrs.get('date', getattr(self.instance, 'date', None))
        comment = attrs.get('comment', getattr(self.instance, 'comment', ''))

        tmp = Operation(
            status=status, type=op_type, category=category, subcategory=subcategory,
            amount=amount, date=date, comment=comment
        )
        # Вызовет Operation.clean() и соберет ValidationError по полям
        tmp.full_clean()

        return attrs