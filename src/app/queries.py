import requests 
import json
import os

es_user = os.environ["ES_USER"]
es_pass = os.environ["ES_PASS"]
es_endpoint = os.environ["ES_ENDPOINT"]

def get_all_jobs():
    """Simple Elasticsearch query that will return all jobs"""
    
    # define query
    query = json.dumps({
        "query": {
            "match_all": {}
        }
    })
    
    # define connection
    uri = f"https://{es_user}:{es_pass}@{es_endpoint}/jobs/_search"
    headers ={"Content-Type": "application/json"}

    response = requests.get(uri, headers=headers, data=query)
    response = response.json()
    
    # format response
    data = list()
    for hit in response['hits']['hits']:
        data.append({
            'id': hit['_id'], 
            'source_url' : hit['_source']['post_url'], 
            'title': hit['_source']['title'], 
            'description': hit['_source']['description'], 
            'date_published': hit['_source']['publication_date'], 
            'location_raw': hit['_source']['location_raw'], 
            'geo_locat': hit['_source']['location_point']})
    
    reformatted = {'jobs':data}
    
    return reformatted