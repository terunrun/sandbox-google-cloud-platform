```sh
$ gcloud builds submit --tag asia.gcr.io/{PROJECT_ID}/run_sleep --project {PROJECT_ID}
$ gcloud run deploy sleep \
  --memory=256Mi \
  --platform managed \
  --max-instances=1 --concurrency=1 \
  --region=asia-northeast1 --no-allow-unauthenticated  \
  --image asia.gcr.io/{PROJECT_ID}/run_sleep \
  --project={PROJECT_ID} \
  --set-env-vars "PROJECT={PROJECT_ID}"
```

```sh
$ gcloud workflows deploy iterate_cloud_run \
 --location=asia-northeast1 --async \
 --description="iterate cloud run functions." \
 --source=./iterate_cloud_run.yaml \
 --project={PROJECT_ID}
 ```
