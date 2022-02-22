```sh
gcloud functions deploy return_status_code \
  --region=$REGION --runtime python39 --max-instances=1 --memory=256MB \
   --trigger-http \
  --service-account="functions-executor@${PROJECT_ID}.iam.gserviceaccount.com" \
  --source=./functions --entry-point=return_status_code \
  --project=${PROJECT_ID} \
  --set-env-vars "PROJECT=${PROJECT_ID}"
```

```sh
gcloud workflows deploy {WORKFLOW_NAME} \
 --location=us-central1 --async \
 --description="リトライ調査用" \
 --service-account="functions-executor@${PROJECT_ID}.iam.gserviceaccount.com" \
 --source=./workflows/{WORKFLOW_NAME}.yaml \
 --project=${PROJECT_ID}
```
