from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from core import models


def create_user(email="user@example.com", password="passwor2"):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_success(self):
        email = "test@example.com"
        password = "test1234!"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized(self):
        """tests if the email provided is normalized when creating a new user"""
        emails = [
            ["test1@exaMple.com", "test1@example.com"],
            ["Test2@ExaMple.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            # etc etc
        ]
        for email, expected in emails:
            user = get_user_model().objects.create_user(email, "Pa$$w0rd!")
            self.assertEqual(user.email, expected)

    def test_user_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "Pa$$w0rd!")

    def test_create_super_user(self):
        user = get_user_model().objects.create_superuser(
            "test@example.com", "Pa$$w0rd!"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe_successful(self):
        user = get_user_model().objects.create_user("test@example.com", "Pa$$w0rd!")

        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="sample recipe description",
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag_success(self):
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)

    def test_create_ingrediant_success(self):
        user = create_user()
        ingrediant = models.Ingredient.objects.create(user=user, name="Ingredient")
        self.assertEqual(str(ingrediant), ingrediant.name)

    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid_path(self, mock_uuid):
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')