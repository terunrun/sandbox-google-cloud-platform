"""put file to cloud storage"""
import datetime
import json
import os

from flask import Flask, request, jsonify
from google.cloud import storage

PROJECT = os.environ.get("PROJECT")
BUCKET_ID = os.environ.get("BUCKET_ID", PROJECT + "-work")

TARGET_LIST = [
    {"field_1": "10001-001", "field_2": "Test Data 01", "nested_field": [{"nested_field_1": "90001-001", "nested_field_2": 12345, "nested_field_3": 67890.01, "nested_field_4": "2022-01-01", "nested_field_5": True}]}, 
    {"field_1": "20001-001", "field_2": "Test Data 02", "nested_field": [{"nested_field_1": "80001-001", "nested_field_2": 98765, "nested_field_3": 43219.02, "nested_field_4": "2022-02-01", "nested_field_5": False}, {"nested_field_1": "70001-001", "nested_field_2": 11111, "nested_field_3": 22222.01, "nested_field_4": "2022-02-02", "nested_field_5": False}, {"nested_field_1": "60001-001", "nested_field_2": 33333, "nested_field_3": 44444.01, "nested_field_4": "2022-02-03", "nested_field_5": False}]}
]

storage_client = storage.Client()

# Build structured log messages as an object.
global_log_fields = {}

app = Flask(__name__)


def logging(logLevel, msg):
    entry = dict(
        severity=logLevel,
        message=msg,
        # Log viewer accesses 'component' as jsonPayload.component'.
        component="arbitrary-property",
        **global_log_fields,
    )
    print(json.dumps(entry))


@app.route("/")
def put_to_gcs():
    dt_now_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    date = dt_now_jst.strftime('%Y%m%d%H%M%S')

    # Add log correlation to nest all log messages.
    trace_header = request.headers.get("X-Cloud-Trace-Context")
    if trace_header and PROJECT:
        trace = trace_header.split("/")
        global_log_fields[
            "logging.googleapis.com/trace"
        ] = f"projects/{PROJECT}/traces/{trace[0]}"

    bucket = storage_client.get_bucket(BUCKET_ID)
    filename = f"sample_{date}.json"

    # write jsonlines format to /tmp/file
    with open(f"/tmp/{filename}", "w") as out:
        for target in TARGET_LIST:
            json.dump(target, out)
            out.write("\n")
    blob = storage.Blob(f"retrieved_json/{filename}", bucket)
    blob.upload_from_filename(f"/tmp/{filename}", "application/json")
    os.remove(f"/tmp/{filename}")

    return jsonify({"status": "ok", "bucket": BUCKET_ID, "filename": filename})


if __name__ == "__main__":
    server_port = os.environ.get("PORT", "8080")
    app.run(debug=False, port=server_port, host="0.0.0.0")
