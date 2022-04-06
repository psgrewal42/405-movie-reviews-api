from rss_parser.models import FeedItem
import pandas as pd

def convert_feed_to_df(feed_items: []):

    feed_dict = {"title":[], "description":[]}
    for feed in feed_items:
        feed_dict["title"].append(feed.title)
        feed_dict["description"].append(feed.description)
    return pd.DataFrame(feed_dict)


