from flask import Flask, request, jsonify
import base64
from io import BytesIO
from screenshot_utils import take_screenshot_bytes, compare_images_bytes

app = Flask(__name__)

@app.route("/save_baseline", methods=["POST"])
def save_baseline():
    data = request.get_json()
    url = data["url"]

    try:
        # Capture screenshot as bytes
        image_bytes = take_screenshot_bytes(url)
        # Encode to base64
        base64_str = base64.b64encode(image_bytes).decode("utf-8")
        return jsonify({
            "status": "baseline_generated",
            "baseline_image": f"data:image/png;base64,{base64_str}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/run_test", methods=["POST"])
def run_test():
    data = request.get_json()
    url = data.get("url")
    baseline_base64 = data.get("baseline_image")

    if not url or not baseline_base64:
        return jsonify({"status": "error", "message": "Both 'url' and 'baseline_image' are required"}), 400

    try:
        # Decode baseline
        baseline_bytes = base64.b64decode(baseline_base64.split(",")[-1])
        # Take new screenshot
        new_bytes = take_screenshot_bytes(url)
        # Compare
        diff_percent, diff_image_bytes = compare_images_bytes(baseline_bytes, new_bytes)

        return jsonify({
            "status": "success",
            "diff_percent": round(diff_percent, 2),
            "new_image": f"data:image/png;base64,{base64.b64encode(new_bytes).decode('utf-8')}",
            "diff_image": f"data:image/png;base64,{base64.b64encode(diff_image_bytes).decode('utf-8')}"
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

@app.route("/healthz")
def health():
    return "ok", 200
