# Generated by Django 4.2 on 2023-07-13 11:46

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, verbose_name='наименование')),
                ('description', models.TextField(blank=True, max_length=2048, verbose_name='описание')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='дата начала действия скидки')),
                ('end_date', models.DateTimeField(verbose_name='дата окончания действия скидки')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='создана')),
                ('value', models.IntegerField(verbose_name='значение скидки')),
                ('value_type', models.CharField(choices=[('percentage', 'Скидка в процентах'), ('fixed_amount', 'Фиксированный объем скидки (в рублях)'), ('fixed_price', 'Фиксированная цена после применения скидки')], max_length=50, verbose_name='тип скидки')),
            ],
            options={
                'verbose_name': 'скидка на товар',
                'verbose_name_plural': 'скидки на товары',
            },
        ),
        migrations.CreateModel(
            name='DiscountOnCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, verbose_name='наименование')),
                ('description', models.TextField(blank=True, max_length=2048, verbose_name='описание')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='дата начала действия скидки')),
                ('end_date', models.DateTimeField(verbose_name='дата окончания действия скидки')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='создана')),
                ('value', models.PositiveIntegerField(verbose_name='значение скидки')),
                ('value_type', models.CharField(choices=[('percentage', 'Скидка в процентах'), ('fixed_amount', 'Фиксированный объем скидки (в рублях)'), ('fixed_price', 'Фиксированная цена после применения скидки')], max_length=50, verbose_name='тип скидки')),
                ('quantity_at', models.PositiveIntegerField(default=1, verbose_name='количество товаров в корзине от')),
                ('quantity_to', models.PositiveIntegerField(default=1, verbose_name='количество товаров в корзине до')),
                ('cart_total_price_at', models.PositiveIntegerField(default=1, verbose_name='общая стоимость товаров в корзине от')),
            ],
            options={
                'verbose_name': 'скидка на корзину',
                'verbose_name_plural': 'скидки на корзину',
            },
        ),
        migrations.CreateModel(
            name='DiscountOnSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, verbose_name='наименование')),
                ('description', models.TextField(blank=True, max_length=2048, verbose_name='описание')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='дата начала действия скидки')),
                ('end_date', models.DateTimeField(verbose_name='дата окончания действия скидки')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='создана')),
                ('value', models.PositiveIntegerField(verbose_name='значение скидки')),
                ('value_type', models.CharField(choices=[('percentage', 'Скидка в процентах'), ('fixed_amount', 'Фиксированный объем скидки (в рублях)'), ('fixed_price', 'Фиксированная цена после применения скидки')], max_length=50, verbose_name='тип скидки')),
            ],
            options={
                'verbose_name': 'скидка на наборы товаров',
                'verbose_name_plural': 'скидки на наборы товаров',
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_order_price_for_free_shipping', models.DecimalField(decimal_places=2, default=2000.0, max_digits=6, verbose_name='минимальная стоимость заказа для бесплатной доставки, руб')),
                ('standard_order_price', models.DecimalField(decimal_places=2, default=200.0, max_digits=6, verbose_name='стоимость стандартной досавки, руб')),
                ('express_order_price', models.DecimalField(decimal_places=2, default=500.0, max_digits=6, verbose_name='стоимость экспресс доставки, руб')),
                ('banners_count', models.PositiveIntegerField(default=3, validators=[django.core.validators.MaxValueValidator(3)], verbose_name='количество баннеров')),
                ('banners_cache_time', models.PositiveIntegerField(default=10, verbose_name='время кэширования, минут')),
                ('top_product_count', models.PositiveIntegerField(default=8, validators=[django.core.validators.MaxValueValidator(8)], verbose_name='количество самых популярных товаров')),
                ('limited_edition_count', models.PositiveIntegerField(default=16, validators=[django.core.validators.MaxValueValidator(16)], verbose_name='количество лимитированных предложений')),
                ('hot_deals', models.PositiveIntegerField(default=3, validators=[django.core.validators.MaxValueValidator(9)], verbose_name='количество горячих предложений')),
                ('product_cache_time', models.PositiveIntegerField(default=1, verbose_name='время кэширования, дней')),
                ('categories_cache_time', models.PositiveIntegerField(default=1, verbose_name='время кэширования меню категорий, дней')),
            ],
            options={
                'verbose_name': 'настройки',
                'verbose_name_plural': 'настройка',
            },
        ),
        migrations.CreateModel(
            name='ProductInDiscountOnSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products_in_set', to='settings.discountonset', verbose_name='скидка')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products_in_set', to='products.product', verbose_name='продукт')),
            ],
            options={
                'verbose_name': 'товар из наборов со скидкой',
                'verbose_name_plural': 'товары из наборов со скидкой',
            },
        ),
        migrations.AddConstraint(
            model_name='discountonset',
            constraint=models.CheckConstraint(check=models.Q(('end_date__gt', models.F('start_date'))), name='check_dates_in_discount_on_set', violation_error_message='Дата окончания действия скидки должна быть больше даты начала!'),
        ),
        migrations.AddConstraint(
            model_name='discountonset',
            constraint=models.CheckConstraint(check=models.Q(('value_type__in', ('fixed_amount', 'fixed_price')), models.Q(('value__gt', 0), ('value_type', 'percentage'), ('value__lt', 100), ('value_type', 'percentage')), _connector='OR'), name='check_value_percentage_in_discount_on_set', violation_error_message='Процент скидки не может быть менее 0 и более 100'),
        ),
        migrations.AddConstraint(
            model_name='discountoncart',
            constraint=models.CheckConstraint(check=models.Q(('end_date__gt', models.F('start_date'))), name='check_dates_in_discount_on_cart', violation_error_message='Дата окончания действия скидки должна быть больше даты начала!'),
        ),
        migrations.AddConstraint(
            model_name='discountoncart',
            constraint=models.CheckConstraint(check=models.Q(('value_type__in', ('fixed_amount', 'fixed_price')), models.Q(('value__gt', 0), ('value_type', 'percentage'), ('value__lt', 100), ('value_type', 'percentage')), _connector='OR'), name='check_value_percentage_in_discount_on_cart', violation_error_message='Процент скидки не может быть менее 0 и более 100'),
        ),
        migrations.AddField(
            model_name='discount',
            name='products',
            field=models.ManyToManyField(related_name='discounts', to='products.product', verbose_name='продукты'),
        ),
        migrations.AddConstraint(
            model_name='discount',
            constraint=models.CheckConstraint(check=models.Q(('end_date__gt', models.F('start_date'))), name='check_dates_in_discount', violation_error_message='Дата окончания действия скидки должна быть больше даты начала!'),
        ),
        migrations.AddConstraint(
            model_name='discount',
            constraint=models.CheckConstraint(check=models.Q(('value_type__in', ('fixed_amount', 'fixed_price')), models.Q(('value__gt', 0), ('value_type', 'percentage'), ('value__lt', 100), ('value_type', 'percentage')), _connector='OR'), name='check_value_percentage_in_discount', violation_error_message='Процент скидки не может быть менее 0 и более 100'),
        ),
    ]
