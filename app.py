from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

# Initialize Flask app
app = Flask(__name__)

# Attach Prometheus metrics
metrics = PrometheusMetrics(app)

# Optional: add custom counter metric
REQUEST_COUNT = metrics.counter(
    'app_requests_total', 'Total App Requests', labels={'endpoint': lambda: 'home'}
)

@app.route("/")
def home():
      # increment custom counter
    return "DevOps Flask App Running 🚀"

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

# The /metrics endpoint is automatically added by PrometheusMetrics
# No need to manually use generate_latest()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
