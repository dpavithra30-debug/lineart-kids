# Line Art Generator 🎨

This project generates clean black and white line art images for kids coloring books.

## Features
- AI image generation
- Convert to black & white
- Convert to SVG (vector)
- Adjustable stroke width

## How to run

1. Install dependencies:
   pip install -r requirements.txt

2. Run the app:
   python app.py

3. Open in browser:
   http://localhost:10000

## API Usage

POST /generate

Example JSON:
{
  "prompt": "cat playing drum",
  "stroke": 3,
  "background": "white"
}

## Output
- PNG file
- SVG file

## Author
Pavithra