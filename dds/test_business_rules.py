from django.test import TestCase
from django.core.exceptions import ValidationError
from dds.models import OperationStatus, OperationType, Category, Subcategory, Operation
from django.utils import timezone
from decimal import Decimal


class BusinessRulesTest(TestCase):
    def setUp(self):
        self.s_bus = OperationStatus.objects.create(name='Бизнес')
        self.t_in = OperationType.objects.create(name='Пополнение')
        self.t_out = OperationType.objects.create(name='Списание')
        self.cat_inf = Category.objects.create(name='Инфраструктура', type=self.t_in)
        self.cat_mkt = Category.objects.create(name='Маркетинг', type=self.t_out)
        self.sub_vps = Subcategory.objects.create(name='VPS', category=self.cat_inf)
        self.sub_avito = Subcategory.objects.create(name='Avito', category=self.cat_mkt)

    def test_valid_operation(self):
        op = Operation.objects.create(
            date=timezone.now().date(), status=self.s_bus, type=self.t_in,
            category=self.cat_inf, subcategory=self.sub_vps, amount=Decimal('1000.00')
        )
        self.assertIsNotNone(op.pk)

    def test_invalid_category_for_type(self):
        op = Operation(
            date=timezone.now().date(), status=self.s_bus, type=self.t_in,
            category=self.cat_mkt, subcategory=self.sub_avito, amount=Decimal('1000.00')
        )
        with self.assertRaises(ValidationError):
            op.full_clean()

    def test_invalid_subcategory_for_category(self):
        op = Operation(
            date=timezone.now().date(), status=self.s_bus, type=self.t_in,
            category=self.cat_inf, subcategory=self.sub_avito, amount=Decimal('1000.00')
        )
        with self.assertRaises(ValidationError):
            op.full_clean()

    def test_amount_positive(self):
        op = Operation(
            date=timezone.now().date(), status=self.s_bus, type=self.t_in,
            category=self.cat_inf, subcategory=self.sub_vps, amount=Decimal('-1')
        )
        with self.assertRaises(ValidationError):
            op.full_clean()
