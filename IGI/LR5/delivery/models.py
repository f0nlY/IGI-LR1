from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from datetime import date

# ==============================================================
# ВАЛИДАТОРЫ
# ==============================================================

phone_validator = RegexValidator(
    regex=r'^\+375 \((29|25|33|44)\) \d{3}-\d{2}-\d{2}$',
    message="Номер телефона должен быть в формате: +375 (29) XXX-XX-XX"
)

def validate_age(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Возраст должен быть 18 лет и старше.")


# ==============================================================
# ОСНОВНЫЕ МОДЕЛИ (вариант 25: Продукты с доставкой)
# ==============================================================

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    UNITS = [('шт', 'штуки'), ('кг', 'килограммы'), ('л', 'литры')]

    name = models.CharField(max_length=200, verbose_name="Название товара")
    # ForeignKey — один ко многим (Category → Product)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    price = models.DecimalField(max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)], verbose_name="Цена")
    unit = models.CharField(max_length=10, choices=UNITS, verbose_name="Ед. измерения")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Employee(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО сотрудника")
    position = models.CharField(max_length=100, verbose_name="Должность")
    phone = models.CharField(validators=[phone_validator], max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email", blank=True)
    photo = models.ImageField(upload_to='employees/', blank=True, null=True, verbose_name="Фото")
    birth_date = models.DateField(validators=[validate_age], verbose_name="Дата рождения")

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.full_name


class Client(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="ФИО клиента")
    phone = models.CharField(validators=[phone_validator], max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    birth_date = models.DateField(validators=[validate_age], verbose_name="Дата рождения")
    city = models.CharField(max_length=100, verbose_name="Город", blank=True)
    address = models.TextField(verbose_name="Адрес", blank=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.full_name


class Order(models.Model):
    # ForeignKey — один ко многим (Client → Order)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Клиент")
    # ManyToMany — многие ко многим (Order ↔ Product)
    products = models.ManyToManyField(Product, through='OrderItem', verbose_name="Товары")
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Скидка")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    delivery_date = models.DateTimeField(verbose_name="Дата доставки")
    is_delivered = models.BooleanField(default=False, verbose_name="Доставлено")
    delivery_address = models.TextField(verbose_name="Адрес доставки", blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ №{self.id} — {self.client.full_name}"

    def total_price(self):
        items_total = sum(item.quantity * item.product.price for item in self.orderitem_set.all())
        return items_total - self.discount

class OrderItem(models.Model):
    """Промежуточная таблица для ManyToMany Order ↔ Product с количеством"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


# ==============================================================
# OneToOneField — профиль пользователя (один к одному User ↔ UserProfile)
# ==============================================================

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Покупатель'),
        ('employee', 'Сотрудник'),
    ]
    # OneToOneField — один к одному
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='profile', verbose_name="Пользователь")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,
                             default='buyer', verbose_name="Роль")
    client = models.ForeignKey(Client, on_delete=models.SET_NULL,
                                null=True, blank=True, verbose_name="Клиент")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                  null=True, blank=True, verbose_name="Сотрудник")

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль: {self.user.username} ({self.get_role_display()})"

    def is_employee(self):
        return self.role == 'employee'

    def is_buyer(self):
        return self.role == 'buyer'


# ==============================================================
# МОДЕЛИ ДЛЯ ОБЩИХ СТРАНИЦ САЙТА (из ТЗ стр. 2)
# ==============================================================

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Текст новости")
    summary = models.CharField(max_length=300, verbose_name="Краткое содержание", blank=True)
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name="Картинка")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Review(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    text = models.TextField(verbose_name="Отзыв")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Оценка")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата")
    # ForeignKey на User — чтобы знать кто оставил отзыв
    user = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name="Пользователь")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} — {self.rating}★"


class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name="Должность")
    description = models.TextField(verbose_name="Описание вакансии")
    salary = models.CharField(max_length=100, verbose_name="Зарплата", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return self.title


class GlossaryTerm(models.Model):
    """Словарь терминов и понятий (FAQ)"""
    question = models.CharField(max_length=300, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    date_added = models.DateField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Термин/FAQ"
        verbose_name_plural = "Словарь терминов"

    def __str__(self):
        return self.question


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Промокод")
    discount_percent = models.PositiveIntegerField(verbose_name="Скидка (%)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    valid_until = models.DateField(verbose_name="Действителен до", null=True, blank=True)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды и купоны"

    def __str__(self):
        return f"{self.code} — {self.discount_percent}%"


class CompanyInfo(models.Model):
    """О компании"""
    name = models.CharField(max_length=200, verbose_name="Название компании")
    description = models.TextField(verbose_name="Описание")
    founded_year = models.PositiveIntegerField(verbose_name="Год основания", null=True, blank=True)
    address = models.TextField(verbose_name="Адрес", blank=True)
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    email = models.EmailField(verbose_name="Email", blank=True)

    class Meta:
        verbose_name = "О компании"
        verbose_name_plural = "О компании"

    def __str__(self):
        return self.name


class DeliveryPoint(models.Model):
    """Точки самовывоза"""
    name = models.CharField(max_length=200, verbose_name="Название")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, validators=[phone_validator], verbose_name="Телефон")
    working_hours = models.CharField(max_length=100, verbose_name="Часы работы", blank=True)

    class Meta:
        verbose_name = "Точка самовывоза"
        verbose_name_plural = "Точки самовывоза"

    def __str__(self):
        return self.name