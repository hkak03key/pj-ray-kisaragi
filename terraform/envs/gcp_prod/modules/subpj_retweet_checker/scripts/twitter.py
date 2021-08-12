import requests
import os
import json
from pprint import pprint

import utils
import google_cloud_platform as gcp

__all__ = [
    "collect_retweets_infos",
    "collect_target_tweets",
]

TWITTER_SECRET_ID = os.environ.get("TWITTER_SECRET_ID")
MAX_RESULTS = os.environ.get("MAX_RESULTS", 70)

USER_NAME = "yktan_xxx"


def get_twitter_secrets():
    if not "TWITTER_SECRETS" in globals():
        global TWITTER_SECRETS
        try:
            TWITTER_SECRETS = json.loads(gcp.get_secrets(TWITTER_SECRET_ID))
        except Exception as e:
            TWITTER_SECRETS = None

    return TWITTER_SECRETS


def append_retweets_infos(tweets):
    """
    Args:
        tweets ({tweet_id: date})
    Returns:
        tweets (list({
            "tweet_id": tweet_id (str),
            "tweet_date": tweet_date (str),
            "usernames": usernames (list(str))
        }))
    """
    return [
        {
            "tweet_id": tweet_id,
            "tweet_date": tweet_date,
            "usernames": collect_retweet_usernames(tweet_id)
        } for tweet_id, tweet_date in tweets.items()
    ]


def collect_retweet_usernames(tweet_id):
    res = connect_to_endpoint(
        "https://api.twitter.com/2/tweets/{}/retweeted_by".format(tweet_id)
    )
    return [u["username"] for u in res.get("data", [])]


def collect_target_tweets(pagination_token=None):
    """
    RT対象ツイートを収集する。
    後続処理におけるAPI制限のため、next_tokenも返す
    Args:
        pagination_token (str): 前回処理からの引き継ぎのためのtoken
    Returns:
        tweets ({tweet_id: tweet_created_at}): RT対象ツイート
        next_token (str): 次回処理のためのtoken
    """
    user_id = get_user_id(USER_NAME)
    params = {
            "max_results": MAX_RESULTS,
            "tweet.fields": ",".join(["created_at", "id"]),
            "start_time": "2021-07-01T00:00:00+09:00",
            #"end_time": "2021-07-11T00:00:00Z",
        }
    if pagination_token:
        params.update({"pagination_token": pagination_token})

    response = connect_to_endpoint(
            "https://api.twitter.com/2/users/{}/tweets".format(user_id),
            params
            )

    tweets = { tweet["id"]: utils.get_jst_date(tweet["created_at"]).isoformat()
        for tweet in response.get("data") if ("#ミクチャ" in tweet["text"] and "#MissBouquet" in tweet["text"])
    }
    return tweets, response.get("meta").get("next_token")


def paginate_user_tweets(user_name, params={}):
    user_id = get_user_id(user_name)
    payload = params.copy()
    if not "max_results" in params:
        payload["max_results"] = 100
    for page in pagenate_connect_to_endpoint("https://api.twitter.com/2/users/{}/tweets".format(user_id), payload):
        yield from page.get("data")


def get_user_id(user_name):
    res = connect_to_endpoint(
        "https://api.twitter.com/2/users/by/username/{}".format(user_name)
        ,{
            "user.fields": "id",
        }
    )
    return res.get("data", {}).get("id", None)


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    twitter_api_bearer_token = get_twitter_secrets()["bearer_token"]
    if not twitter_api_bearer_token:
        twitter_api_bearer_token = os.environ.get("TWITTER_API_BEARER_TOKEN")
    if not twitter_api_bearer_token:
        raise Exception("Fail to get twitter_api bearer_token")

    r.headers["Authorization"] = "Bearer {}".format(twitter_api_bearer_token)
    r.headers["User-Agent"] = "v2RetweetedByPython"
    return r


def connect_to_endpoint(url, params=None):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code, url)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def pagenate_connect_to_endpoint(url, params=None):
    payload = params
    while 1:
        response = connect_to_endpoint(url, payload)
        yield response
        next_token = response.get("meta").get("next_token")
        if not next_token:
            return
        payload['pagination_token'] = next_token


