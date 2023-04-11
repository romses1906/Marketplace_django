from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django_softdelete.models import SoftDeleteModel


class Product(models.Model):
    """Продукт"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))
    category = models.ForeignKey("Category", related_name='products', verbose_name=_("категория"),
                                 on_delete=models.PROTECT)


class Property(models.Model):
    """Свойство продукта"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))


class ProductProperty(models.Model):
    """Значение свойства продукта"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    value = models.CharField(max_length=128, verbose_name=_("значение"))


class Category(SoftDeleteModel, MPTTModel):
    """Категория товара"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.CharField(max_length=512, verbose_name=_("описание"))
    image = models.ImageField(upload_to='departments/', verbose_name=_("иконка"))
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True, verbose_name=_('родительская категория'))

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')

    def __str__(self):
        return self.name
