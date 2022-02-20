```sh
$ gcloud builds submit --tag asia.gcr.io/{PROJECT_ID}/put_to_gcs --project {PROJECT_ID}
$ gcloud run deploy put-to-gcs \
  --memory=256Mi \
  --platform managed \
  --max-instances=1 --concurrency=1 \
  --region=asia-northeast1 --no-allow-unauthenticated  \
  --image asia.gcr.io/{PROJECT_ID}/put_to_gcs \
  --project={PROJECT_ID} \
  --set-env-vars "PROJECT={PROJECT_ID}"
```

```sh
$ gcloud builds submit --tag asia.gcr.io/{PROJECT_ID}/get_from_gcs --project {PROJECT_ID}
$ gcloud run deploy get-from-gcs \
  --memory=256Mi \
  --platform managed \
  --max-instances=1 --concurrency=1 \
  --region=asia-northeast1 --no-allow-unauthenticated  \
  --image asia.gcr.io/{PROJECT_ID}/get_from_gcs \
  --project={PROJECT_ID} \
  --set-env-vars "PROJECT={PROJECT_ID}"
```

```sh
$ gcloud workflows deploy run_to_run \
 --location=us-central1 --async \
 --description="invoke two cloud run, connect both" \
 --source=./run_to_run.yaml \
 --project={PROJECT_ID}
 ```
