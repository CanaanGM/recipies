from decimal import Decimal



from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """creates and return a recipe details URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])
    
def create_recipe(user, **params):
    defaults = {
        'title':'sample title',
        'time_minutes':22,
        'price':Decimal('5.25'),
        'description':'sample description',
        'link':'http://sample.com/what.pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

def create_user(**params):
    """creates and returns a new user"""
    return get_user_model().objects.create_user(**params)
     
class PublicRecipeAPITests(TestCase):
    """Unauthenticated tests"""

    def setUp(self):
        self.client = APIClient()

    def test_uth_required_to_call_api(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPITests(TestCase):
    """Authenticated tests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='iIzPassword')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe_success(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recpies = Recipe.objects.all().order_by('-id') # will fail if UUID/GUID
        serializer = RecipeSerializer(recpies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_recipe_list_limited_to_user(self):
        """authenticated user only recipes"""
        other_user =  create_user(email='notme@example.com', password ='password!2')
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes= Recipe.objects.filter(user=self.user)
        serilizer= RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code , status.HTTP_200_OK)
        self.assertEqual(res.data, serilizer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_Create_recipe_success(self):
        payload = {
            'title':'sample recipe',
            'time_minutes':30,
            'price':Decimal('5.99')
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe= Recipe.objects.get(id=res.data['id'])

        for key,value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_success(self):
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user = self.user,
            title= 'sample test',
            link=original_link
        )
        payload = {'title':'new sample title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        self.assertEqual(recipe.title,payload['title'] )
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_success(self):
        recipe = create_recipe(
            user =self.user,
            title = 'im bored, it"s time for you to die!',
            link="Lord slug movie",
            description ="lord slugs gonna get it !"
        )

        payload= { 
            "title": "berserk goku",
            'link':'ohShit.png',
            'description':'u done goofed',
            'price': Decimal('43.49'),
            'time_minutes':1
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for key,value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)


    def test_update_user_returns_error(self):
        """tests changing the user on a recipe error"""
        new_user = create_user(email='user2@example.com', password='dark shcnider')
        recipe = create_recipe(self.user)

        payload={'user':new_user.id}
        url = detail_url(recipe.id)

        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_selete_recipe_success(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())


    def test_delete_recipe_for_other_users_error(self):
        new_user= create_user(email="acnologia@example.com", password='strongest')
        recipe = create_recipe(user= new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id = recipe.id).exists())

    def test_create_recipe_with_new_tag_success(self):
        payload = {
            'title':'meat',
            'time_minutes':40,
            'price':Decimal('9.8'),
            'tags':[{'name':'meat'}, {'name':'Dinner'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user= self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        tag_meat = Tag.objects.create(user=self.user, name='meat')
        payload={
            'title':' Meat',
            'time_minutes':20,
            'price':Decimal('4.5'),
            'tags':[{'name':'meat'}, {'name':"vigges"}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipies = Recipe.objects.filter(user=self.user)
        recipe = recipies[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_meat, recipe.tags.all())

        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """tests creating a tag when updating a recipe"""
        recipe = create_recipe(user=self.user)

        payload = {
            'tags':[{'name':'Lunch'}]
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code , status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name=payload['tags'][0]['name'])
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_existing_tag(self):
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {
            'tags':[{'name':'Lunch'}]
        }

        url = detail_url(recipe.id)
        res = self.client.patch(url , payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())


    def test_clear_recipe_tags(self):
        tag = Tag.objects.create(user=self.user, name = 'Dessert')
        recipe = create_recipe(user = self.user)
        recipe.tags.add(tag)

        payload = {'tags':[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url , payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)