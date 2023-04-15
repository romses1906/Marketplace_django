from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

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


class Offer(models.Model):
    """Предложение магазина"""
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("цена"))


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
    link = models.URLField()
    objects = BannerManager()

    def __str__(self):
        return self.title
