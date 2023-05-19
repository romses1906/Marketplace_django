from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.templatetags.static import static

from users.models import User

phone_validate = RegexValidator(
    regex=r'^\+?[78]\d{10}$',
    message=_("Номер телефона должен быть введен в формате: '+71234567890'. Максимальная длина 12 символов.")
)


class Shop(models.Model):
    """Магазин"""
    name = models.CharField(max_length=512, verbose_name=_("название"))
    products = models.ManyToManyField("products.Product", through="Offer", related_name="shops",
                                      verbose_name=_("товары в магазине"))
    description = models.TextField(verbose_name=_("описание магазина"), blank=True, null=True)
    phone_number = models.CharField(max_length=12, validators=[phone_validate], verbose_name=_("номер телефона"),
                                    blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name=_("адрес"), blank=True, null=True)
    email = models.EmailField(max_length=255, verbose_name=_("email"), blank=True, null=True)
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('магазин')
        verbose_name_plural = _('магазины')

    def __str__(self):
        return self.name


class Offer(models.Model):
    """Предложение магазина"""
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name='offers', verbose_name=_('магазин'))
    product = models.ForeignKey(
        "products.Product", on_delete=models.PROTECT, related_name='offers', verbose_name=_('продукт')
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('создано'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('обновлено'))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("цена"))
    in_stock = models.IntegerField(blank=True, null=False, default=0, verbose_name=_("наличие"))
    limited_edition = models.BooleanField(default=True, verbose_name=_("ограниченное предложение"))
    index = models.IntegerField(default=0, verbose_name=_("индекс сортировки"))

    class Meta:
        verbose_name = _('предложение')
        verbose_name_plural = _('предложения')

    def get_absolute_url(self):
        return reverse('shops:offer_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """
        Задаем значение индекса сортировки для новых товаров
        """
        if not self.pk:
            latest_index = Offer.objects.aggregate(last_index=Max('index')).get('last_index') or 0
            self.index = latest_index + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.shop} | {self.product} | {_("цена")}: {self.price} | {_("наличие")}: {self.in_stock}'


class BannerManager(models.Manager):
    """Менеджер,для отображения активных баннеров на главной странице."""

    def get_active_banners(self):
        return self.filter(is_active=True).order_by('?')[:3]


class Banner(models.Model):
    """Баннеры магазина"""
    image = models.ImageField(upload_to='banners/')
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=False)
    link = models.CharField(blank=True)
    objects = BannerManager()

    class Meta:
        verbose_name = _('баннер')
        verbose_name_plural = _('баннеры')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[str(self.id)])

    def get_image_url(self):
        return static(self.image)
