main.py
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def main(request):
    return jsonify({'message': '429 error'}), 429

# if __name__ == "__main__":
#     app.run(debug=False, host='0.0.0.0', port=80)
