import logging
from core.models.feed import FeedModel

# TODO Should probably figure out how to make all feeds inherit this base object at some point
class BottifyFeed:

    # Not gonna worry about every possible exception here because we can catch all of them in the worker tasks
    def __init__(self, model: FeedModel):
        self.logger = logging.getLogger(f"Bottify.Feeds.{model.feed_name}")
        self.index_name = model.index_name
        self.feed_type = model.feed_type
