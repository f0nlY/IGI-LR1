from django.urls import path, re_path
from . import views

urlpatterns = [
    # Главная
    path('', views.index, name='index'),

    # Авторизация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Детальная страница товара — re_path с регулярным выражением (требование ТЗ)
    re_path(r'^product/(?P<pk>[0-9]+)/$', views.product_detail, name='product_detail'),

    # CRUD для товаров (только для сотрудников/админа)
    path('product/create/', views.product_create, name='product_create'),
    re_path(r'^product/(?P<pk>[0-9]+)/edit/$', views.product_edit, name='product_edit'),
    re_path(r'^product/(?P<pk>[0-9]+)/delete/$', views.product_delete, name='product_delete'),

    # Личный кабинет
    path('cabinet/', views.cabinet, name='cabinet'),

    # Общие страницы сайта
    path('news/', views.news_list, name='news_list'),
    re_path(r'^news/(?P<pk>[0-9]+)/$', views.news_detail, name='news_detail'),
    path('reviews/', views.reviews, name='reviews'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('glossary/', views.glossary, name='glossary'),
    path('promo/', views.promo, name='promo'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),

    # Статистика + matplotlib график
    path('statistics/', views.statistics_view, name='statistics'),
    path('statistics/chart/', views.chart_view, name='chart'),

    path('order/<int:product_id>/', views.create_order, name='create_order'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
]