from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView

from products.models import Product
from users.models import User
from .models import Reviews


class CreateReviewsView(LoginRequiredMixin, View):
    """Представление по добавлению отзывов к товару."""

    template_name = 'products/product.j2'

    def get_success_url(self):
        """Возвращаемый URL при успешном выполнении методов."""
        return reverse('products:product_detail', kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        """Метод по добавлению отзыва к товару."""
        content = request.POST.get('review')
        user = User.objects.get(pk=self.request.user.pk)
        product = Product.objects.get(pk=kwargs['pk'])
        Reviews.objects.create(
            product=product,
            author=user,
            content=content
        )

        return HttpResponseRedirect(self.get_success_url())
