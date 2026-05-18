from django.test import TestCase, Client as TestClient
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import (Category, Product, Client, Employee,
                     Order, News, Review, Vacancy, GlossaryTerm,
                     PromoCode, UserProfile, OrderItem)
from .forms import ClientRegistrationForm, ProductForm, ReviewForm
from datetime import date, timedelta
from django.utils import timezone


# ==============================================================
# ТЕСТЫ МОДЕЛЕЙ
# ==============================================================

class CategoryModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Овощи")

    def test_str(self):
        self.assertEqual(str(self.cat), "Овощи")

    def test_create(self):
        self.assertEqual(Category.objects.count(), 1)


class ProductModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Фрукты")
        self.product = Product.objects.create(
            name="Яблоко", category=self.cat, price=2.50, unit="кг"
        )

    def test_str(self):
        self.assertEqual(str(self.product), "Яблоко")

    def test_fk_category(self):
        self.assertEqual(self.product.category.name, "Фрукты")

    def test_price_positive(self):
        self.assertGreater(self.product.price, 0)

    def test_unit_choices(self):
        self.assertIn(self.product.unit, ['шт', 'кг', 'л'])


class ClientModelTest(TestCase):
    def test_valid_client(self):
        c = Client(
            full_name="Иван Иванов",
            phone="+375 (29) 123-45-67",
            email="ivan@test.com",
            birth_date=date(1990, 1, 1)
        )
        c.full_clean()  # не должно бросить исключение

    def test_invalid_phone(self):
        c = Client(
            full_name="Тест",
            phone="80291234567",
            email="test@test.com",
            birth_date=date(1990, 1, 1)
        )
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_underage_client(self):
        c = Client(
            full_name="Тест",
            phone="+375 (29) 123-45-67",
            email="test@test.com",
            birth_date=date(2015, 1, 1)
        )
        with self.assertRaises(ValidationError):
            c.full_clean()

    def test_str(self):
        c = Client.objects.create(
            full_name="Пётр Петров",
            phone="+375 (29) 987-65-43",
            email="petr@test.com",
            birth_date=date(1985, 5, 5)
        )
        self.assertEqual(str(c), "Пётр Петров")


class EmployeeModelTest(TestCase):
    def test_underage_employee(self):
        emp = Employee(
            full_name="Молодой",
            position="Курьер",
            phone="+375 (29) 111-22-33",
            birth_date=date(2015, 1, 1)
        )
        with self.assertRaises(ValidationError):
            emp.full_clean()

    def test_valid_employee(self):
        emp = Employee(
            full_name="Иванов Иван",
            position="Менеджер",
            phone="+375 (29) 111-22-33",
            birth_date=date(1990, 6, 15)
        )
        emp.full_clean()


class OrderModelTest(TestCase):
    def setUp(self):
        self.client_obj = Client.objects.create(
            full_name="Клиент Тест",
            phone="+375 (29) 123-45-67",
            email="client@test.com",
            birth_date=date(1990, 1, 1)
        )
        self.order = Order.objects.create(
            client=self.client_obj,
            delivery_date=timezone.now() + timedelta(days=2)
        )

    def test_str(self):
        self.assertIn("Заказ №", str(self.order))

    def test_fk_client(self):
        self.assertEqual(self.order.client.full_name, "Клиент Тест")

    def test_total_price_empty(self):
        self.assertEqual(self.order.total_price(), 0)


class ManyToManyOrderTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Молочное")
        self.product = Product.objects.create(
            name="Молоко", category=self.cat, price=2.00, unit="л"
        )
        self.client_obj = Client.objects.create(
            full_name="М2М Клиент",
            phone="+375 (29) 321-00-11",
            email="m2m@test.com",
            birth_date=date(1988, 3, 3)
        )
        self.order = Order.objects.create(
            client=self.client_obj,
            delivery_date=timezone.now() + timedelta(days=1)
        )
        OrderItem.objects.create(order=self.order, product=self.product, quantity=3)

    def test_m2m_products(self):
        self.assertIn(self.product, self.order.products.all())

    def test_total_price(self):
        self.assertEqual(self.order.total_price(), 6.00)


class UserProfileOneToOneTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')
        self.profile = UserProfile.objects.create(user=self.user, role='buyer')

    def test_one_to_one(self):
        self.assertEqual(self.user.profile.role, 'buyer')

    def test_str(self):
        self.assertIn('testuser', str(self.profile))

    def test_is_buyer(self):
        self.assertTrue(self.profile.is_buyer())

    def test_is_not_employee(self):
        self.assertFalse(self.profile.is_employee())


class NewsModelTest(TestCase):
    def test_create_news(self):
        n = News.objects.create(title="Тест", content="Контент")
        self.assertEqual(str(n), "Тест")


class ReviewModelTest(TestCase):
    def test_str(self):
        r = Review.objects.create(name="Вася", text="Отлично", rating=5)
        self.assertIn("Вася", str(r))


class PromoCodeModelTest(TestCase):
    def test_create(self):
        p = PromoCode.objects.create(code="SAVE10", discount_percent=10)
        self.assertEqual(str(p), "SAVE10 — 10%")


# ==============================================================
# ТЕСТЫ ФОРМ
# ==============================================================

class ProductFormTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Зелень")

    def test_valid_form(self):
        form = ProductForm(data={
            'name': 'Укроп',
            'category': self.cat.id,
            'price': '1.50',
            'unit': 'шт',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_form_no_name(self):
        form = ProductForm(data={
            'category': self.cat.id,
            'price': '1.50',
            'unit': 'шт',
        })
        self.assertFalse(form.is_valid())

    def test_invalid_price_negative(self):
        form = ProductForm(data={
            'name': 'Тест',
            'category': self.cat.id,
            'price': '-5',
            'unit': 'шт',
        })
        self.assertFalse(form.is_valid())


class ReviewFormTest(TestCase):
    def test_valid(self):
        form = ReviewForm(data={'name': 'Вася', 'text': 'Хорошо', 'rating': 5})
        self.assertTrue(form.is_valid())

    def test_invalid_rating(self):
        form = ReviewForm(data={'name': 'Вася', 'text': 'Хорошо', 'rating': 10})
        self.assertFalse(form.is_valid())


# ==============================================================
# ТЕСТЫ VIEWS (HTTP запросы)
# ==============================================================

class PublicViewsTest(TestCase):
    def setUp(self):
        self.client_http = TestClient()
        cat = Category.objects.create(name="Тест")
        Product.objects.create(name="Продукт Тест", category=cat, price=5.00, unit="шт")
        News.objects.create(title="Новость", content="Текст")

    def test_index_200(self):
        response = self.client_http.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_contains_product(self):
        response = self.client_http.get(reverse('index'))
        self.assertContains(response, "Продукт Тест")

    def test_login_page_200(self):
        response = self.client_http.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_200(self):
        response = self.client_http.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_news_list_200(self):
        response = self.client_http.get(reverse('news_list'))
        self.assertEqual(response.status_code, 200)

    def test_vacancies_200(self):
        response = self.client_http.get(reverse('vacancies'))
        self.assertEqual(response.status_code, 200)

    def test_glossary_200(self):
        response = self.client_http.get(reverse('glossary'))
        self.assertEqual(response.status_code, 200)

    def test_promo_200(self):
        response = self.client_http.get(reverse('promo'))
        self.assertEqual(response.status_code, 200)

    def test_contacts_200(self):
        response = self.client_http.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)

    def test_about_200(self):
        response = self.client_http.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_privacy_200(self):
        response = self.client_http.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)

    def test_reviews_200(self):
        response = self.client_http.get(reverse('reviews'))
        self.assertEqual(response.status_code, 200)


class SearchAndFilterTest(TestCase):
    def setUp(self):
        self.client_http = TestClient()
        cat = Category.objects.create(name="Овощи")
        Product.objects.create(name="Помидор", category=cat, price=1.50, unit="кг")
        Product.objects.create(name="Огурец", category=cat, price=2.00, unit="кг")

    def test_search_found(self):
        response = self.client_http.get(reverse('index') + '?q=Помидор')
        self.assertContains(response, "Помидор")

    def test_search_not_found(self):
        response = self.client_http.get(reverse('index') + '?q=Помидор')
        self.assertNotContains(response, "Огурец")

    def test_sort_by_price_asc(self):
        response = self.client_http.get(reverse('index') + '?sort=price_asc')
        self.assertEqual(response.status_code, 200)

    def test_filter_by_category(self):
        cat = Category.objects.first()
        response = self.client_http.get(reverse('index') + f'?cat={cat.id}')
        self.assertEqual(response.status_code, 200)


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client_http = TestClient()
        self.user = User.objects.create_user(username='user1', password='testpass123')
        UserProfile.objects.create(user=self.user, role='employee')

    def test_login_success(self):
        response = self.client_http.post(reverse('login'), {
            'username': 'user1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects(self):
        self.client_http.login(username='user1', password='testpass123')
        response = self.client_http.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_cabinet_requires_login(self):
        response = self.client_http.get(reverse('cabinet'))
        self.assertEqual(response.status_code, 302)

    def test_statistics_requires_login(self):
        response = self.client_http.get(reverse('statistics'))
        self.assertEqual(response.status_code, 302)

    def test_product_create_requires_login(self):
        response = self.client_http.get(reverse('product_create'))
        self.assertEqual(response.status_code, 302)


class RoleAccessTest(TestCase):
    def setUp(self):
        self.client_http = TestClient()
        self.buyer = User.objects.create_user(username='buyer1', password='pass123')
        UserProfile.objects.create(user=self.buyer, role='buyer')

        self.employee = User.objects.create_user(username='emp1', password='pass123')
        UserProfile.objects.create(user=self.employee, role='employee')

    def test_buyer_cannot_create_product(self):
        self.client_http.login(username='buyer1', password='pass123')
        cat = Category.objects.create(name="Тест")
        response = self.client_http.post(reverse('product_create'), {
            'name': 'Хакерский товар', 'category': cat.id, 'price': '1', 'unit': 'шт'
        })
        # Должен быть редирект с сообщением об ошибке
        self.assertEqual(response.status_code, 302)

    def test_employee_can_access_statistics(self):
        self.client_http.login(username='emp1', password='pass123')
        response = self.client_http.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)


class ProductDetailTest(TestCase):
    def setUp(self):
        self.client_http = TestClient()
        cat = Category.objects.create(name="Молочное")
        self.product = Product.objects.create(
            name="Кефир", category=cat, price=1.80, unit="л"
        )

    def test_detail_page_200(self):
        response = self.client_http.get(reverse('product_detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)

    def test_detail_404_for_unknown(self):
        response = self.client_http.get(reverse('product_detail', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)