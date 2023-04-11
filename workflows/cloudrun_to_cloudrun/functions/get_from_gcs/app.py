"""get file from cloud storage"""
import json
import os

from flask import Flask, request, jsonify
from google.cloud import storage

PROJECT = os.environ.get("PROJECT")
BUCKET_ID = os.environ.get("BUCKET_ID", PROJECT + "-work")

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


# https://www.python.ambitious-engineer.com/archives/1843
def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return:
    """
    for idx in range(0, len(l), n):
        # http://ailaby.com/yield/
        yield l[idx:idx + n]


# @app.route("/")
# POSTでリクエストパラメータを受け取る
# https://migratory-worker.com/archives/4607
@app.route("/", methods=["POST"])
def  get_from_gcs():
    req = request.json
    filename = req.get("filename")

    # Add log correlation to nest all log messages.
    trace_header = request.headers.get("X-Cloud-Trace-Context")
    if trace_header and PROJECT:
        trace = trace_header.split("/")
        global_log_fields[
            "logging.googleapis.com/trace"
        ] = f"projects/{PROJECT}/traces/{trace[0]}"

    bucket = storage_client.get_bucket(BUCKET_ID)

    json_file = bucket.blob(f"retrieved_json/{filename}")
    data_list = (json_file.download_as_text()).split("\n")
    target_list = []
    for data in data_list:
        if not data:
            break
        data_json = json.loads(data)
        for inv in data_json["nested_field"]:
            target_list.append(inv["nested_field_1"])
    logging("INFO", f"target_list: {target_list}")

    # write jsonlines format to /tmp/file
    result_list = list(split_list(target_list, 2))
    target_filename_base = f"{filename}_target.txt"
    file_list = []
    logging("INFO", f"splitted target_list: {result_list}")
    for i, results in enumerate(result_list):
        logging("INFO", f"splitted target_list_{i}: {result_list[i]}")
        target_filename = f"{i}_{target_filename_base}"
        with open(f"/tmp/{target_filename}", "w") as out:
            for result in results:
                out.write(f"{result}\n")
        blob = storage.Blob(f"retrieved_json/{target_filename}", bucket)
        blob.upload_from_filename(f"/tmp/{target_filename}", "txt/plain")
        file_list.append(target_filename)
        os.remove(f"/tmp/{target_filename}")

    return jsonify({"status": "ok", "filelist": f"{file_list}"})


if __name__ == "__main__":
    server_port = os.environ.get("PORT", "8080")
    app.run(debug=False, port=server_port, host="0.0.0.0")
