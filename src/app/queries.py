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
    headers ={"Content-Type": "application/json"}

    response = requests.get(uri, headers=headers, data=query)
    return response.json()

def reformat(response_query):
    """
    Reformats elasticsearch query to remove extra information
    """

    data = list()
    for hit in response_query['hits']['hits']:
        data.append({
            'id': hit['_id'], 
            'source_url' : hit['_source']['post_url'], 
            'title': hit['_source']['title'], 
            'company': hit['_source']['company'],
            'description': hit['_source']['description'], 
            'date_published': hit['_source']['publication_date'], 
            'location_raw': hit['_source']['location_raw'], 
            'location_city': hit['_source']['location_city'],
            'location_state': hit['_source']['location_state'], 
            'geo_locat': hit['_source']['location_point']})
    
    return {'jobs':data}


def get_all_jobs():
    """Simple Elasticsearch query that will return all jobs"""
    
    # define query
    query = json.dumps({
        "query": {
            "match_all": {}
        }
    })
    
    response = connect(query)
    reformatted = reformat(response)
    
    return reformatted