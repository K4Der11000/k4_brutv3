# Advanced URL Guessing Tool

This is a Python-based web tool for guessing URL paths using a wordlist, built with Flask.

## Features
- Insert multiple base URLs with placeholder variables like `{{var1}}`
- Paste or upload wordlists (supporting text, CSV, Excel)
- Automatic proxy rotation (basic mock implementation)
- SSE-based real-time feedback
- Download results in stylish HTML table format

## How to Run

1. Make sure Python 3 is installed.
2. Install Flask if not already installed:
   ```
   pip install flask
   ```

3. Run the script:
   ```
   python url_guesser_single_script.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Usage
- In "Base URLs", add one or more URLs with `{{var1}}` as the guessing placeholder.
- Add your wordlist (via paste, upload, or drag-drop).
- Choose proxy mode (None or Auto).
- Click â€œStart Guessingâ€ and wait for results.
- Click â€œDownload Resultsâ€ to get an HTML file with matched entries.

Enjoy!
