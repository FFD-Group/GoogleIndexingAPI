import json
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from pprint import pprint
from ratelimit import limits, sleep_and_retry
import urllib.parse
import pandas as pd

SCOPES = [ "https://www.googleapis.com/auth/indexing" ]
PUBLISH_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
STATUS_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications/metadata?url="

class FFDServiceAccount:

    _json_file = ""
    _http = None
    _credentials = None
    _queue = []
    _failed = []

    def __init__(self, json_file: str):
        self._json_file = json_file
        self._create_credentials()
        self._http = self._credentials.authorize(httplib2.Http())

    def _create_credentials(self):
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(self._json_file, scopes=SCOPES)

    @sleep_and_retry
    @limits(calls=600, period=60)
    def request_index(self, url: str):
        raw_content = {'url': url, 'type': 'URL_UPDATED'}
        content = json.dumps(raw_content)

        response, content = self._http.request(PUBLISH_ENDPOINT, method="POST", body=content)

        if response.status != 200:
            failure = {
                "our_url": url,
                "response": {
                    "content": content,
                    "response": response
                }
            }
            self._failed.append(failure)

        return response.status

    @sleep_and_retry
    @limits(calls=60, period=60)
    def check_status(self, url: str):
        endpoint_url = STATUS_ENDPOINT + urllib.parse.quote_plus(url)
        response, content = self._http.request(endpoint_url, method="GET")
        return response.status


# service_account_file.json is the private key that you created for your service account.
JSON_KEY_FILE_1 = "ffd-catering-equipment-website-123114725930.json"
JSON_KEY_FILE_2 = "woven-perigee-407109-f00e542421a4.json"
JSON_KEY_FILE_3 = "ffd-gia-project-6dbe12cbd494.json"
JSON_KEY_FILE_FFD = "ffd-refrigeration-website-gia-b1338c17baf4.json"
MAX_REQUESTS_EXCLUSIVE = 401
URLS_TO_INDEX_FILE = "ffd/FFD-REF-project_links_nonindexed_39870.csv"
FAILED_URLS_LOG = "failed_urls.log"
CSV_SEPARATOR = ","

# QUERY = ""

sa = FFDServiceAccount(JSON_KEY_FILE_FFD)
dataframe = pd.read_csv(URLS_TO_INDEX_FILE, sep=CSV_SEPARATOR)

# pprint(sa.check_status(QUERY))
# pprint(sa.request_index(QUERY))

index_requests_sent = 0

for n in range(MAX_REQUESTS_EXCLUSIVE):
    if index_requests_sent > 199:
        pprint("Sent 200 index requests.")
        break
    row = dataframe.loc[n]
    status = row["Status"]
    previous_result = row["Result"]
    if previous_result != 200 and status == "Not indexed":
        url = row["Url"]
        # Check if Google has indexed since
        if sa.check_status(url) == 200:
            pprint(f"URL: {url} -> Already requested.")
            result = 200
        else: # If not then request index
            result = sa.request_index(url)
            pprint(f"URL: {url} -> {result}")
            index_requests_sent += 1
        dataframe.loc[n, "Result"] = result
        if result == 429:
            pprint("429 Too Many Requests")
            break

dataframe.to_csv(URLS_TO_INDEX_FILE, sep=CSV_SEPARATOR)

if (len(sa._failed) > 0):
    pprint(sa._failed)
    with open(FAILED_URLS_LOG, mode='a') as log:
        for failure in sa._failed:
            if failure.our_url:
                log.write(f"Url: {failure.our_url} -> {failure.response.response.status}\n")
            else:
                log.write(f"Got a bad response: {failure.response.response.status} with content: {failure.response.content}\n")

pprint(f"Total index requests sent: {index_requests_sent}.")