```sh
gcloud functions deploy sample_429 \
  --region=$REGION --runtime python39 --max-instances=1 --memory=256MB \
   --trigger-http \
  --service-account="functions-executor@${PROJECT_ID}.iam.gserviceaccount.com" \
  --source=./functions --entry-point=main \
  --project=${PROJECT_ID} \
  --set-env-vars "PROJECT=${PROJECT_ID}"
```

```sh
gcloud workflows deploy sample_retry \
 --location=us-central1 --async \
 --description="リトライ調査用" \
 --service-account="functions-executor@${PROJECT_ID}.iam.gserviceaccount.com" \
 --source=./workflows/workflows.yaml \
 --project=${PROJECT_ID}
```
