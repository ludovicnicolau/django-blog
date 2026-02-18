from django.test import TestCase

from blog.factories import UserFactory

class CustomUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_user = UserFactory(is_active=True)
        cls.inactive_user = UserFactory(is_active=False)
    
    def test_get_absolute_url_active_user(self):
        url = self.active_user.get_absolute_url()
        self.assertEqual(url, f'/users/profile/{self.active_user.username}/')

    def test_get_absolute_url_inactive_user(self):
        url = self.inactive_user.get_absolute_url()
        self.assertEqual(url, '/users/deleted-user/')