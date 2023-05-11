from shops.models import Banner


def active_banners(request):
    banners = Banner.objects.get_active_banners()
    return {'banners': banners}
