from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from products.models import Product


class Reviews(models.Model):
    """Модель отзывов к продуктам."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_reviews',
        null=False, blank=False, verbose_name=_('продукт')
    )
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name=_('автор отзыва'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('время добавления'))
    content = models.TextField(null=False, blank=False, verbose_name=_('содержимое отзыва'))

    class Meta:
        """Класс переопределяющий параметры модели."""
        verbose_name = _('отзыв')
        verbose_name_plural = _('отзывы')

    def __str__(self):
        """Переопределение строкового представления модели."""
        return f'{self.product.name}, автор - {self.author.username}'
