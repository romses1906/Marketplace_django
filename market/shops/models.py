from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Max, Sum
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from settings.models import SiteSettings
from users.models import User

from .services import offer_price_with_discount

phone_validate = RegexValidator(
    regex=r'^\+\d{1,3}\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$',
    message=_("Номер телефона должен быть введен в формате: '+7 (123) 456-78-90'. Максимальная длина 12 символов.")
)

banners_cache_time = 60 * SiteSettings.load().banners_cache_time


class Shop(models.Model):
    """Магазин"""
    name = models.CharField(max_length=512, verbose_name=_("название"))
    products = models.ManyToManyField("products.Product", through="Offer", related_name="shops",
                                      verbose_name=_("товары в магазине"))
    description = models.TextField(verbose_name=_("описание магазина"), blank=True, null=True)
    phone_number = models.CharField(max_length=18, validators=[phone_validate], verbose_name=_("номер телефона"),
                                    blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name=_("адрес"), blank=True, null=True)
    email = models.EmailField(max_length=255, verbose_name=_("email"), blank=True, null=True)
    user = models.OneToOneField(to=User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('магазин')
        verbose_name_plural = _('магазины')

    def get_absolute_url(self):
        """ Метод получения url детальной страницы магазина """

        return reverse('shops:shop-detail', kwargs={'pk': self.pk})

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
        """ Метод получения url """

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
        return f'{self.shop} | {self.product} | {_("цена")}: {self.price} | {_("наличие")}: {self.in_stock} | ' \
               f'{_("уже купили")}: {self.total_purchases() if self.total_purchases() else 0}'

    def total_purchases(self):
        """
        Метод получения количества покупок товара
        """

        offers = Offer.objects.select_related('shop', 'product__category').filter(order__status='paid').annotate(
            total_purchases=Sum('orderitem__quantity'))
        for offer in offers:
            if offer.id == self.id:
                return offer.total_purchases

    def get_price_on_discount(self):
        """
        Метод получения цены на товар со скидкой
        """

        disc_price = offer_price_with_discount(product_id=self.product.id, price=self.price)
        if not disc_price:
            disc_price = self.price
        return disc_price


class BannerManager(models.Manager):
    """Менеджер для отображения активных баннеров на главной странице."""

    def get_active_banners(self):
        """ Метод получения действующих баннеров """

        # Проверяем, есть ли закешированные баннеры
        banners = cache.get('active_banners')

        if not banners:
            # Если закешированных баннеров нет, получаем активные баннеры и сохраняем в кеш
            banners = list(self.filter(is_active=True).order_by('?')[:3])
            cache.set('active_banners', banners, banners_cache_time)
        else:
            # Если есть закешированные баннеры, проверяем обновления перед возвратом
            active_banners = list(self.filter(is_active=True).order_by('?')[:3])
            if banners != active_banners:
                cache.delete('active_banners')
                banners = active_banners
                cache.set('active_banners', banners, banners_cache_time)

        return banners


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
