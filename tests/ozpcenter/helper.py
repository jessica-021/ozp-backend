"""
Test Utility Helper

Function to help unit tests
"""
import os
import yaml

from rest_framework import status

from ozpcenter import model_access as generic_model_access

TEST_BASE_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'ozpcenter', 'scripts'))
TEST_DATA_PATH = os.path.join(TEST_BASE_PATH, 'test_data')


class ExceptionUnitTestHelper(object):
    """
    This class returns dictionaries of exceptions to compare with response data
    """
    @staticmethod
    def permission_denied(detailmsg=None):
        detail = detailmsg or 'You do not have permission to perform this action.'
        return {'detail': detail,
                'error': True,
                'error_code': 'permission_denied'}

    @staticmethod
    def authorization_failurexx(detailmsg=None):
        detail = detailmsg or 'Not authorized to view.'
        return {'detail': detail,
                'error': True,
                'error_code': 'authorization_failure'}

    @staticmethod
    def authorization_failure(detailmsg=None):
        detail = detailmsg or 'Authentication credentials were not provided.'
        return {'detail': detail,
                'error': True,
                'error_code': 'not_authenticated'}
        # 'error_code': 'authorization_failure'}


def _import_bookmarks(test_case_instance, username, bookmark_notification_id, status_code=201):
    user = generic_model_access.get_profile(username).user
    test_case_instance.client.force_authenticate(user=user)
    url = '/api/self/library/import_bookmarks/'
    data = {'bookmark_notification_id': bookmark_notification_id}
    response = test_case_instance.client.post(url, data, format='json')

    if response:
        if status_code == 201:
            test_case_instance.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif status_code == 400:
            test_case_instance.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            raise Exception('status code is not supported')

    return response


def _edit_listing(test_case_instance, id, input_data, default_user='bigbrother'):
    """
    Helper Method to modify a listing

    Args:
        test_case_instance
        id
        input_data
        default_user(optional)

    Return:
        response
    """
    user = generic_model_access.get_profile(default_user).user
    test_case_instance.client.force_authenticate(user=user)
    url = '/api/listing/{0!s}/'.format(id)
    # GET Listing
    data = test_case_instance.client.get(url, format='json').data

    for current_key in input_data:
        if current_key in data:
            data[current_key] = input_data[current_key]

    # PUT the Modification
    response = test_case_instance.client.put(url, data, format='json')
    test_case_instance.assertEqual(response.status_code, status.HTTP_200_OK)
    return response


def _create_create_bookmark(test_case_instance, username, listing_id, folder_name=None, status_code=200):
    """
    Create Bookmark Helper Function

    Args:
        test_case_instance
        username
        listing_id
        folder_name(optional)
        status_code

    Returns:
        response
    """
    user = generic_model_access.get_profile(username).user
    test_case_instance.client.force_authenticate(user=user)

    data = {'listing': {'id': listing_id}, 'folder': folder_name}
    url = '/api/self/library/'
    response = test_case_instance.client.post(url, data, format='json')

    if response:
        if status_code == 201:
            test_case_instance.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif status_code == 400:
            test_case_instance.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        else:
            raise Exception('status code is not supported')

    return response


def unittest_request_helper(test_case_instance, url, method, data=None, username='bigbrother', status_code=200, validator=None):
    user = generic_model_access.get_profile(username).user
    test_case_instance.client.force_authenticate(user=user)

    response = None

    if method.upper() == 'GET':
        response = test_case_instance.client.get(url, format='json')
    elif method.upper() == 'POST':
        response = test_case_instance.client.post(url, data, format='json')
    elif method.upper() == 'PUT':
        response = test_case_instance.client.put(url, data, format='json')
    elif method.upper() == 'DELETE':
        response = test_case_instance.client.delete(url, format='json')
    else:
        raise Exception('method is not supported')

    if response:
        if status_code == 200:
            test_case_instance.assertEqual(response.status_code, status.HTTP_200_OK)
        elif status_code == 201:
            test_case_instance.assertEqual(response.status_code, status.HTTP_201_CREATED)
        elif status_code == 204:
            test_case_instance.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        elif status_code == 403:
            test_case_instance.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            raise Exception('status code is not supported')

    try:
        if validator:
            validator(response.data, test_case_instance=test_case_instance)
    except Exception as err:
        # print(response.data)
        raise err

    return response


def validate_listing_map_keys_list(response_data, test_case_instance=None):
    for listing_map in response_data:
        test_case_instance.assertEqual(validate_listing_map_keys(listing_map), [])


def validate_listing_search_keys_list(response_data, test_case_instance=None):
    for listing_map in response_data['results']:
        test_case_instance.assertEqual(validate_listing_map_keys(listing_map), [])


def validate_listing_map_keys(listing_map, test_case_instance=None):
    """
    Used to validate the keys of a listing
    """
    if not isinstance(listing_map, dict):
        raise Exception('listing_map is not type dict, it is {0!s}'.format(type(listing_map)))

    listing_map_default_keys = ['id', 'is_bookmarked', 'screenshots',
                                'doc_urls', 'owners', 'categories', 'tags', 'contacts', 'intents',
                                'small_icon', 'large_icon', 'banner_icon', 'large_banner_icon',
                                'agency', 'last_activity', 'current_rejection', 'listing_type',
                                'title', 'approved_date', 'edited_date', 'description', 'launch_url',
                                'version_name', 'unique_name', 'what_is_new', 'description_short',
                                'usage_requirements', 'system_requirements', 'approval_status', 'is_enabled', 'is_featured',
                                'is_deleted', 'avg_rate', 'total_votes', 'total_rate5', 'total_rate4',
                                'total_rate3', 'total_rate2', 'total_rate1', 'total_reviews',
                                'iframe_compatible', 'security_marking', 'is_private',
                                'required_listings']

    listing_keys = [k for k, v in listing_map.items()]

    invalid_key_list = []

    for current_key in listing_map_default_keys:
        if current_key not in listing_keys:
            invalid_key_list.append(current_key)

    return invalid_key_list


class ListingFileClass(object):
    """
    Listing File

    from tests.ozpcenter.helper import ListingFile; ListingFile.filter_listings(is_enabled=True,approval_status='S')
    """

    def __init__(self, listing_file_name=None):
        self.listing_file_path = os.path.join(TEST_DATA_PATH, listing_file_name or 'listings.yaml')

    def filter_listings(self, **kwargs):
        """
        filter_listings(hello='d',hel='da')
        kwargs = {'hello': 'd', 'hel': 'da'}

        kwargs order is not guaranteed

        Does not take in account Private apps
        """
        listings_data = self.listing_records()

        listing_entries = []
        for current_listing_data in listings_data:
            current_listing = current_listing_data['listing']
            listing_activity = current_listing_data['listing_activity']

            current_listing['approval_status'] = listing_activity[-1]['action']

            accept_listing = True

            for keyword_key, keyword_value in kwargs.items():
                postfix = None
                if '__' in keyword_key:
                    keyword_key_split = keyword_key.split('__')
                    keyword_key = keyword_key_split[0]
                    postfix = keyword_key_split[1]

                # Check to see if keyword exist in lisiting
                if keyword_key in current_listing:
                    if postfix == 'in':
                        current_listing_keyword_value = current_listing[keyword_key]

                        if type(current_listing_keyword_value) is list:
                            # Case 1: When current_listing_keyword_value is a list
                            current_listing_set = set(current_listing_keyword_value)
                        else:
                            # Case 1: When current_listing_keyword_value is a string/int, convert into list, then set
                            current_listing_set = set([current_listing_keyword_value])

                        keyword_key_set = set(keyword_value)

                        if len(current_listing_set.intersection(keyword_key_set)) == 0:
                            accept_listing = False
                    else:
                        if not current_listing[keyword_key] == keyword_value:
                            accept_listing = False

                else:
                    raise Exception('Keyword {} is not in the listing'.format(keyword_key))

            if accept_listing:
                listing_entries.append(current_listing)

        return listing_entries

    def listing_records(self):
        """
        Extract Listing Records from listings.yaml
        """
        listings_data = None
        with open(self.listing_file_path, 'r') as stream:
            try:
                listings_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                raise
        return listings_data

    def listings_titles(self):
        """
        Extract Listing's titles from listing.yaml file

        Return a sorted list of titles
        """
        listings_data = self.listing_records()
        return sorted([current_record['listing']['title'] for current_record in listings_data])

    def listings_tags(self):
        """
        Extract Listing's tags from listing.yaml file

        Return a sorted list of tags
        """
        listings_data = self.listing_records()

        listing_tags = set()
        for current_listing_data in listings_data:
            current_listing = current_listing_data['listing']

            for current_tag in current_listing['tags']:
                listing_tags.add(current_tag)
        return sorted(list(listing_tags))


ListingFile = ListingFileClass()
