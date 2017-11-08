"""
Tests for listing endpoints
"""
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from ozpcenter import model_access as generic_model_access
from ozpcenter import models
from ozpcenter.scripts import sample_data_generator as data_gen
import ozpcenter.api.listing.model_access as model_access
from tests.ozpcenter.helper import validate_listing_map_keys
from tests.ozpcenter.helper import unittest_request_helper
from tests.ozpcenter.helper import ExceptionUnitTestHelper


@override_settings(ES_ENABLED=False)
class ListingApiTest(APITestCase):

    def setUp(self):
        """
        setUp is invoked before each test method
        """
        self.maxDiff = None

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data for the whole TestCase (only run once for the TestCase)
        """
        data_gen.run()

    def test_create_listing_minimal(self):
        # create a new listing with minimal data (title)
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        title = 'julias app'
        data = {'title': title, 'security_marking': 'UNCLASSIFIED'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], title)
        self.assertEqual(validate_listing_map_keys(response.data), [])
        self.assertEqual(response.data['is_bookmarked'], False)

    def test_create_listing_no_title(self):
        # create a new listing with minimal data (title)
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {'description': 'text here'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO: we have some strange inter-test dependency here. if  this test
    # doesn't run last (or after some other unknown test), it segfaults. Naming
    # the test 'test_z*' seems to make it run at the end. One could also run
    # the tests with the --reverse flag (but then you'd need to change this test
    # name to remove the _z)
    def test_z_create_listing_full(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        title = 'julias app'
        data = {
            "title": title,
            "description": "description of app",
            "launch_url": "http://www.google.com/launch",
            "version_name": "1.0.0",
            "unique_name": "org.apps.julia-one",
            "what_is_new": "nothing is new",
            "description_short": "a shorter description",
            "usage_requirements": "None",
            "system_requirements": "None",
            "is_private": "true",
            "feedback_score": 0,
            "contacts": [
                {"email": "a@a.com", "secure_phone": "111-222-3434",
                    "unsecure_phone": "444-555-4545", "name": "me",
                    "contact_type": {"name": "Government"}
                },
                {"email": "b@b.com", "secure_phone": "222-222-3333",
                    "unsecure_phone": "555-555-5555", "name": "you",
                    "contact_type": {"name": "Military"}
                }
            ],
            "security_marking": "UNCLASSIFIED",
            "listing_type": {"title": "Web Application"},
            "small_icon": {"id": 1},
            "large_icon": {"id": 2},
            "banner_icon": {"id": 3},
            "large_banner_icon": {"id": 4},
            "categories": [
                {"title": "Business"},
                {"title": "Education"}
            ],
            "owners": [
                {"user": {"username": "wsmith"}},
                {"user": {"username": "julia"}}
            ],
            "tags": [
                {"name": "demo"},
                {"name": "map"}
            ],
            "intents": [
                {"action": "/application/json/view"},
                {"action": "/application/json/edit"}
            ],
            "doc_urls": [
                {"name": "wiki", "url": "http://www.google.com/wiki"},
                {"name": "guide", "url": "http://www.google.com/guide"}
            ],
            "screenshots": [
                {"small_image": {"id": 1}, "large_image": {"id": 2}},
                {"small_image": {"id": 3}, "large_image": {"id": 4}}
            ]

        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # title
        self.assertEqual(response.data['title'], title)
        # description
        self.assertEqual(response.data['description'], 'description of app')
        # launch_url
        self.assertEqual(response.data['launch_url'],
            'http://www.google.com/launch')
        # version_name
        self.assertEqual(response.data['version_name'], '1.0.0')
        # unique_name
        self.assertEqual(response.data['unique_name'], 'org.apps.julia-one')
        # what_is_new
        self.assertEqual(response.data['what_is_new'], 'nothing is new')
        # description_short
        self.assertEqual(response.data['description_short'],
            'a shorter description')
        # usage_requirements
        self.assertEqual(response.data['usage_requirements'], 'None')
        # system_requirements
        self.assertEqual(response.data['system_requirements'], 'None')
        # is_private
        self.assertEqual(response.data['is_private'], True)
        # contacts
        self.assertEqual(len(response.data['contacts']), 2)
        names = []
        for c in response.data['contacts']:
            names.append(c['name'])
        self.assertTrue('me' in names)
        self.assertTrue('you' in names)
        # security_marking
        self.assertEqual(response.data['security_marking'], 'UNCLASSIFIED')
        # listing_type
        self.assertEqual(response.data['listing_type']['title'], 'Web Application')
        # icons
        self.assertEqual(response.data['small_icon']['id'], 1)
        self.assertEqual(response.data['large_icon']['id'], 2)
        self.assertEqual(response.data['banner_icon']['id'], 3)
        self.assertEqual(response.data['large_banner_icon']['id'], 4)
        # categories
        categories = []
        for c in response.data['categories']:
            categories.append(c['title'])
        self.assertTrue('Business' in categories)
        self.assertTrue('Education' in categories)
        # owners
        owners = []
        for o in response.data['owners']:
            owners.append(o['user']['username'])
        self.assertTrue('wsmith' in owners)
        self.assertTrue('julia' in owners)
        # tags
        tags = []
        for t in response.data['tags']:
            tags.append(t['name'])
        self.assertTrue('demo' in tags)
        self.assertTrue('map' in tags)
        # intents
        intents = []
        for i in response.data['intents']:
            intents.append(i['action'])
        self.assertTrue('/application/json/view' in intents)
        self.assertTrue('/application/json/edit' in intents)
        # doc_urls
        doc_urls = []
        for d in response.data['doc_urls']:
            doc_urls.append(d['url'])
        self.assertTrue('http://www.google.com/wiki' in doc_urls)
        self.assertTrue('http://www.google.com/guide' in doc_urls)
        # screenshots
        screenshots_small = []
        for s in response.data['screenshots']:
            screenshots_small.append(s['small_image']['id'])
        self.assertTrue(1 in screenshots_small)
        self.assertTrue(3 in screenshots_small)

        screenshots_large = []
        for s in response.data['screenshots']:
            screenshots_large.append(s['large_image']['id'])
        self.assertTrue(2 in screenshots_large)
        self.assertTrue(4 in screenshots_large)

        # fields that should come back with default values
        self.assertEqual(response.data['approved_date'], None)
        self.assertEqual(response.data['approval_status'],
            models.Listing.IN_PROGRESS)
        self.assertEqual(response.data['is_enabled'], True)
        self.assertEqual(response.data['is_featured'], False)
        self.assertEqual(response.data['avg_rate'], 0.0)
        self.assertEqual(response.data['total_votes'], 0)
        self.assertEqual(response.data['total_rate5'], 0)
        self.assertEqual(response.data['total_rate4'], 0)
        self.assertEqual(response.data['total_rate3'], 0)
        self.assertEqual(response.data['total_rate2'], 0)
        self.assertEqual(response.data['total_rate1'], 0)
        self.assertEqual(response.data['total_reviews'], 0)
        self.assertEqual(response.data['iframe_compatible'], True)
        self.assertEqual(response.data['required_listings'], None)
        self.assertTrue(response.data['edited_date'])
        self.assertEqual(validate_listing_map_keys(response.data), [])
        self.assertEqual(response.data['is_bookmarked'], False)

    def test_delete_listing(self):
        url = '/api/listing/1/'
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)
        self.assertFalse(response.data.get('is_deleted'))
        self.assertEqual(validate_listing_map_keys(response.data), [])

        url = '/api/listing/1/'
        response = unittest_request_helper(self, url, 'DELETE', username='wsmith', status_code=204)

        url = '/api/listing/1/'
        response = unittest_request_helper(self, url, 'GET', username='wsmith', status_code=200)
        self.assertTrue(response.data.get('is_deleted'))
        self.assertEqual(validate_listing_map_keys(response.data), [])

    def test_delete_listing_permission_denied(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_listing_permission_denied_2nd_party(self):
        user = generic_model_access.get_profile('johnson').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # replaced for consistent errors
        # data = response.data
        # expected_data = {'detail': 'Permission denied.', 'error': True, 'message': 'Current profile does not have delete permissions'}
        # self.assertEqual(data, expected_data)
        self.assertEqual(response.data, ExceptionUnitTestHelper.permission_denied('Current profile does not have delete permissions'))

    def test_update_listing_partial(self):
        """
        This was added to catch the case where a listing that didn't previously
        have an icon was being updated, and the update method in the serializer
        was invoking instance.small_icon.id to get the old value for the
        change_details. There was no previous value, so accessing
        instance.small_icon.id raised an exception. The same problem could exist
        on any property that isn't a simple data type
        """
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'

        listing = models.Listing.objects.get(id=1)
        listing.small_icon = None
        listing.large_icon = None
        listing.banner_icon = None
        listing.large_banner_icon = None
        listing.listing_type = None
        listing.save()

        # now make another change to the listing
        data = self.client.get(url, format='json').data
        data['small_icon'] = {'id': 1}
        data['large_icon'] = {'id': 2}
        data['banner_icon'] = {'id': 3}
        data['large_banner_icon'] = {'id': 4}
        data['listing_type'] = {'title': 'Web Application'}
        # and another update
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['edited_date'])
        self.assertEqual(response.data['small_icon']['id'], 1)
        self.assertEqual(response.data['large_icon']['id'], 2)
        self.assertEqual(response.data['banner_icon']['id'], 3)
        self.assertEqual(response.data['large_banner_icon']['id'], 4)
        self.assertEqual(response.data['is_bookmarked'], False)
        self.assertEqual(validate_listing_map_keys(response.data), [])

    def test_update_listing_full(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        title = 'julias app 2'
        data = {
            "title": title,
            "description": "description of app",
            "launch_url": "http://www.google.com/launch",
            "version_name": "2.1.8",
            "unique_name": "org.apps.julia-one",
            "what_is_new": "nothing is new",
            "description_short": "a shorter description",
            "usage_requirements": "Many new things",
            "system_requirements": "Good System",
            "is_private": "true",
            "is_enabled": "false",
            "is_featured": "false",
            "feedback_score": 0,
            "contacts": [
                {"email": "a@a.com", "secure_phone": "111-222-3434",
                    "unsecure_phone": "444-555-4545", "name": "me",
                    "contact_type": {"name": "Government"}
                },
                {"email": "b@b.com", "secure_phone": "222-222-3333",
                    "unsecure_phone": "555-555-5555", "name": "you",
                    "contact_type": {"name": "Military"}
                }
            ],
            "security_marking": "SECRET",
            "listing_type": {"title": "Widget"},
            "small_icon": {"id": 1},
            "large_icon": {"id": 2},
            "banner_icon": {"id": 3},
            "large_banner_icon": {"id": 4},
            "categories": [
                {"title": "Business"},
                {"title": "Education"}
            ],
            "owners": [
                {"user": {"username": "wsmith"}},
                {"user": {"username": "julia"}}
            ],
            "tags": [
                {"name": "demo"},
                {"name": "map"}
            ],
            "intents": [
                {"action": "/application/json/view"},
                {"action": "/application/json/edit"}
            ],
            "doc_urls": [
                {"name": "wiki", "url": "http://www.google.com/wiki2"},
                {"name": "guide", "url": "http://www.google.com/guide2"}
            ],
            "screenshots": [
                {"small_image": {"id": 1}, "large_image": {"id": 2}, "description": "Test Description"},
                {"small_image": {"id": 3}, "large_image": {"id": 4}, "description": "Test Description"}
            ]

        }
        # for checking Activity status later on
        old_listing_data = self.client.get(url, format='json').data
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # title
        self.assertEqual(response.data['title'], data['title'])
        # description
        self.assertEqual(response.data['description'], data['description'])
        # launch_url
        self.assertEqual(response.data['launch_url'], data['launch_url'])
        # version_name
        self.assertEqual(response.data['version_name'], data['version_name'])
        # unique_name
        self.assertEqual(response.data['unique_name'], data['unique_name'])
        # what_is_new
        self.assertEqual(response.data['what_is_new'], data['what_is_new'])
        # description_short
        self.assertEqual(response.data['description_short'], data['description_short'])
        # usage_requirements
        self.assertEqual(response.data['usage_requirements'], data['usage_requirements'])
        # system_requirements
        self.assertEqual(response.data['system_requirements'], data['system_requirements'])
        # is_private
        self.assertEqual(response.data['is_private'], True)
        # contacts
        self.assertEqual(len(response.data['contacts']), 2)
        names = []
        for c in response.data['contacts']:
            names.append(c['name'])
        self.assertTrue('me' in names)
        self.assertTrue('you' in names)
        # security_marking
        self.assertEqual(response.data['security_marking'],
            'SECRET')
        # listing_type
        self.assertEqual(response.data['listing_type']['title'],
            'Widget')
        # icons
        self.assertEqual(response.data['small_icon']['id'], 1)
        self.assertEqual(response.data['large_icon']['id'], 2)
        self.assertEqual(response.data['banner_icon']['id'], 3)
        self.assertEqual(response.data['large_banner_icon']['id'], 4)
        # categories
        categories = []
        for c in response.data['categories']:
            categories.append(c['title'])
        self.assertEqual(len(response.data['categories']), 2)
        self.assertTrue('Business' in categories)
        self.assertTrue('Education' in categories)
        # owners
        owners = []
        for o in response.data['owners']:
            owners.append(o['user']['username'])
        self.assertEqual(len(response.data['owners']), 2)
        self.assertTrue('wsmith' in owners)
        self.assertTrue('julia' in owners)
        # tags
        tags = []
        for t in response.data['tags']:
            tags.append(t['name'])
        self.assertEqual(len(response.data['tags']), 2)
        self.assertTrue('demo' in tags)
        self.assertTrue('map' in tags)
        # intents
        intents = []
        for i in response.data['intents']:
            intents.append(i['action'])
        self.assertEqual(len(response.data['intents']), 2)
        self.assertTrue('/application/json/view' in intents)
        self.assertTrue('/application/json/edit' in intents)
        # doc_urls
        doc_urls = []
        for d in response.data['doc_urls']:
            doc_urls.append(d['url'])
        self.assertEqual(len(response.data['doc_urls']), 2)
        self.assertTrue('http://www.google.com/wiki2' in doc_urls)
        self.assertTrue('http://www.google.com/guide2' in doc_urls)
        # screenshots
        screenshots_small = []
        self.assertEqual(len(response.data['screenshots']), 2)
        for s in response.data['screenshots']:
            screenshots_small.append(s['small_image']['id'])
        self.assertTrue(1 in screenshots_small)
        self.assertTrue(3 in screenshots_small)

        screenshots_large = []
        for s in response.data['screenshots']:
            screenshots_large.append(s['large_image']['id'])
        self.assertTrue(2 in screenshots_large)
        self.assertTrue(4 in screenshots_large)

        self.assertTrue(response.data['approved_date'])
        self.assertEqual(response.data['approval_status'], models.Listing.APPROVED)
        self.assertEqual(response.data['is_enabled'], False)
        self.assertEqual(response.data['is_featured'], False)
        self.assertEqual(response.data['avg_rate'], 3.0)
        self.assertEqual(response.data['total_votes'], 3)
        self.assertEqual(response.data['total_rate5'], 1)
        self.assertEqual(response.data['total_rate4'], 0)
        self.assertEqual(response.data['total_rate3'], 1)
        self.assertEqual(response.data['total_rate2'], 0)
        self.assertEqual(response.data['total_rate1'], 1)
        self.assertEqual(response.data['total_reviews'], 3)
        self.assertEqual(response.data['iframe_compatible'], False)
        self.assertEqual(response.data['required_listings'], None)
        self.assertTrue(response.data['edited_date'])
        self.assertEqual(validate_listing_map_keys(response.data), [])

        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #                   verify change_details
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        activity_url = url + 'activity/'
        activity_response = self.client.get(activity_url, format='json')
        activity_data = activity_response.data

        fields = ['title', 'description', 'description_short', 'version_name',
            'usage_requirements', 'system_requirements', 'unique_name', 'what_is_new', 'launch_url',
            'is_enabled', 'is_featured', 'is_private', 'feedback_score', 'doc_urls', 'contacts',
            'screenshots', 'categories', 'owners', 'tags', 'small_icon',
            'large_icon', 'banner_icon', 'large_banner_icon', 'security_marking',
            'listing_type', 'approval_status', 'intents']

        changed_found_fields = []

        for activity in activity_data:
            if activity['action'] == 'MODIFIED':
                for change in activity['change_details']:
                    # Field Set 1
                    temp_change_fields = ['title', 'description', 'description_short',
                        'version_name', 'usage_requirements', 'system_requirements', 'what_is_new', 'unique_name', 'launch_url', 'feedback_score',
                        'is_private', 'is_featured', 'listing_type', 'security_marking']

                    for temp_field in temp_change_fields:
                        if change['field_name'] == temp_field:
                            if temp_field == 'listing_type':
                                self.assertEqual(change['new_value'], data[temp_field]['title'], 'new_value assertion for {}'.format(temp_field))
                            else:
                                self.assertEqual(change['new_value'], data[temp_field], 'new_value assertion for {}'.format(temp_field))

                            if temp_field.startswith('is_'):
                                self.assertEqual(change['old_value'], model_access.bool_to_string(old_listing_data[temp_field]), 'old_value assertion for {}'.format(temp_field))
                            elif temp_field == 'listing_type':
                                self.assertEqual(change['old_value'], old_listing_data[temp_field]['title'], 'old_value assertion for {}'.format(temp_field))
                            else:
                                self.assertEqual(change['old_value'], old_listing_data[temp_field], 'old_value assertion for {}'.format(temp_field))
                            changed_found_fields.append(temp_field)

                    # Field Set 2
                    temp_change_fields = ['small_icon', 'large_icon', 'banner_icon', 'large_banner_icon']
                    for temp_field in temp_change_fields:
                        if change['field_name'] == temp_field:
                            self.assertEqual(change['new_value'], str(data[temp_field]['id']) + '.UNCLASSIFIED', 'new_value assertion for {}'.format(temp_field))
                            self.assertEqual(change['old_value'], str(old_listing_data[temp_field]['id']) + '.UNCLASSIFIED', 'old_value assertion for {}'.format(temp_field))
                            changed_found_fields.append(temp_field)

                    # Field Set 3
                    temp_change_fields = ['doc_urls', 'screenshots', 'contacts', 'intents', 'categories', 'tags', 'owners']
                    for temp_field in temp_change_fields:
                        if change['field_name'] == temp_field:
                            temp_field_function = getattr(model_access, '{}_to_string'.format(temp_field))
                            self.assertEqual(change['new_value'], temp_field_function(data[temp_field]))
                            self.assertEqual(change['old_value'], temp_field_function(old_listing_data[temp_field]))
                            changed_found_fields.append(temp_field)

        difference_in_fields = sorted(list(set(fields) - set(changed_found_fields)))  # TODO: Better way to do this
        self.assertEqual(difference_in_fields, ['approval_status', 'feedback_score', 'is_enabled', 'is_featured'])

    # TODO: def test_update_listing_full_access_control(self):

    def test_update_listing_full_2nd_party_request_user(self):
        user = generic_model_access.get_profile('johnson').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        title = 'julias app 2'
        data = {
            "title": title,
            "description": "description of app",
            "security_marking": "SECRET",
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.data
        expected_data = {'non_field_errors': ['Permissions are invalid for current profile']}

        self.assertEqual(data, expected_data)

    def test_update_listing_full_2nd_party_owner(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/'
        title = 'julias app 2'
        data = {
            "title": title,
            "description": "description of app",
            "launch_url": "http://www.google.com/launch",
            "version_name": "2.1.8",
            "unique_name": "org.apps.julia-one",
            "what_is_new": "nothing is new",
            "description_short": "a shorter description",
            "usage_requirements": "Many new things",
            "system_requirements": "Good System",
            "is_private": "true",
            "is_enabled": "false",
            "is_featured": "false",
            "feedback_score": 0,
            "contacts": [
                {"email": "a@a.com", "secure_phone": "111-222-3434",
                    "unsecure_phone": "444-555-4545", "name": "me",
                    "contact_type": {"name": "Government"}
                },
                {"email": "b@b.com", "secure_phone": "222-222-3333",
                    "unsecure_phone": "555-555-5555", "name": "you",
                    "contact_type": {"name": "Military"}
                }
            ],
            "security_marking": "SECRET",
            "listing_type": {"title": "Widget"},
            "small_icon": {"id": 1},
            "large_icon": {"id": 2},
            "banner_icon": {"id": 3},
            "large_banner_icon": {"id": 4},
            "categories": [
                {"title": "Bumake siness"},
                {"title": "Education"}
            ],
            "owners": [
                {"user": {"username": "johnson"}},
                {"user": {"username": "julia"}}
            ],
            "tags": [
                {"name": "demo"},
                {"name": "map"}
            ],
            "intents": [
                {"action": "/application/json/view"},
                {"action": "/application/json/edit"}
            ],
            "doc_urls": [
                {"name": "wiki", "url": "http://www.google.com/wiki2"},
                {"name": "guide", "url": "http://www.google.com/guide2"}
            ],
            "screenshots": [
                {"small_image": {"id": 1}, "large_image": {"id": 2}},
                {"small_image": {"id": 3}, "large_image": {"id": 4}}
            ]

        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.data
        expected_data = {'non_field_errors': ['Permissions are invalid for current owner profile']}

        self.assertEqual(data, expected_data)

    def test_z_create_update(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {
          "title": "test",
          "screenshots": [],
          "contacts": [
            {
              "name": "test1",
              "email": "test1@domain.com",
              "secure_phone": "240-544-8777",
              "contact_type": {
                "name": "Civilian"
              }
            },
            {
              "name": "test2",
              "email": "test2@domain.com",
              "secure_phone": "240-888-7477",
              "contact_type": {
                "name": "Civilian"
              }
            }
          ],
          "tags": [],
          "owners": [
            {
              "display_name": "Big Brother",
              "id": 4,
              "user": {
                "username": "bigbrother"
              }
            }
          ],
          "agency": {
            "short_name": "Miniluv",
            "title": "Ministry of Love"
          },
          "categories": [
            {
              "title": "Books and Reference"
            }
          ],
          "intents": [],
          "doc_urls": [],
          "security_marking": "UNCLASSIFIED",  # //FOR OFFICIAL USE ONLY//ABCDE
          "listing_type": {
            "title": "Web Application"
          },
          "last_activity": {
            "action": "APPROVED"
          },
          "required_listings": None
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approval_status'], 'IN_PROGRESS')
        self.assertEqual(validate_listing_map_keys(response.data), [])
        listing_id = response.data['id']

        data = {
          "id": listing_id,
          "title": "test",
          "description": None,
          "description_short": None,
          "screenshots": [],
          "contacts": [
            {
              "id": 4,
              "contact_type": {
                "name": "Government"
              },
              "secure_phone": "240-544-8777",
              "unsecure_phone": None,
              "email": "test1@domain.com",
              "name": "test15",
              "organization": None
            },
            {
              "id": 5,
              "contact_type": {
                "name": "Civilian"
              },
              "secure_phone": "240-888-7477",
              "unsecure_phone": None,
              "email": "test2@domain.com",
              "name": "test2",
              "organization": None
            }
          ],
          "avg_rate": 0,
          "total_votes": 0,
          "feedback_score": 0,
          "tags": [],
          "usage_requirements": None,
          "system_requirements": None,
          "version_name": None,
          "launch_url": None,
          "what_is_new": None,
          "owners": [
            {
              "display_name": "Big Brother",
              "id": 4,
              "user": {
                "username": "bigbrother"
              }
            }
          ],
          "agency": {
            "short_name": "Miniluv",
            "title": "Ministry of Love"
          },
          "is_enabled": True,
          "categories": [
            {
              "title": "Books and Reference"
            }
          ],
          "intents": [],
          "doc_urls": [],
          "approval_status": "IN_PROGRESS",
          "is_featured": False,
          "is_private": False,
          "security_marking": "UNCLASSIFIED//FOR OFFICIAL USE ONLY//ABCDE",
          "listing_type": {
            "title": "Web Application"
          },
          "unique_name": None,
          "last_activity": {
            "action": "APPROVED"
          },
          "required_listings": None
        }

        url = '/api/listing/{0!s}/'.format(listing_id)
        response = self.client.put(url, data, format='json')

        contacts = response.data['contacts']
        contact_types = [i['contact_type']['name'] for i in contacts]
        self.assertEqual(str(contact_types), str(['Civilian', 'Government']))
        self.assertEqual(validate_listing_map_keys(response.data), [])

    def test_update_listing_approval_status_deny_user(self):
        # a standard user cannot update the approval_status
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'

        data = {
            "title": 'mr jones app',
            "approval_status": "APPROVED",
            "security_marking": "UNCLASSIFIED"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['approval_status'], 'IN_PROGRESS')
        self.assertEqual(validate_listing_map_keys(response.data), [])

        data = response.data
        data['approval_status'] = models.Listing.APPROVED
        listing_id = data['id']

        url = '/api/listing/{0!s}/'.format(listing_id)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # double check that the status wasn't changed
        # TODO: listing doesn't exist?
        # url = '/api/listing/%s/' % listing_id
        # response = self.client.get(url, data, format='json')
        # self.assertEqual(response.data['approval_status'], models.Listing.IN_PROGRESS)

    def test_get_listings_with_query_params(self):
        """
        test_get_listings_with_query_params
        Supported query params: org (agency title), approval_status, enabled
        """
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/?approval_status=APPROVED&org=Ministry of Truth&enabled=true'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 5)
        # TODO: more tests

    def test_get_listings_with_query_params_owner(self):
        """
        test_get_listings_with_query_params
        """
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/?approval_status=APPROVED&org=Ministry of Truth&enabled=true&owners_id=4'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for listing_record in response.data:
            if 'owners' in listing_record:
                owners_list = [owner_dict['id'] for owner_dict in listing_record['owners']]
                self.assertTrue(4 in owners_list)

    def test_counts_in_listings(self):
        """
        test_counts_in_listings
        Supported query params: org (agency title), approval_status, enabled
        """
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        last_item = data[-1]

        expected_item = {"counts": {
            "APPROVED": 176,
            "APPROVED_ORG": 1,
            "DELETED": 0,
            "IN_PROGRESS": 0,
            "PENDING": 10,
            "PENDING_DELETION": 0,
            "enabled": 183,
            "REJECTED": 0,
            "organizations": {
              "1": 44,
              "2": 42,
              "3": 49,
              "4": 37,
              "5": 5,
              "6": 3,
              "7": 2,
              "8": 3,
              "9": 2
            },
            "total": 187
          }
        }
        self.assertEqual(last_item, expected_item)
    # TODO: test_counts_in_listings - 2ndparty

    def test_create_listing_with_different_agency(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {'title': 'test app', 'security_marking': 'UNCLASSIFIED',
                'agency': {'title': 'Ministry of Plenty'}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_listing_with_invalid_agency(self):
        user = generic_model_access.get_profile('julia').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/'
        data = {'title': 'test app', 'security_marking': 'UNCLASSIFIED',
            'agency': {'title': 'Ministry of NONE'}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_listing_normal_user(self):
        user = generic_model_access.get_profile('jones').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/rejection/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {'description': 'because it\'s not good'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_listing_org_steward(self):
        user = generic_model_access.get_profile('wsmith').user
        self.client.force_authenticate(user=user)
        url = '/api/listing/1/rejection/'
        data = {'description': 'because it\'s not good'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/activity/'
        response = self.client.get(url, format='json')
        actions = [i['action'] for i in response.data]
        self.assertTrue('REJECTED' in actions)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['last_activity']['action'], 'REJECTED')
        current_rejection = response.data['current_rejection']
        self.assertEqual(current_rejection['author']['user']['username'], 'wsmith')
        self.assertTrue(current_rejection['description'])
        self.assertTrue(current_rejection['author']['display_name'])

    def test_gave_single_user_feedback_listing(self):
        """
        betafish user
        """
        user = generic_model_access.get_profile('bettafish').user
        self.client.force_authenticate(user=user)

        # Create a positive feedback
        url = '/api/listing/1/feedback/'
        data = {"feedback": 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/feedback/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)
        self.assertEqual(response.data['feedback_score'], 1)

        # Login as betaraybill (no feedback given to listing #1)
        user = generic_model_access.get_profile('betaraybill').user
        self.client.force_authenticate(user=user)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 0)
        self.assertEqual(response.data['feedback_score'], 1)

    def test_gave_double_user_feedback_listing(self):
        """
        betafish user
        """
        user = generic_model_access.get_profile('bettafish').user
        self.client.force_authenticate(user=user)

        # Create a positive feedback
        url = '/api/listing/1/feedback/'
        data = {"feedback": 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/feedback/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)
        self.assertEqual(response.data['feedback_score'], 1)

        # Login as betaraybill
        user = generic_model_access.get_profile('betaraybill').user
        self.client.force_authenticate(user=user)

        # Create a negative feedback
        url = '/api/listing/1/feedback/'
        data = {"feedback": -1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/feedback/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], -1)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], -1)
        self.assertEqual(response.data['feedback_score'], 0)

    def test_feedback_score_positive_then_negative(self):
        """
        betafish user
        """
        user = generic_model_access.get_profile('bettafish').user
        self.client.force_authenticate(user=user)

        # Create a positive feedback
        url = '/api/listing/1/feedback/'
        data = {"feedback": 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/feedback/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)
        self.assertEqual(response.data['feedback_score'], 1)

        # Login as betaraybill
        user = generic_model_access.get_profile('betaraybill').user
        self.client.force_authenticate(user=user)

        # Create a negative feedback
        url = '/api/listing/1/feedback/'
        data = {"feedback": -1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/feedback/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], -1)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], -1)
        self.assertEqual(response.data['feedback_score'], 0)

        # Login as bettafish again
        user = generic_model_access.get_profile('bettafish').user
        self.client.force_authenticate(user=user)

        # Create a negative feedback
        url = '/api/listing/1/feedback/'
        data = {"feedback": -1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/feedback/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], -1)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], -1)
        self.assertEqual(response.data['feedback_score'], -2)

    def test_feedback_score_after_feedback_delete(self):
        """
        betafish user
        """
        user = generic_model_access.get_profile('bettafish').user
        self.client.force_authenticate(user=user)

        # Create a positive feedback
        url = '/api/listing/1/feedback/'
        data = {"feedback": 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = '/api/listing/1/feedback/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 1)
        self.assertEqual(response.data['feedback_score'], 1)

        url = '/api/listing/1/feedback/1/'
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = '/api/listing/1/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.data['feedback'], 0)
        self.assertEqual(response.data['feedback_score'], 0)
