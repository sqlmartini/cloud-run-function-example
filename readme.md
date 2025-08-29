### 1. Function Code (`main.py`)
This file fetches configuration from environment variables, calls the external API, and uploads the result to a GCS bucket.

### 2. Dependencies (`requirements.txt`)
The file `requirements.txt` should reside in the same directory as `main.py` to specify the function's dependencies.

### 3. Deployment to Cloud Run
You can deploy this function directly to Cloud Run, which will provide a scalable, serverless HTTP endpoint.

#### Prerequisites
*   Install the gcloud CLI.
*   Authenticate: `gcloud auth login`
*   Set your project: `gcloud config set project YOUR_PROJECT_ID`

#### Enable APIs
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com storage.googleapis.com
```

#### Deployment Command
Run the following command from the directory containing your main.py and requirements.txt files.

```bash
gcloud run deploy timesheet-ingest-service \
  --source . \
  --trigger-http \
  --entry-point timesheet_to_gcs \
  --runtime python312 \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --set-env-vars="TIMESHEET_API_URL=https://api.your-timesheet-app.com/v1/entries" \
  --set-env-vars="GCS_BUCKET_NAME=your-gcs-bucket-name" \
  --set-env-vars="TIMESHEET_API_KEY=your-secret-api-key"
```

### 4. Testing the Function
Once deployed, you can trigger the function by sending an HTTP POST request to its URL. You can find the URL in the output of the gcloud run deploy command.

```bash
# Get the URL of your service
SERVICE_URL=$(gcloud run services describe timesheet-ingest-service --platform managed --region YOUR_REGION --format="value(status.url)")

# Trigger the function
curl -X POST "$SERVICE_URL"
```
You should see a success message, and a new JSON file will appear in your GCS bucket. Check the logs in the Cloud Console for any errors.