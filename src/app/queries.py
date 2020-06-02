import requests
import json
import os

es_name = os.environ["ES_NAME"]
es_pass = os.environ["ES_PASS"]
es_endpoint = os.environ["ES_ENDPOINT"]


def connect(query):
    """
    Defines elasticsearch connection
    Connects to job index and search API
    
    Param query - 
    the query to be ran

    Output -
    Elasticsearch response in json format
    """
    uri = f"https://{es_name}:{es_pass}@{es_endpoint}/jobs/_search"
    headers = {"Content-Type": "application/json"}

    response = requests.get(uri, headers=headers, data=query)
    return response.json()


def reformat(response_query):
    """
    Reformats elasticsearch query to remove extra information
    """

    data = list()
    for hit in response_query["hits"]["hits"]:
        data.append(
            {
                "id": hit["_id"],
                "source_url": hit["_source"]["post_url"],
                "title": hit["_source"]["title"],
                "company": hit["_source"]["company"],
                "description": hit["_source"]["description"],
                "date_published": hit["_source"]["publication_date"],
                "location_city": hit["_source"]["location_city"],
                "location_state": hit["_source"]["location_state"],
                "geo_locat": hit["_source"]["location_point"],
            }
        )

    return {"jobs": data}


def get_all_jobs():
    """Simple Elasticsearch query that will return all jobs"""

    query = json.dumps({"query": {"match_all": {}}})

    response = connect(query)
    reformatted = reformat(response)

    return reformatted

def search_all_locations(search):
    """
    Query to use if user does not specify a location
    Does a multi_match for the search string in the 
    description and title field
    """

    query = json.dumps(
        {
            "query": {
                "multi_match": {
                    "query": search,
                    "fields": ["description", "title"]
                }
             }
        }
    )

    response = connect(query)
    reformatted = reformat(response)

    return reformatted

def search_city_state(search, city, state):
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
                    {
                    "multi_match": {
                    "query": search,
                    "fields": ["description, ", "title"]
                    }
                    }],
                "should": [
                    {
                    "match": {
                        "location_city": city
                    }
                    },
                    {
                    "match": {
                        "location_state": state
                    }
                    }
                ]
                }
            }
        }
    )

    response = connect(query)
    reformatted = reformat(response)

    return reformatted

def search_state(search, state):
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
                "fields": ["description", "title"]
                }
                }],
            "should": [
                {
                "match": {
                    "location_state": state
                }
                }
            ]
            }
        }
        }
    )

    print(query)
    response = connect(query)
    reformatted = reformat(response)

    return reformatted