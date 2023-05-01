from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django_softdelete.models import SoftDeleteModel
from django.urls import reverse
from django.utils import timezone
import os
from datetime import datetime
from taggit.managers import TaggableManager

UPLOAD_TO_CATEGORY_IMAGE = './static/img/icons/departments/'


def upload_product_image(instance, filename):
    """ Формирование пути к изображению продукта """
    return os.path.join(
        'products/',
        f'product_{instance.product.pk}_{datetime.strftime(timezone.now(), "%d.%m.%Y_%H-%M")}_{filename}'
    )


class Product(SoftDeleteModel):
    """Продукт"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    property = models.ManyToManyField(
        "Property", through="ProductProperty", related_name='products', verbose_name=_("характеристики")
    )
    category = models.ForeignKey(
        "Category", related_name='products', verbose_name=_("категория"), on_delete=models.PROTECT
    )
    description = models.TextField(max_length=2048, blank=True, verbose_name=_('описание'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('создан'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('обновлён'))
    tags = models.ManyToManyField('ProductTag', blank=True, related_name='products', verbose_name=_("теги"))

    class Meta:
        verbose_name = _('продукт')
        verbose_name_plural = _('продукты')

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.category} | {self.name}'


class ProductImage(models.Model):
    """ Изображение продукта """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_images', verbose_name=_('продукт')
    )
    image = models.ImageField(upload_to=upload_product_image, verbose_name=_('изображение'))
    description = models.TextField(blank=True, max_length=2048, verbose_name=_('описание'))
    ord_number = models.PositiveSmallIntegerField(
        unique=True, null=True, blank=True, verbose_name=_('порядковый номер')
    )

    class Meta:
        ordering = ["ord_number"]
        verbose_name = _('изображение')
        verbose_name_plural = _('изображения')


class Property(models.Model):
    """Свойство продукта"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))

    class Meta:
        verbose_name = _('свойство')
        verbose_name_plural = _('свойства')

    def __str__(self):
        return self.name


class ProductProperty(models.Model):
    """Значение свойства продукта"""
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='product_properties', verbose_name=_('продукт')
    )
    property = models.ForeignKey(
        Property, on_delete=models.PROTECT, related_name='product_properties', verbose_name=_('свойство')
    )
    value = models.CharField(max_length=128, verbose_name=_("значение"))

    class Meta:
        verbose_name = _('свойство продукта')
        verbose_name_plural = _('свойства продукта')

    def __str__(self):
        return f'{self.product} | {self.property}'


class Category(MPTTModel, SoftDeleteModel):
    """Категория товара"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    description = models.CharField(max_length=512, verbose_name=_("описание"))
    image = models.ImageField(upload_to=UPLOAD_TO_CATEGORY_IMAGE, null=True, blank=True,
                              verbose_name=_("иконка"))
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='children',
                            db_index=True, verbose_name=_('родительская категория'))

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')

    def get_absolute_url(self):
        return reverse('products:products_by_category', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    tags = TaggableManager(verbose_name=_('теги'), help_text=_('Список тегов, разделенных запятыми.'))

    class Meta:
        verbose_name = _('тэг')
        verbose_name_plural = _('тэги')

    def __str__(self):
        return ', '.join(self.tags.names())
