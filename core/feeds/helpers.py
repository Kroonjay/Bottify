import logging


def action_wrapper(model, exclude=None, use_id=False, by_alias=False):
    if not use_id:
        return {"doc": model.json(exclude=exclude, by_alias=by_alias)}
    else:
        return {"_id": model.id, "doc": model.json(exclude=exclude, by_alias=by_alias)}


def get_elastic_property(name: str, schema_data: dict):
    if not isinstance(name, str):
        logging.error(
            f"Schema to Mappings : Input Name must be a String : Got {type(name)}"
        )
        return None
    if not isinstance(schema_data, dict):
        logging.error(
            f"Schema to Mappings : Schema Data Must be a Dictionary : Got {type(schema_data)}"
        )
        return None
    if name == "_id":
        return None  # ALways exclude _id from mappings
    schema_type = schema_data.get("type")
    if (
        not schema_type
    ):  # Null values will be returned as NoneType in model schema, all other types will be returned as strings
        return {name: {"type": "null"}}
    if schema_type == "integer":
        return {
            name: {"type": "integer"}
        }  # Not necessary but doing it for completeness
    elif schema_type == "number":
        return {
            name: {"type": "double"}
        }  # This mainly applies to decimal and condecimal types
    elif schema_type == "string":
        str_fmt = schema_data.get("format")
        if (
            not str_fmt
        ):  # Basic string fields won't have a format key, datetime, timedelta, IPAddress values will
            return {
                name: {"type": "keyword"}
            }  # Will probably need to update this for large bodies of text
        if str_fmt == "date-time":
            return {name: {"type": "date"}}
        else:
            logging.error(
                f"Schema to Mappings : Received Unsupported String Format : Schema Data {schema_data}"
            )
            return {name: {"type": "keyword"}}
    elif schema_type == "boolean":
        return "boolean"  # Once again probably not necessary but w/e
    elif schema_type == "array":
        # return {name: {"type": "text"}}
        return {
            name: {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            }
        }
    else:
        logging.error(
            f"Schema to Mappings : Received Unsupported Schema Type : Schema Type {schema_type} : Schema Data {schema_data}"
        )
        return None


def get_mappings(feed):
    if not feed.result_model:
        logging.error(f"Set Mappings : Feed's Result Model is None : Feed ID {feed.id}")
        return None
    es_properties = {}
    for name, data in feed.result_model.schema().get("properties").items():
        es_prop = get_elastic_property(name, data)
        if not es_prop:
            continue
        es_properties.update(es_prop)
    if not es_properties:
        logging.error(
            f"Get Mappings : Failed to Map Any Properties from Result Model Schema : Feed ID {feed.id}"
        )
        return None
    return {"mappings": {"properties": es_properties}}
