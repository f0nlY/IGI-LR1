from django.contrib import admin
from .models import (
    Category, Product, Employee, Client, Order, OrderItem,
    UserProfile, News, Review, Vacancy, GlossaryTerm,
    PromoCode, CompanyInfo, DeliveryPoint
)

# Это для "встроенного редактирования" (Inline)
class OrderItemInline(admin.TabularInline):
    model = OrderItem  # Теперь мы напрямую указываем твою новую таблицу
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'unit')
    list_filter = ('category', 'unit')
    search_fields = ('name',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'email')
    search_fields = ('full_name', 'phone')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'order_date', 'delivery_date', 'is_delivered')
    list_filter = ('is_delivered', 'order_date')
    inlines = [OrderItemInline]
    exclude = ('products',)

# Регистрация остальных моделей
admin.site.register(Category)
admin.site.register(Employee)
admin.site.register(News)
admin.site.register(Review)
admin.site.register(UserProfile)
admin.site.register(Vacancy)
admin.site.register(GlossaryTerm)
admin.site.register(PromoCode)
admin.site.register(CompanyInfo)
admin.site.register(DeliveryPoint)