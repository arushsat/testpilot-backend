from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
from io import BytesIO
import numpy as np

def take_screenshot_bytes(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        screenshot = page.screenshot(full_page=True)
        browser.close()
        return screenshot

def compare_images_bytes(baseline_bytes, new_bytes):
    baseline_img = Image.open(BytesIO(baseline_bytes)).convert("RGB")
    new_img = Image.open(BytesIO(new_bytes)).convert("RGB")

    if baseline_img.size != new_img.size:
        new_img = new_img.resize(baseline_img.size)

    diff = ImageChops.difference(baseline_img, new_img)
    diff_np = np.array(diff)
    non_zero = np.count_nonzero(diff_np)
    total = diff_np.size
    diff_percent = (non_zero / total) * 100

    red_overlay = Image.new("RGB", baseline_img.size, (255, 0, 0))
    mask = diff.convert("L").point(lambda x: 255 if x > 10 else 0)
    diff_image = Image.composite(red_overlay, new_img, mask)

    output = BytesIO()
    diff_image.save(output, format="PNG")
    return diff_percent, output.getvalue()
