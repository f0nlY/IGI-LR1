import statistics
import requests
import calendar
import json
import logging
import io

import matplotlib
matplotlib.use('Agg')  # без GUI — обязательно до pyplot
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse

from .models import (Product, News, Category, Review, Vacancy,
                     GlossaryTerm, PromoCode, Employee, Client,
                     Order, CompanyInfo, DeliveryPoint, UserProfile, OrderItem)
from .forms import ClientRegistrationForm, ProductForm, ReviewForm

logger = logging.getLogger('delivery')


# ==============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================================

def get_api_data():
    """Получает данные из внешних API (курс валют и погода)"""
    usd_rate = 3.25
    try:
        res = requests.get('https://api.nbrb.by/exrates/rates/431', timeout=3)
        if res.status_code == 200:
            usd_rate = res.json()['Cur_OfficialRate']
    except Exception as e:
        logger.warning(f"НБРБ API недоступен: {e}")

    weather = "Данные недоступны"
    try:
        res = requests.get('https://wttr.in/Minsk?format=3', timeout=3)
        if res.status_code == 200:
            weather = res.text
    except Exception as e:
        logger.warning(f"wttr.in API недоступен: {e}")

    return usd_rate, weather


def get_user_role(user):
    """Возвращает роль пользователя: 'admin', 'employee', 'buyer', 'guest'"""
    if not user.is_authenticated:
        return 'guest'
    if user.is_superuser:
        return 'admin'
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return 'buyer'


# ==============================================================
# ГЛАВНАЯ СТРАНИЦА
# ==============================================================

def index(request):

    if not request.user.is_authenticated:
        return redirect('register')
    logger.info(f"Главная страница. Пользователь: {request.user}")

    query = request.GET.get('q', '')
    cat_id = request.GET.get('cat', '')
    sort = request.GET.get('sort', 'name')

    products = Product.objects.select_related('category').all()

    if query:
        products = products.filter(name__icontains=query)
    if cat_id:
        products = products.filter(category_id=cat_id)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('name')

    usd_rate, weather = get_api_data()

    prices = [float(p.price) for p in products]
    avg_price = round(statistics.mean(prices), 2) if prices else 0
    median_price = round(statistics.median(prices), 2) if prices else 0
    try:
        mode_price = round(statistics.mode(prices), 2)
    except statistics.StatisticsError:
        mode_price = "Нет моды"

    for p in products:
        p.price_usd = round(float(p.price) / usd_rate, 2)

    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)
    text_calendar = calendar.HTMLCalendar().formatmonth(now_local.year, now_local.month)

    role = get_user_role(request.user)

    context = {
        'products': products,
        'categories': Category.objects.all(),
        'latest_news': News.objects.order_by('-pub_date').first(),
        'avg_price': avg_price,
        'median_price': median_price,
        'mode_price': mode_price,
        'now_local': now_local,
        'now_utc': now_utc,
        'text_calendar': text_calendar,
        'usd_rate': usd_rate,
        'weather': weather,
        'current_query': query,
        'role': role,
    }
    return render(request, 'delivery/index.html', context)


# ==============================================================
# CRUD ДЛЯ ТОВАРОВ
# ==============================================================

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    usd_rate, _ = get_api_data()
    product.price_usd = round(float(product.price) / usd_rate, 2)
    role = get_user_role(request.user)
    return render(request, 'delivery/product_detail.html', {'product': product, 'role': role})


@login_required
def product_create(request):
    role = get_user_role(request.user)
    if role not in ('admin', 'employee'):
        messages.error(request, "Нет доступа.")
        return redirect('index')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            logger.info(f"Создан товар: {form.cleaned_data['name']} пользователем {request.user}")
            messages.success(request, "Товар успешно добавлен!")
            return redirect('index')
    else:
        form = ProductForm()
    return render(request, 'delivery/product_form.html', {'form': form, 'action': 'Создать'})


@login_required
def product_edit(request, pk):
    role = get_user_role(request.user)
    if role not in ('admin', 'employee'):
        messages.error(request, "Нет доступа.")
        return redirect('index')

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            logger.info(f"Товар #{pk} отредактирован пользователем {request.user}")
            messages.success(request, "Товар обновлён!")
            return redirect('product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'delivery/product_form.html', {'form': form, 'action': 'Редактировать'})


@login_required
def product_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Только администратор может удалять товары.")
        return redirect('index')

    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        logger.warning(f"Товар '{name}' удалён пользователем {request.user}")
        messages.success(request, f"Товар '{name}' удалён.")
        return redirect('index')
    return render(request, 'delivery/product_confirm_delete.html', {'product': product})


# ==============================================================
# ЛИЧНЫЙ КАБИНЕТ
# ==============================================================

@login_required
def cabinet(request):
    role = get_user_role(request.user)
    context = {'role': role}

    if role == 'buyer':
        try:
            client = request.user.profile.client
            orders = Order.objects.filter(client=client).prefetch_related('orderitem_set__product')
            context['orders'] = orders
            context['client'] = client
        except (UserProfile.DoesNotExist, AttributeError):
            context['orders'] = []

    elif role == 'employee':
        context['orders'] = Order.objects.select_related('client').order_by('-order_date')
        context['clients'] = Client.objects.all()

    elif role == 'admin':
        return redirect('/admin/')

    return render(request, 'delivery/cabinet.html', context)


# ==============================================================
# СТАТИСТИКА + MATPLOTLIB ГРАФИК
# ==============================================================

@login_required
def statistics_view(request):
    role = get_user_role(request.user)
    if role not in ('admin', 'employee'):
        messages.error(request, "Нет доступа.")
        return redirect('index')

    cats = Category.objects.annotate(product_count=Count('product'))

    sales_by_cat = (
        Category.objects
        .annotate(total=Sum('product__orderitem__quantity'))
        .values('name', 'total')
        .order_by('-total')
    )

    all_prices = list(Product.objects.values_list('price', flat=True))
    float_prices = [float(p) for p in all_prices]

    context = {
        'sales_by_cat': sales_by_cat,
        'total_products': len(all_prices),
        'total_orders': Order.objects.count(),
        'total_clients': Client.objects.count(),
        'avg_price': round(statistics.mean(float_prices), 2) if float_prices else 0,
        'median_price': round(statistics.median(float_prices), 2) if float_prices else 0,
        'role': role,
    }
    return render(request, 'delivery/statistics.html', context)


@login_required
def chart_view(request):
    """
    График товаров по категориям через matplotlib.
    Возвращает PNG-изображение — используется как <img src="/statistics/chart/">
    """
    role = get_user_role(request.user)
    if role not in ('admin', 'employee'):
        return HttpResponse(status=403)

    cats = Category.objects.annotate(product_count=Count('product'))
    labels = [c.name for c in cats]
    values = [c.product_count for c in cats]

    colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12',
              '#9b59b6', '#1abc9c', '#e67e22', '#34495e']

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=colors[:len(labels)])
    ax.set_title('Количество товаров по категориям', fontsize=14, pad=15)
    ax.set_xlabel('Категория', fontsize=11)
    ax.set_ylabel('Количество товаров', fontsize=11)
    ax.bar_label(bars, padding=3)
    ax.set_ylim(0, max(values) + 2 if values else 5)
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')


# ==============================================================
# ОБЩИЕ СТРАНИЦЫ САЙТА
# ==============================================================

def news_list(request):
    news = News.objects.order_by('-pub_date')
    return render(request, 'delivery/news_list.html', {'news': news})


def news_detail(request, pk):
    article = get_object_or_404(News, pk=pk)
    return render(request, 'delivery/news_detail.html', {'article': article})


def reviews(request):
    all_reviews = Review.objects.order_by('-date')
    form = None

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                logger.info(f"Новый отзыв от {request.user.username}")
                messages.success(request, "Отзыв добавлен!")
                return redirect('reviews')
        else:
            form = ReviewForm()

    return render(request, 'delivery/reviews.html', {'reviews': all_reviews, 'form': form})


def vacancies(request):
    active = Vacancy.objects.filter(is_active=True)
    return render(request, 'delivery/vacancies.html', {'vacancies': active})


def glossary(request):
    terms = GlossaryTerm.objects.order_by('date_added')
    return render(request, 'delivery/glossary.html', {'terms': terms})


def promo(request):
    active_promos = PromoCode.objects.filter(is_active=True)
    archive_promos = PromoCode.objects.filter(is_active=False)
    return render(request, 'delivery/promo.html', {
        'active_promos': active_promos,
        'archive_promos': archive_promos,
        'role': get_user_role(request.user),
    })


def contacts(request):
    employees = Employee.objects.all()
    points = DeliveryPoint.objects.all()
    return render(request, 'delivery/contacts.html', {
        'employees': employees,
        'points': points,
    })


def about(request):
    info = CompanyInfo.objects.first()
    return render(request, 'delivery/about.html', {'info': info})


def privacy(request):
    return render(request, 'delivery/privacy.html')


# ==============================================================
# АВТОРИЗАЦИЯ / РЕГИСТРАЦИЯ
# ==============================================================

def register_view(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f"Новый пользователь зарегистрирован: {user.username}")
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('index')
    else:
        form = ClientRegistrationForm()
    return render(request, 'delivery/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"Пользователь {user.username} вошёл в систему")
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'delivery/login.html', {'form': form})


def logout_view(request):
    username = request.user.username
    logout(request)
    logger.info(f"Пользователь {username} вышел из системы")
    return redirect('index')

@login_required
def create_order(request, product_id):
    if request.method == 'POST':
        role = get_user_role(request.user)
        if role != 'buyer':
            messages.error(request, "Только покупатели могут делать заказы.")
            return redirect('index')

        product = get_object_or_404(Product, pk=product_id)
        client_profile = request.user.profile.client
        
        # Логика промокода
        promo_code = request.POST.get('promo_code')
        discount_amount = 0
        if promo_code:
            try:
                pc = PromoCode.objects.get(code=promo_code, is_active=True)
                if not pc.valid_until or pc.valid_until >= timezone.now().date():
                    discount_amount = (product.price * pc.discount_percent) / 100
                    messages.success(request, f"Промокод применен! Скидка: {discount_amount} BYN")
                else:
                    messages.error(request, "Срок действия промокода истек.")
            except PromoCode.DoesNotExist:
                messages.error(request, "Неверный промокод.")

        # Создаем заказ с сохранением скидки
        new_order = Order.objects.create(
            client=client_profile,
            delivery_date=timezone.now() + timezone.timedelta(days=3),
            delivery_address=client_profile.address or "Самовывоз",
            discount=discount_amount  # Сохраняем скидку в базу!
        )
        
        # Создаем позицию заказа (теперь NameError не будет)
        OrderItem.objects.create(order=new_order, product=product, quantity=1)

        messages.success(request, f"Заказ №{new_order.id} успешно оформлен!")
        return redirect('cabinet')
    
    return redirect('product_detail', pk=product_id)
# 1. Добавить в корзину
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] += 1
    else:
        cart[product_id_str] = 1
        
    request.session['cart'] = cart
    messages.success(request, "Товар добавлен в корзину!")
    return redirect('index')

# 2. Просмотр корзины
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    for p_id, qty in cart.items():
        product = get_object_or_404(Product, pk=p_id)
        item_total = product.price * qty
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': qty,
            'total': item_total
        })
    
    # Логика промокода
    promo_code = request.GET.get('promo')
    discount = 0
    if promo_code:
        try:
            pc = PromoCode.objects.get(code=promo_code, is_active=True)
            if pc.valid_until and pc.valid_until < timezone.now().date():
                messages.error(request, "Срок действия промокода истек.")
            else:
                discount = (total_price * pc.discount_percent) / 100
                total_price -= discount
                messages.success(request, f"Применен промокод на {pc.discount_percent}%!")
        except PromoCode.DoesNotExist:
            messages.error(request, "Неверный промокод.")

    return render(request, 'delivery/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'discount': discount,
        'promo': promo_code
    })

# 3. Финальное оформление (создание Order в базе)
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('index')
        
    role = get_user_role(request.user)
    if role != 'buyer':
        messages.error(request, "Только покупатели могут делать заказы.")
        return redirect('index')

    client_profile = request.user.profile.client
    
    # Создаем заказ
    new_order = Order.objects.create(
        client=client_profile,
        delivery_date=timezone.now() + timezone.timedelta(days=3),
        delivery_address=client_profile.address or "Самовывоз",
    )
    
    # Переносим товары из корзины в базу (OrderItem)
    for p_id, qty in cart.items():
        product = get_object_or_404(Product, pk=p_id)
        OrderItem.objects.create(order=new_order, product=product, quantity=qty)
    
    # Очищаем корзину
    request.session['cart'] = {}
    
    # ВАЖНО: Статистика обновится автоматически, так как 
    # твои графики и расчеты тянут данные из БД (моделей Order и OrderItem)
    
    messages.success(request, f"Заказ №{new_order.id} успешно оформлен!")
    return redirect('cabinet')