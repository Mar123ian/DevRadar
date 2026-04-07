from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from categories.models import Type, Technology
from services.models import Service
from accounts.models import ProgrammerUser

User = get_user_model()

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    BROKER_URL='memory://',
    DEFAULT_FROM_EMAIL='test@devradar.com'
)
class CreateServiceViewTest(TestCase):
    def setUp(self):
        self.programmer_group, _ = Group.objects.get_or_create(name='Programmers')
        self.user = ProgrammerUser.objects.create_user(
            username='create_test_programmer',
            email='create@test.com',
            password='test_password'
        )
        self.user.groups.add(self.programmer_group)
        self.client.login(username='create_test_programmer', password='test_password')
        self.type = Type.objects.create(name='Test Type')
        self.tech = Technology.objects.create(name='Python')

    def test_view_returns_200_for_programmers(self):
        response = self.client.get(reverse('create_service'))
        self.assertEqual(response.status_code, 200)

    def test_programmer_cannot_create_duplicate_services(self):
        url = reverse('create_service')
        image = SimpleUploadedFile(
            name='test.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/jpeg'
        )
        data = {
            'name': 'Duplicate Service',
            'description': 'Test Description',
            'min_price': 100,
            'max_price': 200,
            'type': self.type.pk,
            'technologies': [self.tech.pk],
            'image': image
        }
        self.client.post(url, data)
        image.seek(0)
        response = self.client.post(url, data)
        self.assertContains(response, 'Този програмист вече е предложил същата услуга!')

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    BROKER_URL='memory://',
    DEFAULT_FROM_EMAIL='test@devradar.com'
)
class UpdateServicePermissionsTest(TestCase):
    def setUp(self):
        self.programmer_group, _ = Group.objects.get_or_create(name='Programmers')
        self.owner = ProgrammerUser.objects.create_user(
            username='upd_owner', email='upd_o@test.com', password='password'
        )
        self.owner.groups.add(self.programmer_group)
        self.type = Type.objects.create(name='Update Type')
        self.service = Service.objects.create(
            name='Update Service',
            programmer=self.owner,
            type=self.type,
            min_price=100,
            max_price=200,
            slug='update-service'
        )

    def test_owner_can_access_update_page(self):
        self.client.login(username='upd_owner', password='password')
        response = self.client.get(reverse('update_service', kwargs={'service_slug': self.service.slug}))
        self.assertEqual(response.status_code, 200)

@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
    BROKER_URL='memory://',
    DEFAULT_FROM_EMAIL='test@devradar.com'
)
class DeleteServicePermissionsTest(TestCase):
    def setUp(self):
        self.programmer_group, _ = Group.objects.get_or_create(name='Programmers')
        self.owner = ProgrammerUser.objects.create_user(
            username='del_owner', email='del_o@test.com', password='password'
        )
        self.owner.groups.add(self.programmer_group)
        self.type = Type.objects.create(name='Delete Type')
        self.service = Service.objects.create(
            name='Delete Service',
            programmer=self.owner,
            type=self.type,
            min_price=100,
            max_price=200,
            slug='delete-service'
        )

    def test_owner_can_access_delete_page(self):
        self.client.login(username='del_owner', password='password')
        response = self.client.get(reverse('delete_service', kwargs={'service_slug': self.service.slug}))
        self.assertEqual(response.status_code, 200)
