from flask import Flask, request, jsonify, send_file
import os, uuid
from PIL import Image
import cairosvg
import subprocess
import requests

app = Flask(__name__)
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OPENAI_API_KEY = "YOUR_API_KEY"

# -------- AI IMAGE GENERATION --------
def generate_ai_image(prompt, filename):
    url = "https://api.openai.com/v1/images/generations"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    data = {
        "prompt": f"""
Simple clean black and white coloring book line art.
Bold smooth outlines, no shading, no grayscale, no color fill.
Minimal details, big open spaces for coloring.
Centered composition.

Subject: {prompt}
""",
        "size": "1024x1024"
    }

    response = requests.post(url, headers=headers, json=data)
    image_url = response.json()['data'][0]['url']

    img_data = requests.get(image_url).content
    png_path = f"{OUTPUT_FOLDER}/{filename}_ai.png"

    with open(png_path, 'wb') as f:
        f.write(img_data)

    return png_path

# -------- CONVERT TO BLACK & WHITE --------
def convert_to_bw(input_path, output_path):
    img = Image.open(input_path).convert("L")
    img = img.point(lambda x: 0 if x < 200 else 255)
    img.save(output_path)

# -------- VECTORIZE USING POTRACE --------
def convert_to_svg(bw_path, svg_path):
    pbm_path = bw_path.replace(".png", ".pbm")
    Image.open(bw_path).save(pbm_path)
    subprocess.run(["potrace", pbm_path, "-s", "-o", svg_path])

# -------- APPLY STROKE --------
def apply_stroke(svg_path, stroke):
    with open(svg_path, "r") as f:
        content = f.read()

    content = content.replace('fill="black"', 'fill="none" stroke="black"')
    content = content.replace(
        '<path',
        f'<path stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"'
    )

    with open(svg_path, "w") as f:
        f.write(content)

# -------- MAIN API --------
@app.route('/generate', methods=['POST'])
def generate():
    data = request.json

    prompt = data.get("prompt")
    stroke = float(data.get("stroke", 3))
    background = data.get("background", "white")

    file_id = str(uuid.uuid4())

    # Step 1: AI Image
    ai_image = generate_ai_image(prompt, file_id)

    # Step 2: Convert to B/W
    bw_image = f"{OUTPUT_FOLDER}/{file_id}_bw.png"
    convert_to_bw(ai_image, bw_image)

    # Step 3: Convert to SVG
    svg_path = f"{OUTPUT_FOLDER}/{file_id}.svg"
    convert_to_svg(bw_image, svg_path)

    # Step 4: Apply stroke
    apply_stroke(svg_path, stroke)

    # Step 5: Export PNG
    png_path = f"{OUTPUT_FOLDER}/{file_id}.png"
    cairosvg.svg2png(
        url=svg_path,
        write_to=png_path,
        background_color=background if background == "white" else None
    )

    return jsonify({
        "png": f"/download/{file_id}.png",
        "svg": f"/download/{file_id}.svg"
    })

@app.route('/download/<path:filename>')
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)