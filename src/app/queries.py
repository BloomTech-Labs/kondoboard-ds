import requests
import logging
import json
import os
import boto3
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(name)s:%(message)s")

host = os.environ["AWS_ENDPOINT"]
region = os.environ["REGION"]
service = "es"


# There are two connection methods for connecting to the elasticsearch database
# 1. Running live inside aws elastic beanstalk 
#   - credentials are handled via instance roles attached to the ec2 instance
# 2. Running local for testing and development
#   - credentials are handled via a token system with expiration, verified with your 
#   - individual access_key and secret_key configured through the awsebcli
# assure the appropriate connection method is uncommented 


# *************************************************
# 1. Running live inside aws elastic beanstalk

# Elasticsearch connection method 1 BEGIN
class AssumeRoleAWS4Auth(AWS4Auth):
    """
    Subclass of AWS4Auth which accepts botocore credentials as its first argument
    Which allows us to handle assumed role sessions transparently
    """
    def __init__(self, credentials, region, service, **kwargs):
        self.credentials = credentials

        frozen_credentials = self.get_credentials()

        super(AssumeRoleAWS4Auth, self).__init__(
            frozen_credentials.access_key,
            frozen_credentials.secret_key,
            region,
            service,
            session_token=frozen_credentials.token,
            **kwargs
        )

    def get_credentials(self):
        if hasattr(self.credentials, 'get_frozen_credentials'):
            return self.credentials.get_frozen_credentials()
        return self.credentials

    def __call__(self, req):
        if hasattr(self.credentials, 'refresh_needed') and self.credentials.refresh_needed():

            frozen_credentials = self.get_credentials()

            self.access_id = frozen_credentials.access_key
            self.session_token = frozen_credentials.token
            self.regenerate_signing_key(secret_key=frozen_credentials.secret_key)
        return super(AssumeRoleAWS4Auth, self).__call__(req)

    def handle_date_mismatch(self, req):
        req_datetime = self.get_request_date(req)
        new_key_date = req_datetime.strftime('%Y%m%d')

        frozen_credentials = self.get_credentials()

        self.access_id = frozen_credentials.access_key
        self.session_token = frozen_credentials.token
        self.regenerate_signing_key(
            date=new_key_date,
            secret_key=frozen_credentials.secret_key
        )


session = boto3.Session()
credentials = session.get_credentials()
awsauth = AssumeRoleAWS4Auth(credentials, region, service)

es = Elasticsearch(
    hosts=[host],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)
# Elasticsearch connection method 1 END


# *************************************************
# 2. Running local for testing and development

# Elasticsearch connection method 2 BEGIN 
# credentials = boto3.Session().get_credentials()
# awsauth = AWS4Auth(
#     credentials.access_key,
#     credentials.secret_key,
#     region,
#     service,
#     session_token=credentials.token,
# )

# es = Elasticsearch(
#     hosts=[host],
#     http_auth=awsauth,
#     use_ssl=True,
#     verify_certs=True,
#     connection_class=RequestsHttpConnection,
# )
# Elasticsearch connection method 2 END


def logging_response(response):
    """
    Takes in a response object returned from elasticsearch,
    logs results based on that object like:
    Number of ES hits
    Number of returned responses
    """
    logging.info(f"Total number of ES hits: {response['hits']['total']['value']}")
    if len(response["hits"]["hits"]) == 0:
        logging.error("There are zero returned matches")
    else:
        logging.info(
            f"Total number of returned responses: {len(response['hits']['hits'])}"
        )


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

    logging.info(f"Reformatted {len(data)} returned responses")

    return {"jobs": data}


def get_all_jobs():
    """Simple Elasticsearch query that will return all jobs"""

    logging.info("=" * 50)
    logging.info("Grabbing all jobs:")

    query = json.dumps({"query": {"match_all": {}}})

    response = es.search(body=query, index="jobs")

    logging_response(response)

    return reformat(response)


def search_all_locations(search):
    """
    Query to use if user does not specify a location
    Does a multi_match for the search string in the 
    description and title field 
    Penalizes any positions with senior, master, and lead 
    in the title
    """

    logging.info("=" * 50)
    logging.info("Searching through all locations:")

    query = json.dumps(
        {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": search,
                                "fields": ["description", "title", "tags"],
                            }
                        },
                        {
                            "bool": {
                                "must_not": {"match": {"title": "senior master lead"}}
                            }
                        },
                    ]
                }
            }
        }
    )

    response = es.search(index="jobs", body=query)

    logging_response(response)

    return reformat(response)


def search_city_state(search, city, state):
    """
    Query to call if user specifies the location 
    they want to search in. 
    
    Job posting MUST match the location, and then
    its relevancy score is increased as more search
    terms are in the description, title, or tags. 

    Job postings are penalized if they have lead, master,
    or senior in the title.
    """

    logging.info("=" * 50)
    logging.info(f"Searching through {city} city and {state} state:")

    query = json.dumps(
        {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"location_city": city.title()}},
                        {"match": {"location_state": state.title()}},
                    ],
                    "should": [
                        {
                            "multi_match": {
                                "query": search,
                                "fields": ["description", "title", "tags"],
                            }
                        },
                        {
                            "bool": {
                                "must_not": {"match": {"title": "senior master lead"}}
                            }
                        },
                    ],
                }
            }
        }
    )

    response = es.search(index="jobs", body=query)

    logging_response(response)

    return reformat(response)


def search_state(search, state):
    """
    Query to use if user just specifies the state
    that they want to search in
    """

    logging.info("=" * 50)
    logging.info(f"Searching through {state} state:")

    query = json.dumps(
        {
            "query": {
                "bool": {
                    "must": [{"match": {"location_state": state.title()}}],
                    "should": [
                        {
                            "multi_match": {
                                "query": search,
                                "fields": ["description", "title", "tags"],
                            }
                        },
                        {
                            "bool": {
                                "must_not": {"match": {"title": "senior master lead"}}
                            }
                        },
                    ],
                }
            }
        }
    )

    response = es.search(index="jobs", body=query)

    logging_response(response)

    return reformat(response)
