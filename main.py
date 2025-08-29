# main.py
import os
from datetime import datetime

import functions_framework
import requests
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError


@functions_framework.http
def timesheet_to_gcs(request):
    """
    An HTTP-triggered Cloud Function that downloads data from a timesheet API
    and stores the response in a Google Cloud Storage bucket.

    This function expects the following environment variables to be set:
    - TIMESHEET_API_URL: The full URL of the timesheet API endpoint.
    - TIMESHEET_API_KEY: The API key for authenticating with the timesheet service.
                         (For production, it's highly recommended to use Secret Manager).
    - GCS_BUCKET_NAME: The name of the GCS bucket to store the data in.
    """
    # --- 1. Get Configuration from Environment Variables ---
    try:
        api_url = os.environ["TIMESHEET_API_URL"]
        api_key = os.environ["TIMESHEET_API_KEY"]
        bucket_name = os.environ["GCS_BUCKET_NAME"]
    except KeyError as e:
        error_message = f"Error: Missing environment variable {e}"
        print(error_message)
        return error_message, 500

    # --- 2. Download Data from Timesheet API ---
    print(f"Downloading data from timesheet API at {api_url}...")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        timesheet_data = response.text
        print("Successfully downloaded data from the timesheet API.")
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching data from timesheet API: {e}"
        print(error_message)
        return error_message, 500

    # --- 3. Upload Data to Google Cloud Storage ---
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        # Create a unique filename using a timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        destination_blob_name = f"timesheets/data_{timestamp}.json"

        blob = bucket.blob(destination_blob_name)

        print(f"Uploading data to gs://{bucket_name}/{destination_blob_name}...")
        blob.upload_from_string(timesheet_data, content_type="application/json")

        success_message = (
            f"Successfully uploaded file {destination_blob_name} to bucket {bucket_name}."
        )
        print(success_message)
        return success_message, 200

    except GoogleCloudError as e:
        error_message = f"Error uploading to Google Cloud Storage: {e}"
        print(error_message)
        return error_message, 500
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        return error_message, 500

