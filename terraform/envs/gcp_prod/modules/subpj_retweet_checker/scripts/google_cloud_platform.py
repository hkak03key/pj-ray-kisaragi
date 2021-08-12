import json
import os
import re
import requests

import google.auth
from google.cloud import secretmanager_v1beta1 as secretmanager
from google.cloud import tasks_v2 as tasks
from google.protobuf import timestamp_pb2



def get_secrets(secret_id, project_id=None, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    project_id = get_project_id()
    name = client.secret_version_path(project_id, secret_id, version_id)
    response = client.access_secret_version(request={"name":name})
    ret = response.payload.data.decode("UTF-8")
    return ret


def get_secrets_json(secret_id, project_id=None, version_id="latest"):
    return json.loads(get_secrets(secret_id, project_id, version_id))


def get_project_id():
    if not "PROJECT_ID" in globals():
        global PROJECT_ID
        _, PROJECT_ID = google.auth.default()
    return PROJECT_ID


def get_service_account_email():
    if not "SERVICE_ACCOUNT_EMAIL" in globals():
        global SERVICE_ACCOUNT_EMAIL
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
            headers={"Metadata-Flavor": "Google"}
        )
        SERVICE_ACCOUNT_EMAIL = response.text

    return SERVICE_ACCOUNT_EMAIL


def get_function_region():
    if not "FUNCTION_REGION" in globals():
        global FUNCTION_REGION
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/zone",
            headers={"Metadata-Flavor": "Google"}
        )

        re_search = re.search(r"projects/(?P<project_num>[0-9]+)/zones/(?P<zone>.+)", response.text)
        zone = re_search.group("zone")

        re_search = re.search(r"^(?P<region>[a-zA-Z]+-[a-zA-Z0-9]+)", zone)
        FUNCTION_REGION = re_search.group("region")

    return FUNCTION_REGION


def get_function_name():
    if not "FUNCTION_NAME" in globals():
        global FUNCTION_NAME
        FUNCTION_NAME = os.environ.get("K_SERVICE")
        if not FUNCTION_NAME:
            FUNCTION_NAME = os.environ.get("FUNCTION_NAME")
    return FUNCTION_NAME


def get_function_url():
    if not "FUNCTION_URL" in globals():
        global FUNCTION_URL
        if os.environ.get("FUNCTION_SIGNATURE_TYPE") != "http":
            FUNCTION_URL = None
            return FUNCTION_URL

        project_id = get_project_id()
        if not project_id:
            FUNCTION_URL = None
            return FUNCTION_URL

        region = get_function_region()
        if not region:
            FUNCTION_URL = None
            return FUNCTION_URL

        function_name = get_function_name()
        if not function_name:
            FUNCTION_URL = None
            return FUNCTION_URL

        FUNCTION_URL = "https://{}-{}.cloudfunctions.net/{}".format(region, project_id, function_name)

    return FUNCTION_URL

def create_pagenate_task(target_queue_path, schedule_time_str, body={}):
    client = tasks.CloudTasksClient()

    schedule_time_pb2 = timestamp_pb2.Timestamp()
    schedule_time_pb2.FromJsonString(schedule_time_str) # FromJsonString()の戻り値はNone

    task = {
        "name": "{}/tasks/{}_paginate_{}".format(target_queue_path, get_function_name(), re.sub(r"\D", "", schedule_time_str)),
        "schedule_time": schedule_time_pb2,
        "http_request": {  # Specify the type of request.
            "http_method": "POST",
            "url": get_function_url(),
            "oidc_token": {
                "service_account_email": get_service_account_email(),
            },
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps(body).encode(),
        },
    }

    response = client.create_task(request={"parent": target_queue_path, "task": task})

    print("Created task {}".format(response.name))
    return response

