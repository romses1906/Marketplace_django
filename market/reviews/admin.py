from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Reviews


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    """Регистрация модели Отзывов в админ-панели."""
    list_display = 'product', 'author', 'content_short', 'created_at'
    list_filter = 'product',

    @staticmethod
    def content_short(obj: Reviews) -> str:
        """Метод, обрезающий длину символов отзыва под отображение в админ-панели."""
        if len(obj.content) < 38:
            return obj.content
        return obj.content[:38] + "..."

    content_short.short_description = _('содержимое отзыва')
