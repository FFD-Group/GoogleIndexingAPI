# Google Indexing API Script
This script can be run to request a list of Urls to be indexed by Google.

## Required resources

### Google API & Account Permissions
It makes use of the Google API and so an account needs setting up:
1. Go to https://console.developers.google.com/flows/enableapi?apiid=indexing.googleapis.com&credential=client_key
2. Create a new project
3. Enable API access
4. Create a service account: https://console.developers.google.com/iam-admin/serviceaccounts
5. Select project just created
6. Click "+ create service account"
7. Copy the service account ID (looks like an email address)
8. Manage keys on the service account
9. Create new JSON key (Choose the default JSON format)
10. Add the service account as an owner on the property in Google Search Console (with Owner permission)

### CSV of non-indexed Urls
Make sure you have a CSV with the headings;
`"Name";"Url";"title";"description";"Status";"DMCA";"Check type";"Creation Date";"Check Date";"Result"`
These are the Urls from a GSC export, - not all are required by the script.

Ensure each Url has the protocol and FQDN.

## Running

1. Enable/create the virtual environment;
```python
python -m venv virtualenv # create
./virtualenv/Scripts/activate # activate on Windows
source virtualenv/bin/activate # activate on Linux
```
2. Update the `URLS_TO_INDEX_FILE` with the path to your CSV file.
3. Make sure the JSON key file is passed to the FFDServiceAccount initialisation, you can use a variable for this such as `JSON_KEY_FILE_1`.
4. Run the script;
```python
python ./main.py
```

The results will be output to the console and written to the CSV file `Result` column.