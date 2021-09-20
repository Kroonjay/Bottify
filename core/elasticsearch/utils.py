import asyncio
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.serializer import JSONSerializer
from requests_aws4auth import AWS4Auth
import boto3
from elasticsearch.helpers import streaming_bulk
from pydantic import BaseModel
import urllib3
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from requests import Request, Session
import os


host = "search-bottify-feeds-dev-obb3hnmtwtx3fae2tmwgt56eou.us-west-2.es.amazonaws.com"  # For example, my-test-domain.us-east-1.es.amazonaws.com
region = "us-west-2"  # e.g. us-west-1

ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")
service = "es"


class PydanticEncoder(JSONSerializer):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.json()
        else:
            return JSONSerializer.default(self, obj)


# es = Elasticsearch(
#     hosts=[{"host": host, "port": 443}],
#     http_auth=awsauth,
#     use_ssl=True,
#     verify_certs=True,
#     connection_class=RequestsHttpConnection,
#     serializer=PydanticEncoder(),
# )

# document = {"title": "Moneyball", "director": "Bennett Miller", "year": "2011"}

# es.index(index="movies", doc_type="_doc", id="5", body=document)

# print(es.get(index="movies", doc_type="_doc", id="5"))

# es.bulk()


def index_feed_results(
    es,
    feed_result,
    index_name,
):
    index_name = "CurrencyInfo"
    ex.index(index=index_name, doc_type=feed_result.feed_id, id=feed_result.result_uuid)


def get_aws_auth(access_key: str, secret_key: str, service: str):
    if not access_key or not secret_key:
        print("Failed to Authenticate to AWS:Secret Key or Access Key was Not Supplied")
        return None
    credentials = boto3.Session(
        aws_access_key_id=access_key, aws_secret_access_key=secret_key
    ).get_credentials()
    return AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token,
    )


def get_elasticsearch_client():
    es_host = os.getenv("ELASTICSEARCH_HOST")
    if not es_host:
        print("Failed to Start Elasticsearch Client:Required hostname was Not Supplied")
        return None
    aws_auth = get_aws_auth("es")
    if not aws_auth:
        print("Failed to Start Elasticsearch Client:AWS Authentication Invalid")
        return None
    return Elasticsearch(
        hosts=[{"host": es_host, "port": 443}],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )


def bulk_index(result_generator, configs=None):
    print("Loading dataset...")

    if not result_generator:
        print("Bulk Index Failure:Result Generator Yields None")
        return
    client = get_elasticsearch_client()
    if not client:
        print("Bulk Index Failure:Elasticsearch Client is Invalid")
        return

    if configs:
        for ok, action in streaming_bulk(
            client=client,
            index="cmc-currencies",
            actions=result_generator(**configs),
        ):
            print(f"Document Indexed:Result: {ok}:Action: {action}")
        return
    else:
        for ok, action in streaming_bulk(
            client=client,
            index="cmc-currencies",
            actions=result_generator(),
        ):
            print(f"Document Indexed:Result: {ok}:Action: {action}")
        return
