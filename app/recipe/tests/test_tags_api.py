from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from decimal import Decimal

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


def detail_url(tag_id):
    return reverse("recipe:tag-detail", args=[tag_id])


def create_user(email="user@example.com", password="password12"):
    return get_user_model().objects.create_user(email, password)


class PublicTagsAPITests(TestCase):
    """Tests UNAUTHENTICATED endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_to_retrieve_tags(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Tests Authenticated endpoints"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retreive_tags_list_success(self):
        Tag.objects.create(user=self.user, name="Dessert")
        Tag.objects.create(user=self.user, name="Meal")

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_authenticated_user(self):
        user2 = create_user(email="user2@example.com", password="pasword2")

        Tag.objects.create(user=user2, name="Fruits")
        tag = Tag.objects.create(user=self.user, name="healthy foods")
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)
        self.assertEqual(res.data[0]["id"], tag.id)

    def test_update_tag_success(self):
        tag = Tag.objects.create(user=self.user, name="break fast")

        payload = {"name": "Dessert"}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()

        self.assertEqual(tag.name, payload["name"])

    def test_delete_tag_success(self):
        tag = Tag.objects.create(user=self.user, name="Breakfast")

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filtered_Tags_assigned_to_recipe(self):
        tag1 = Tag.objects.create(user=self.user, name="Healthy")
        tag2 = Tag.objects.create(user=self.user, name="Lunch")

        recipe1 = Recipe.objects.create(
            title="Green tea", time_minutes=10, price=Decimal("1.5"), user=self.user
        )
        recipe1.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})
        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_tags_are_unique(self):
        tag1 = Tag.objects.create(user=self.user, name="Healthy")
        Tag.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title="Green tea", time_minutes=10, price=Decimal("1.5"), user=self.user
        )
        recipe2 = Recipe.objects.create(
            title="Green tea", time_minutes=10, price=Decimal("1.5"), user=self.user
        )
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)
        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
