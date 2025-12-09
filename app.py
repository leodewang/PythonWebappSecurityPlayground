
from flask import Flask, jsonify
import os

# Create a Flask application object. This is the core "app".
app = Flask(__name__)

@app.route("/healthz")
def healthz():
    return jsonify(status="ok")

@app.route("/version")
def version():
    # We'll use this later to demonstrate env vars and deployments
    return jsonify(version=os.getenv("APP_VERSION", "0.1.0"))

@app.route("/")
def root():
    return jsonify(message="Hello from AKS demo app")

if __name__ == "__main__":
    # 0.0.0.0 so it’s reachable from outside the container
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
