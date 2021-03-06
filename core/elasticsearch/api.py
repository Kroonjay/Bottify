from requests import Session
from requests.exceptions import ReadTimeout
from json.decoder import JSONDecodeError
from elasticsearch import (
    Elasticsearch,
    RequestsHttpConnection,
    TransportError,
)
from elasticsearch.helpers import streaming_bulk
import json
from typing import Dict
import logging
from core.config import settings
from core.elasticsearch.transformers import transform_monitor
from core.elasticsearch.utils import get_aws_auth

# Can't use this lib's async client until we move off AWS OpenSearch :/ Upgrading will throw UnsupportedDistributionError if we move any higher than 7.1.3
class ElasticApiHelper:
    def __init__(self):
        self.logger = logging.getLogger("Bottify.ElasticApi")
        self.host = settings.ElasticHost.host
        self.base_url = str(settings.ElasticHost)
        self.aws_access_key = settings.AwsAccessKey
        self.aws_secret_key = settings.AlertSecretKey
        self.aws_service = "es"
        self.port = 443
        self.use_ssl = True
        self.verify_certs = True
        self.max_retries = 2
        self.conn_cls = RequestsHttpConnection
        self.session = Session()
        self.client = None
        self.index_base_settings = {"number_of_shards": 1}

        aws_auth = get_aws_auth(
            self.aws_access_key, self.aws_secret_key, self.aws_service
        )
        if aws_auth:
            self.client = Elasticsearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_auth=aws_auth,
                use_ssl=self.use_ssl,
                verify_certs=self.verify_certs,
                connection_class=self.conn_cls,
            )
        else:
            self.logger.error("AWS Authentication Not Provided")

    # Need to fully deprecate this garbage
    def make_request(
        self, method: str, endpoint: str, params: Dict = None, data: Dict = None
    ):
        url = f"{self.base_url}/{endpoint}"

        headers = {"Content-Type": "application/json"}
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=30,
        )
        if not response.ok:
            self.logger.error(
                f"Make Request : Response Status Code indicates an Error : Status Code {response.status_code} : Data {response.text} Headers {response.headers}"
            )
        try:
            return response.json()
        except JSONDecodeError as jde:
            self.logger.error(f"Make Request : JSON Decode Error : {jde}")
            return None

    def get_monitor(self, monitor_id: str):
        endpoint = f"_opendistro/_alerting/monitors/{monitor_id}"
        response = self.make_request("GET", endpoint)
        if not response:
            self.logger.error(f"Get Monitor : No Response from ElasticSearch API")
            return None
        return transform_monitor(response)

    def create_index_manual(self, index_name: str, index_mappings: Dict):
        body = {}
        if isinstance(index_mappings, Dict):
            body.update({"mappings": index_mappings})

        response = self.make_request(
            method="PUT", endpoint=str(index_name), data=json.dumps(body)
        )
        if not response:
            self.logger.error("Create Index : Invalid API Response")
            return False
        return True

    def create_index(self, index_name, mappings: dict, settings: dict = None):
        index_settings = self.index_base_settings
        if settings:
            index_settings.update(settings)
        body = {"settings": index_settings}
        body.update(mappings)
        retries = 0
        if not self.client:
            self.logger.error("Create Index : ElasticSearch Client is Not Ready")
            return False

        try:
            self.client.indices.create(index=index_name, body=body)
            return True
        except TransportError as te:

            try:
                err = te.info.get("error")
            except AttributeError as ae:
                err = None
                if isinstance(te.info, ReadTimeout):
                    logging.error(f"Create Index : ReadTimeout : Retrying")
                    self.create_index(index_name, mappings, settings)
                else:
                    logging.error(f"Create Index : Unknown Error : Exiting")
                    return False
            if err:
                if err.get("type") == "resource_already_exists_exception":
                    self.logger.error(
                        f"Create Index : Failed to Create Index : Index Already Exists : Index Name {err.get('index')}"
                    )
                    return False
            self.logger.error(
                f"Create Index : Received RequestError while Creating Index : Data {te.info} \n Body {body}"
            )
            return False

    def get_index_mappings(self, index_name: str):
        endpoint = f"{index_name}/_mapping"
        response = self.make_request(method="GET", endpoint=endpoint)
        if response.get(index_name):
            return response.get(index_name).get("mappings")
        self.logger.error(f"Get Index Mappings : No Results : Index Name {index_name}")
        return None

    def index_generator(self, index_name, result_generator):
        if not self.client:
            self.logger.error("Index Generator : ElasticSearch Client is Not Ready")
            return
        for ok, action in streaming_bulk(
            client=self.client,
            index=index_name,
            actions=result_generator,
            raise_on_exception=False,  # Don???t propagate exceptions from call to bulk and just report the items that failed as failed
            raise_on_error=False,  # Don't raise BulkIndexError containing errors (as .errors) from the execution of the last chunk when some occur.
            max_retries=self.max_retries,  # maximum number of times a document will be retried when 429 is received
            initial_backoff=2,
            max_backoff=600,
            request_timeout=60,
        ):
            self.logger.debug(
                f"Index Generator : Document Indexed Successfully : Result {ok} : Action {action}"
            )
        return

    def index_one(self, index_name: str, doc_id: str, data: str):
        # if not isinstance(data, str):
        #     self.logger.error(
        #         f"Index One : Input Data Must be a JSON String : Got {type(data)}"
        #     )
        #     return
        if not self.client:
            self.logger.error("Index One : ElasticSearch Client is Not Ready")
            return
        response = self.client.index(
            index=index_name,
            id=doc_id,
            body=data,
            doc_type=None,
        )

    def get(self, index_name: str, doc_id: str):
        if not self.client:
            self.logger.error("Get : ElasticSearch Client is Not Ready")
            return
        data = self.client.get(index_name, doc_id)
        if data:
            return data["doc"]
        else:
            self.logger.error("Get: Response Returned No Document")
            return None

    def template_search(self, template_id: str, index_name: str, params: dict):
        if not isinstance(params, dict):
            self.logger.error(
                f"Template Search : Params input Must be a Dict : Got {type(params)}"
            )
            return
        body = {"id": template_id, "params": params}
        data = self.client.search_template(body, index=index_name)
        if data.get("hits"):
            return data.get("hits").get("hits")
        else:
            logging.info("Search Template : No Hits")
            return None
