import requests
import json
import os
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

host = os.environ["AWS_ENDPOINT"]
region = os.environ["REGION"]

service = "es"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token,
)

es = Elasticsearch(
    hosts=[host],
    # http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)

def reformat(response_query):
    """
    Reformats elasticsearch query to remove extra information
    """

    data = list()
    for hit in response_query["hits"]["hits"][2:]:
        data.append(
            {
                "id": hit["_id"],
                "source_url": hit["_source"]["doc"]["post_url"],
                "title": hit["_source"]["doc"]["title"],
                "company": hit["_source"]["doc"]["company"],
                "description": hit["_source"]["doc"]["description"],
                "date_published": hit["_source"]["doc"]["publication_date"],
                "location_city": hit["_source"]["doc"]["location_city"],
                "location_state": hit["_source"]["doc"]["location_state"],
                "geo_locat": hit["_source"]["doc"]["location_point"],
            }
        )

    return {"jobs": data}


def get_all_jobs():
    """Simple Elasticsearch query that will return all jobs"""

    query = json.dumps({"query": {"match_all": {}}})

    response = es.search(body=query, size=50)
    reformatted = reformat(response)

    return reformatted


def search_all_locations(search, lim):
    """
    Query to use if user does not specify a location
    Does a multi_match for the search string in the 
    description and title field
    """

    query = json.dumps(
        {
            "query": {
                "multi_match": {"query": search, "fields": ["description", "title"]}
            }
        }
    )

    response = es.search(body=query, size=lim)
    reformatted = reformat(response)

    return reformatted


def search_city_state(search, city, state, lim):
    """
    Query to call if user specifies the location 
    they want to search in. 
    
    Currently using "should" clause, so the locations 
    do not HAVE to match up-
    will change this later when we get more jobs in.
    """

    query = json.dumps(
        {
            "query": {
                "bool": {
                    "must": [
                        {"multi_match": {
                                "query": search,
                                "fields": ["description, ", "title"],
                                }}
                    ],
                    "should": [
                        {"match": {"location_city": city}},
                        {"match": {"location_state": state}},
                    ],
                }
            }
        }
    )

    response = es.search(body=query, size=lim)
    reformatted = reformat(response)

    return reformatted


def search_state(search, state, lim):
    """
    Query to use if user just specifies the state
    that they want to search in
    """

    query = json.dumps(
        {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": search,
                                "fields": ["description", "title"],
                            }
                        }
                    ],
                    "should": [{"match": {"location_state": state}}],
                }
            }
        }
    )

    response = es.search(body=query, size=lim)
    reformatted = reformat(response)

    return reformatted
