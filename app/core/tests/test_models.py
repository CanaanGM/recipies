
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    def test_create_user_with_email_success(self):
        email = 'test@example.com'
        password = 'test1234!'
        user = get_user_model().objects.create_user(
            email=email,password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized(self):
        """tests if the email provided is normalized when creating a new user"""
        emails = [
            ['test1@exaMple.com','test1@example.com'],
            ['Test2@ExaMple.com','Test2@example.com'],
            ['TEST3@EXAMPLE.COM','TEST3@example.com'],
            # etc etc
        ]
        for email, expected in emails:
            user = get_user_model().objects.create_user(email, 'Pa$$w0rd!')
            self.assertEqual(user.email, expected)

    def test_user_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('',  'Pa$$w0rd!')

    def test_create_super_user(self):
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'Pa$$w0rd!'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)