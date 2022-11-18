from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase


class MainSetup(APITestCase):
    def test_setup(self, group='teacher', username='ksarthak4eve', email='hakunamatata'):
        self.user = get_user_model().objects.create_user(
            username,
            email,
            'password1234'
        )
        if group == 'teacher':
            Group.objects.get(name=group).user_set.add(self.user)
            self.client.user = self.user
            self.client.login(username=self.user.username, password='password1234')
            self.client.force_authenticate(user=self.user)
        return self.user
