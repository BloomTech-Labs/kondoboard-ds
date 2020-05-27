import requests 
import json
import os

es_name = os.environ["ES_NAME"]
es_pass = os.environ["ES_PASS"]
es_endpoint = os.environ["ES_ENDPOINT"]

def reformat(response_query):
    """
    reformats elasticsearch query to remove unnecessary information
    """

    data = list()
    for hit in response_query['hits']['hits']:
        data.append({
            'id': hit['_id'], 
            'source_url' : hit['_source']['post_url'], 
            'title': hit['_source']['title'], 
            'description': hit['_source']['description'], 
            'date_published': hit['_source']['publication_date'], 
            'location_raw': hit['_source']['location_raw'], 
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
    
    # define connection
    uri = f"https://{es_name}:{es_pass}@{es_endpoint}/jobs/_search"
    headers ={"Content-Type": "application/json"}

    response = requests.get(uri, headers=headers, data=query)
    response = response.json()
    
    reformatted = reformat(response)
    
    return reformatted