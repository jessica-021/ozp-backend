"""
Tests for storefront endpoints
"""
from django.test import override_settings
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter.scripts import sample_data_generator as data_gen


@override_settings(ES_ENABLED=False)
class StorefrontApiTest(APITestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        self

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_metadata_authorized(self):
        url = '/api/metadata/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('agencies', response.data)
        self.assertIn('categories', response.data)
        self.assertIn('contact_types', response.data)
        self.assertIn('listing_types', response.data)
        self.assertIn('intents', response.data)

        for i in response.data['agencies']:
            self.assertTrue('listing_count' in i)

    def test_metadata_unauthorized(self):
        url = '/api/metadata/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)

    def test_storefront_authorized(self):
        url = '/api/storefront/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')

        self.assertIn('featured', response.data)
        self.assertTrue(len(response.data['featured']) >= 1)
        self.assertIn('recent', response.data)
        self.assertTrue(len(response.data['recent']) >= 1)
        self.assertIn('most_popular', response.data)
        self.assertTrue(len(response.data['most_popular']) >= 1)
        self.assertIn('recommended', response.data)
        self.assertTrue(len(response.data['recommended']) >= 1)

    def test_storefront_authorized_recommended(self):
        url = '/api/storefront/recommended/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('featured', response.data)
        self.assertEqual(response.data['featured'], [])
        self.assertIn('recent', response.data)
        self.assertEqual(response.data['recent'], [])
        self.assertIn('most_popular', response.data)
        self.assertEqual(response.data['most_popular'], [])
        self.assertIn('recommended', response.data)
        self.assertTrue(len(response.data['recommended']) >= 1)

    def test_storefront_authorized_featured(self):
        url = '/api/storefront/featured/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('featured', response.data)
        self.assertTrue(len(response.data['featured']) >= 1)
        self.assertIn('recent', response.data)
        self.assertEqual(response.data['recent'], [])
        self.assertIn('most_popular', response.data)
        self.assertEqual(response.data['most_popular'], [])
        self.assertIn('recommended', response.data)
        self.assertEqual(response.data['recommended'], [])

    def test_storefront_authorized_most_popular(self):
        url = '/api/storefront/most_popular/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('featured', response.data)
        self.assertEqual(response.data['featured'], [])
        self.assertIn('recent', response.data)
        self.assertEqual(response.data['recent'], [])
        self.assertIn('most_popular', response.data)
        self.assertTrue(len(response.data['most_popular']) >= 1)
        self.assertIn('recommended', response.data)
        self.assertEqual(response.data['recommended'], [])

    def test_storefront_authorized_recent(self):
        url = '/api/storefront/recent/'
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        response = self.client.get(url, format='json')
        self.assertIn('featured', response.data)
        self.assertEqual(response.data['featured'], [])
        self.assertIn('recent', response.data)
        self.assertTrue(len(response.data['recent']) >= 1)
        self.assertIn('most_popular', response.data)
        self.assertEqual(response.data['most_popular'], [])
        self.assertIn('recommended', response.data)
        self.assertEqual(response.data['recommended'], [])

    def test_storefront_unauthorized(self):
        url = '/api/storefront/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 401)
