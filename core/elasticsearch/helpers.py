import asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk_streaming

es = AsyncElasticsearch()


async def async_bulk_streaming_upload(feed_gen):
    mywords = ["foo", "bar", "baz"]
    for word in mywords:
        yield {
            "_index": "mywords",
            "doc": {"word": word},
        }


async def main():
    await async_bulk(es, gendata())


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
