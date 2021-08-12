from flask import escape

from datetime import datetime, timedelta, timezone
import json
import os
from pprint import pprint

import twitter as t
import google_spread_sheet as gsht
import google_cloud_platform as gcp


PAGINATE_QUEUE_PATH = os.environ.get("PAGINATE_QUEUE_PATH")


def proc(twitter_pagination_token=None):
    tweets, twitter_next_token = t.collect_target_tweets(twitter_pagination_token)
    tweets = t.append_retweets_infos(tweets)

    is_new = False
    is_final = False
    if not twitter_pagination_token:
        # 初回
        is_new = True
    if not twitter_next_token:
        # 継続処理がない
        is_final = True

    gsht.edit_spreadsheet(tweets, is_new, is_final)

    print("twitter_next_token:", twitter_next_token)
    if not is_final:
        gcp.create_pagenate_task(
            PAGINATE_QUEUE_PATH,
            (datetime.now(timezone.utc) + timedelta(minutes=16)).isoformat(),
            {"twitter_pagination_token": twitter_next_token}
        )

    
    return {
        "status": "finish" if is_final else "continue",
    }


def call_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "twitter_pagination_token" in request_json:
        twitter_pagination_token = request_json["twitter_pagination_token"]
    elif request_args and "twitter_pagination_token" in request_args:
        twitter_pagination_token = request_args["twitter_pagination_token"]
    else:
        twitter_pagination_token = None

    return json.dumps(proc(twitter_pagination_token))


if __name__ == "__main__":
    proc()

