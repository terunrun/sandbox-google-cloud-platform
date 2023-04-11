import json
import os
import time

from flask import Flask, request, jsonify

PROJECT = os.environ.get("PROJECT")

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


@app.route("/", methods=["POST"])
def sleep():
    req = request.json
    coefficient = req.get("coefficient")

    # Add log correlation to nest all log messages.
    trace_header = request.headers.get("X-Cloud-Trace-Context")
    if trace_header and PROJECT:
        trace = trace_header.split("/")
        global_log_fields[
            "logging.googleapis.com/trace"
        ] = f"projects/{PROJECT}/traces/{trace[0]}"

    # https://techacademy.jp/magazine/15822
    wait_seconds = 60 * coefficient
    logging("INFO", f"start waiting for {wait_seconds}...")
    time.sleep(wait_seconds)
    logging("INFO", f"{wait_seconds} elapsed.")

    return jsonify({"status": "ok"})


if __name__ == "__main__":
    server_port = os.environ.get("PORT", "8080")
    app.run(debug=False, port=server_port, host="0.0.0.0")
