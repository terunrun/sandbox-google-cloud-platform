from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
# @app.route("/", methods=["POST"])
def return_status_code(request):
    # req = request.json
    # status_code = req.get("status_code")
    request_json = request.get_json(silent=True)
    status_code = request_json["status_code"]
    return jsonify({"message": f"{status_code} error"}), int(status_code)

# if __name__ == "__main__":
#     app.run(debug=False, host='0.0.0.0', port=80)
