
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.forms import ProgrammerCreationForm, DevRadarUserCreationForm

User = get_user_model()


class RegisterProgrammerUserViewTest(TestCase):
    def test_view_returns_200(self):
        response = self.client.get(reverse('register_programmer'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('register_programmer'))
        self.assertTemplateUsed(response, 'accounts/register_programmer.html')



    def test_user_is_created(self):
        self.client.post(reverse('register_programmer'), {
            'username': 'test_programmer',
            'password': 'test_password',
            'email': 'test@example.com',
        })
        self.assertEqual(User.objects.count(), 1)



class RegisterDevRadarUserViewTest(TestCase):
    def test_view_returns_200(self):
        response = self.client.get(reverse('register_user'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('register_user'))
        self.assertTemplateUsed(response, 'accounts/register_user.html')



    def test_user_is_created(self):
        self.client.post(reverse('register_user'), {
            'username': 'test_user',
            'password': 'test_password',
            'email': 'test@example.com',
        })
        self.assertEqual(User.objects.count(), 1)




class UpdateDevRadarUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_view_returns_200(self):
        response = self.client.get(reverse('update_user', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('update_user', kwargs={'pk': self.user.pk}))
        self.assertTemplateUsed(response, 'accounts/forms/update_user_form.html')




class DeleteDevRadarUserTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_view_returns_200(self):
        response = self.client.get(reverse('delete_user', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('delete_user', kwargs={'pk': self.user.pk}))
        self.assertTemplateUsed(response, 'accounts/forms/delete_user_form.html')



    def test_user_is_redirected(self):
        response = self.client.post(reverse('delete_user', kwargs={'pk': self.user.pk}))
        self.assertRedirects(response, reverse('login'))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.login(username='test_user', password='test_password')

    def test_view_returns_200(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('profile'))
        self.assertTemplateUsed(response, 'accounts/profile.html')
