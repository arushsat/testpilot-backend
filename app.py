from flask import Flask, request, jsonify
from screenshot_utils import take_screenshot_bytes, compare_images_bytes
from supabase import create_client
import os
import uuid
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables (only needed for local dev)
load_dotenv()

app = Flask(__name__)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "testpilot-images")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_image_to_supabase(image_bytes, filename):
    path = f"{filename}.png"
    supabase.storage.from_(SUPABASE_BUCKET).upload(path, image_bytes, {"content-type": "image/png", "upsert": True})
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path}"

@app.route("/save_baseline", methods=["POST"])
def save_baseline():
    data = request.get_json()
    url = data["url"]
    try:
        screenshot_bytes = take_screenshot_bytes(url)
        unique_name = f"baseline_{uuid.uuid4().hex}"
        public_url = upload_image_to_supabase(screenshot_bytes, unique_name)
        return jsonify({
            "status": "baseline_generated",
            "baseline_url": public_url
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/run_test", methods=["POST"])
def run_test():
    data = request.get_json()
    url = data.get("url")
    baseline_url = data.get("baseline_url")

    if not url or not baseline_url:
        return jsonify({"status": "error", "message": "Both 'url' and 'baseline_url' are required"}), 400

    try:
        # Download baseline image
        baseline_resp = supabase.storage.from_(SUPABASE_BUCKET).download(baseline_url.split("/")[-1])
        baseline
