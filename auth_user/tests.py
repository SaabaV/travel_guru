from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

User = get_user_model()


class CustomUserTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='12345', name='Test User')
        self.user.save()

    def test_create_user(self):
        user = User.objects.create_user(
            email='testuser2@example.com',
            password='testpass123',
            name='Test User 2'
        )
        self.assertEqual(user.email, 'testuser2@example.com')
        self.assertEqual(user.name, 'Test User 2')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            name='Admin User'
        )
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertEqual(admin_user.name, 'Admin User')
        self.assertTrue(admin_user.check_password('adminpass123'))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_user/register.html')

        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth_user/login.html')

        data = {
            'username': 'testuser@example.com',
            'password': '12345'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_view(self):
        self.client.login(email='testuser@example.com', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_invalid_login(self):
        data = {
            'username': 'wronguser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_registration_form(self):
        form_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpassword123'))

    def test_login_form(self):
        form_data = {
            'username': 'testuser@example.com',
            'password': '12345'
        }
        form = AuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())




