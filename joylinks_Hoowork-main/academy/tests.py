from django.test import TestCase
from django.urls import reverse

from users.models import User
from academy.models import MarketProduct, MarketPurchase
from homeworks.models import Notification


class MarketTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            password="pass",
            role=User.Role.ADMIN,
        )
        self.student = User.objects.create_user(
            username="student",
            password="pass",
            role=User.Role.STUDENT,
            coin_balance=1000,
        )
        self.product = MarketProduct.objects.create(
            name="Toy",
            price_coins=100,
            is_active=True,
        )

    def test_student_purchase_and_notifications(self):
        self.client.login(username="student", password="pass")
        response = self.client.post(
            reverse("buy_product", args=[self.product.id]), follow=True
        )
        self.assertEqual(response.status_code, 200)

        purchase = MarketPurchase.objects.get(student=self.student, product=self.product)
        self.assertFalse(purchase.admin_confirmed)

        # coin balances adjusted
        self.student.refresh_from_db()
        self.admin.refresh_from_db()
        self.assertEqual(self.student.coin_balance, 900)
        self.assertEqual(self.admin.coin_balance, 100)

        # notifications sent
        self.assertTrue(
            Notification.objects.filter(user=self.admin, message__contains="Toy").exists()
        )
        self.assertTrue(
            Notification.objects.filter(user=self.student, notification_type=Notification.NotificationType.SYSTEM).exists()
        )

    def test_admin_confirm_purchase(self):
        purchase = MarketPurchase.objects.create(
            student=self.student,
            product=self.product,
            coins_spent=100,
        )
        self.client.login(username="admin", password="pass")
        resp = self.client.get(
            reverse("market_purchase_confirm", args=[purchase.pk]), follow=True
        )
        self.assertEqual(resp.status_code, 200)
        purchase.refresh_from_db()
        self.assertTrue(purchase.admin_confirmed)
        self.assertTrue(
            Notification.objects.filter(user=self.student, message__contains="berildi").exists()
        )
