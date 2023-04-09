from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """Продукт"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))


class Property(models.Model):
    """Свойство продукта"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))


class ProductProperty(models.Model):
    """Значение свойства продукта"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    value = models.CharField(max_length=128, verbose_name=_("значение"))


class Category(models.Model):
    """Категория товара"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.CharField(max_length=512, verbose_name=_("описание"))
    image = models.ImageField(upload_to='departments/', verbose_name=_("иконка"))
    product = models.ForeignKey(Product, related_name='category', on_delete=models.PROTECT)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')
        ordering = ['is_active']

    def __str__(self):
        return self.name
