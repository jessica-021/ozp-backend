"""
Elasticsearch Utils
--------------------------
Contains Elasticsearch common functions
"""
import json
import logging
import time

from django.conf import settings
from elasticsearch import Elasticsearch

# Get an instance of a logger
logger = logging.getLogger('ozp-center.' + str(__name__))


if settings.ES_ENABLED:
    kwords = {}
    kwords['hosts'] = settings.ES_HOST

    if settings.ES_BASIC_AUTH:
        kwords['http_auth'] = (settings.ES_AUTH_USERNAME, settings.ES_AUTH_PASSWORD)
    # Create ES client
    es_client = Elasticsearch(**kwords)
else:
    es_client = None


def get_mapping_setting_obj(number_of_shards=None, number_of_replicas=None):
    """
    This method creates the elasticsearch mapping object

    https://www.elastic.co/guide/en/elasticsearch/guide/current/_how_primary_and_replica_shards_interact.html
    Args:
        number_of_shards(int): Number of shards that index should to have
        number_of_replicas(int): Number of replicas that index should have

    Returns:
        mapping obj(dictionary): elasticsearch mapping object
    """
    if number_of_shards is None:
        number_of_shards = settings.ES_NUMBER_OF_SHARDS

    if number_of_replicas is None:
        number_of_replicas = settings.ES_NUMBER_OF_REPLICAS

    data = {
      "settings": {
        "number_of_shards": number_of_shards,
        "number_of_replicas": number_of_replicas,
        "analysis": {
          "filter": {
            "autocomplete_filter": {
              "type": "edge_ngram",
              "min_gram": 1,
              "max_gram": 20
            }
          },
          "analyzer": {
            "autocomplete": {
              "type": "custom",
              "tokenizer": "standard",
              "filter": [
                "lowercase",
                "autocomplete_filter"
              ]
            },
            "case_insensitive_sort": {
              "tokenizer": "keyword",
              "filter": ["lowercase"]
            }
          }
        }
      },
      "mappings": {
        "listings": {
          "dynamic": "strict",
          "properties": {
            "id": {
              "type": "long"
            },
            "title": {
              "type": "string",
              "analyzer": "autocomplete",
              "search_analyzer": "autocomplete",
              "fields": {
                  "raw": {
                      "type": "string",
                      "analyzer": "case_insensitive_sort"
                    }
                }
            },
            "agency_id": {
              "type": "long"
            },
            "agency_short_name": {
              "type": "string",
              "index": "not_analyzed"
            },
            "agency_title": {
              "type": "string"
            },
            "approval_status": {
              "type": "string"
            },
            "approved_date": {
              "type": "date",
            },
            "launch_url": {
              "type": "string"
            },
            "avg_rate": {
              "type": "double"
            },
            "categories": {
              "type": "nested",
              "properties": {
                "description": {
                  "type": "string"
                },
                "id": {
                  "type": "long"
                },
                "title": {
                  "type": "string"
                }
              }
            },
            "description": {
              "type": "string",
              "analyzer": "autocomplete",
              "search_analyzer": "autocomplete"
            },
            "description_short": {
              "type": "string",
              "analyzer": "autocomplete",
              "search_analyzer": "autocomplete"
            },
            "is_deleted": {
              "type": "boolean"
            },
            "is_enabled": {
              "type": "boolean"
            },
            "is_featured": {
              "type": "boolean"
            },
            "is_private": {
              "type": "boolean"
            },
            "listing_type_description": {
              "type": "string"
            },
            "listing_type_id": {
              "type": "long"
            },
            "listing_type_title": {
              "type": "string"
            },
            "security_marking": {
              "type": "string"
            },
            "tags": {
              "type": "nested",
              "properties": {
                "id": {
                  "type": "long"
                },
                "name": {
                  "type": "string",
                  "analyzer": "autocomplete",
                  "search_analyzer": "autocomplete"
                },
                "name_string": {
                  "type": "string"
                }
              }
            },
            "banner_icon": {
              "properties": {
                "file_extension": {
                  "type": "string"
                },
                "id": {
                  "type": "long"
                },
                "security_marking": {
                  "type": "string"
                }
              }
            },
            "large_banner_icon": {
              "properties": {
                "file_extension": {
                  "type": "string"
                },
                "id": {
                  "type": "long"
                },
                "security_marking": {
                  "type": "string"
                }
              }
            },
            "large_icon": {
              "properties": {
                "file_extension": {
                  "type": "string"
                },
                "id": {
                  "type": "long"
                },
                "security_marking": {
                  "type": "string"
                }
              }
            },
            "small_icon": {
              "properties": {
                "file_extension": {
                  "type": "string"
                },
                "id": {
                  "type": "long"
                },
                "security_marking": {
                  "type": "string"
                }
              }
            },
            "total_rate1": {
              "type": "long"
            },
            "total_rate2": {
              "type": "long"
            },
            "total_rate3": {
              "type": "long"
            },
            "total_rate4": {
              "type": "long"
            },
            "total_rate5": {
              "type": "long"
            },
            "total_reviews": {
              "type": "long"
            },
            "total_votes": {
              "type": "long"
            },
            "unique_name": {
              "type": "string"
            }
          }
        }
      }
    }
    return data


def update_es_listing(current_listing_id, record, is_new):
    """
    Args:
        is_new: backend is new
    """
    if settings.ES_ENABLED is False:
        logger.warn('Elasticsearch Service Not Enabled')
    elif not es_client.ping():
        logger.warn('Elasticsearch Service Unavailable')
        # raise errors.ElasticsearchServiceUnavailable()
    else:

        if not es_client.indices.exists(settings.ES_INDEX_NAME):
            request_body = get_mapping_setting_obj()

            logger.info("Creating '{}' index...".format(settings.ES_INDEX_NAME))
            res = es_client.indices.create(index=settings.ES_INDEX_NAME, body=request_body)
            logger.info("response: '{}'".format(res))

            # TODO: Figure out a better method to insure index is created on server than using sleep (rivera 11/14/2016)
            # Seems like there needs to be a delay if not a 503 error will happen
            time.sleep(20)

        es_record_exist = es_client.exists(
            index=settings.ES_INDEX_NAME,
            doc_type=settings.ES_TYPE_NAME,
            id=current_listing_id,
            refresh=True
        )

        record_clean_obj = prepare_clean_listing_record(record)
        if is_new is not None:
            if es_record_exist:
                es_client.update(
                    index=settings.ES_INDEX_NAME,
                    doc_type=settings.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body={"doc": record_clean_obj}
                )
            else:
                es_client.create(
                    index=settings.ES_INDEX_NAME,
                    doc_type=settings.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body=record_clean_obj
                )
        else:
            if es_record_exist:
                es_client.update(
                    index=settings.ES_INDEX_NAME,
                    doc_type=settings.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body={"doc": record_clean_obj}
                )
            else:
                # Ensure if doc exist in es, then update
                es_client.create(
                    index=settings.ES_INDEX_NAME,
                    doc_type=settings.ES_TYPE_NAME,
                    id=current_listing_id,
                    refresh=True,
                    body=record_clean_obj
                )


def encode_special_characters(user_string):
    if user_string is None:
        return ""

    sp_chars = ['+', '-', '=', '|', '<', '>', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?', ':', '\\', '/']
    # List of special characters can be found here: https://www.elastic.co/guide/en/elasticsearch/reference/2.4/query-dsl-query-string-query.html#_reserved_characters
    output_list = []

    for char in user_string:
        if char in sp_chars:
            # replace
            output_list.append(char.replace(char, '\\' + char))
        else:
            output_list.append(char)

    return "".join(output_list)


def make_search_query_obj(filter_obj, exclude_agencies=None):
    """
    Function is used to make elasticsearch query for searching

    Ordering Reference: https://www.elastic.co/guide/en/elasticsearch/reference/2.4/search-request-sort.html#_sort_order

    Args:
        filter_params(SearchParamParser): Object with search parameters
            search(str): Search Keyword
            user_offset(int): Offset
            user_limit(int): Limit
            categories([str,str,..]): List category Strings
            agencies([str,str,..]): List agencies Strings
            listing_types([str,str,..]): List listing types Strings
            minscore(float): Minscore Float
            TODO: Add Ordering


    """
    user_string = filter_obj.search_string
    user_string = encode_special_characters(user_string)

    # Pagination
    user_offset = filter_obj.offset
    user_limit = filter_obj.limit  # Size
    # user_limit_set = filter_params.get('limit_set', False)

    # Filtering
    tags = filter_obj.tags
    categories = filter_obj.categories
    agencies = filter_obj.agencies
    listing_types = filter_obj.listing_types
    # Ordering
    ordering = filter_obj.ordering

    # Boost
    boost_title = filter_obj.boost_title
    boost_description = filter_obj.boost_description
    boost_description_short = filter_obj.boost_description_short
    boost_tags = filter_obj.boost_tags

    min_score = filter_obj.min_score

    # Exclude_agencies
    exclude_agencies = exclude_agencies or []

    # Default Filter
    # Filters out listing that are not deleted, enabled, and Approved
    filter_data = [
        {
          "query": {
            "term": {
              "is_deleted": 0
            }
          }
        },
        {
          "query": {
            "term": {
              "is_enabled": 1
            }
          }
        },
        {
          "query": {
            "match": {
              "approval_status": "APPROVED"
            }
          }
        }
    ]

    # Agencies to filter
    if agencies:
        agencies_temp = []

        for agency_title in agencies:
            current_agency_data = {
                "match": {
                    "agency_short_name": agency_title
                }
            }
            agencies_temp.append(current_agency_data)

        agencies_data = {
            "query": {
                "bool": {
                    "should": agencies_temp
                    }
                }
        }

        filter_data.append(agencies_data)

    # Agencies to exclude
    if exclude_agencies:
        exclude_agencies_temp = []

        for exclude_agency_short_name in exclude_agencies:
            temp_filter = {
              "bool": {
                "filter": [
                  {
                    "match": {
                      "agency_short_name": exclude_agency_short_name
                    }
                  },
                  {
                    "match": {
                      "is_private": 1
                    }
                  }
                ]
              }
            }

            exclude_agencies_temp.append(temp_filter)

        agencies_query_data = {
            "query": {
                "bool": {
                    "must_not": exclude_agencies_temp
                }
            }
        }

        filter_data.append(agencies_query_data)

    # Listing Types to filter
    if listing_types:
        listing_types_temp = []

        for listing_type_title in listing_types:
            current_listing_type_data = {
                "match": {
                    "listing_type_title": listing_type_title
                }
            }
            listing_types_temp.append(current_listing_type_data)

        listing_type_data = {
            "query": {
                "bool": {
                    "should": listing_types_temp
                }
            }
        }
        filter_data.append(listing_type_data)

    # Tags to filter
    if tags:
        tags_temp = []

        for tag in tags:
            current_tag_data = {
                "match": {
                    "tags.name_string": tag
                }
            }
            tags_temp.append(current_tag_data)

        tags_data = {
            "nested": {
                "boost": 1,
                "path": "tags",
                "query": {
                    "bool": {
                        "should": tags_temp
                    }
                }
            }
        }

        filter_data.append(tags_data)

    # Categories to filter
    if categories:
        categories_temp = []

        for category in categories:
            current_category_data = {
                "match": {
                    "categories.title": category
                }
            }
            categories_temp.append(current_category_data)

        categories_data = {
            "nested": {
                "boost": 1,
                "path": "categories",
                "query": {
                    "bool": {
                        "should": categories_temp
                    }
                }
            }
        }

        filter_data.append(categories_data)

    temp_should = []

    if user_string:
        bt = boost_title
        bd = boost_description
        bds = boost_description_short

        temp_should.append({
            "nested": {
                "boost": boost_tags,
                "query": {
                    "query_string": {
                        "fields": [
                            "tags.name"
                        ],
                        "query": user_string
                    }
                },
                "path": "tags"
            }
        })

        temp_should.append({
           "multi_match": {
              "query": user_string,
              "type": "best_fields",
              "fields": ["title^" + str(bt), "description^" + str(bd), "description_short^" + str(bds)],
              "tie_breaker": 0.3,
              "minimum_should_match": "60%",
              "analyzer": "english",
              "fuzziness": "10"
              # fuzziness changes fixes missing first letter issue with searches (10).
           }
        })

    else:
        temp_should.append({"match_all": {}})

    search_query = {
      "size": user_limit,
      "min_score": min_score,
      "query": {
        "bool": {
          "should": temp_should,
          "filter": filter_data
        }
      }
    }

    if ordering:
        sort_list = []

        for order_item in ordering:
            order = 'asc'
            if order_item[0] == '-':
                order_item = order_item[1:]
                order = 'desc'

            # TODO: Figure out a way to get raw field dynamically
            if order_item == 'title':
                order_item = 'title.raw'
            sort_list.append({order_item: {'order': order}})

        search_query['sort'] = sort_list

    if user_offset:
        search_query['from'] = user_offset
    return search_query


def prepare_clean_listing_record(record):
    """
    Clean Record

    # Sample Record (record_json) after clean

    {
      "id": 316,
      "title": "JotSpot 28",
      "description": "Jot things down",
      "unique_name": "ozp.test.jotspot.28",
      "description_short": "Jot stuff down",
      "approval_status": "APPROVED",
      "is_enabled": true,
      "is_featured": true,
      "is_deleted": false,
      "avg_rate": 4,
      "total_votes": 1,
      "total_rate5": 0,
      "total_rate4": 1,
      "total_rate3": 0,
      "total_rate2": 0,
      "total_rate1": 0,
      "total_reviews": 1,
      "security_marking": "UNCLASSIFIED",
      "is_private": false,
      "agency": {
        "id": 1,
        "title": "Ministry of Truth",
        "short_name": "Minitrue"
      },
      "listing_type": {
        "id": 1,
        "title": "web application",
        "description": "web applications"
      },
      "categories": [
        {
          "id": 4,
          "title": "Education",
          "description": "Educational in nature"
        },
        {
          "id": 14,
          "title": "Tools",
          "description": "Tools and Utilities"
        }
      ],
      "tags": [
        {
          "id": 1,
          "name": "demo"
        }
      ]
    }

    Args:
        record: One record of ReadOnlyListingSerializer
    """
    keys_to_remove = ['contacts',
                      'last_activity',
                      'required_listings',
                      'owners',
                      'current_rejection',
                      'what_is_new',
                      'iframe_compatible',
                      'edited_date',
                      'version_name',
                      'requirements',
                      'intents']

    # Clean Record
    for key in keys_to_remove:
        if key in record:
            del record[key]

    image_keys_to_clean = ['large_icon',
                           'small_icon',
                           'banner_icon',
                           'large_banner_icon']

    # Clean Large_icon
    for image_key in image_keys_to_clean:
        if record.get(image_key):
            del record[image_key]['image_type']
            del record[image_key]['uuid']

    del record['agency']['icon']

    record_clean_obj = json.loads(json.dumps(record))

    # title_suggest = {"input": [ record_clean_obj['title'] ] }
    # record_clean_obj['title_suggest'] =title_suggest

    # Flatten Agency Obj - Makes the search query easier
    record_clean_obj['agency_id'] = record_clean_obj['agency']['id']
    record_clean_obj['agency_short_name'] = record_clean_obj['agency']['short_name']
    record_clean_obj['agency_title'] = record_clean_obj['agency']['title']
    del record_clean_obj['agency']

    # Flatten listing_type Obj - - Makes the search query easier
    record_clean_obj['listing_type_id'] = record_clean_obj['listing_type']['id']
    record_clean_obj['listing_type_description'] = record_clean_obj['listing_type']['description']
    record_clean_obj['listing_type_title'] = record_clean_obj['listing_type']['title']
    del record_clean_obj['listing_type']

    tags = []

    for tag_entry in record_clean_obj['tags']:
        tag_entry['name_string'] = tag_entry['name']
        tags.append(tag_entry)

    record_clean_obj['tags'] = tags

    return record_clean_obj
