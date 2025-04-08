from flask import Flask, render_template, request, redirect, send_from_directory
import time
import threading
import os

app = Flask(__name__)

# Global Variables
guesses = []
proxies = []
results = []
is_guessing_paused = False
current_guess_index = 0
remaining_guess_time = 0
guess_timer_thread = None

# Helper Functions
def start_guess_timer(duration_in_seconds):
    global remaining_guess_time
    remaining_guess_time = duration_in_seconds
    while remaining_guess_time > 0:
        if is_guessing_paused:
            break
        time.sleep(1)
        remaining_guess_time -= 1

@app.route("/", methods=["GET", "POST"])
def index():
    global guesses, proxies, current_guess_index, is_guessing_paused, results, guess_timer_thread

    if request.method == "POST":
        if "start" in request.form:
            # Start guessing
            guesses = request.form["guess_list"].splitlines()
            proxies = request.form["proxy_list"].splitlines()
            results = []
            current_guess_index = 0
            is_guessing_paused = False

            # Start guess timer
            guess_count = len(guesses)
            estimated_time = guess_count * 0.3  # Estimate time (in seconds)
            guess_timer_thread = threading.Thread(target=start_guess_timer, args=(estimated_time,))
            guess_timer_thread.start()

            # Start guessing loop
            threading.Thread(target=start_guess_loop).start()

        elif "pause_resume" in request.form:
            # Pause/Resume guessing
            is_guessing_paused = not is_guessing_paused

        elif "save" in request.form:
            # Save results
            save_results()
            return redirect(url_for('download_results'))

        return redirect(url_for("index"))

    return render_template("index.html", guesses=guesses, proxies=proxies, results=results, 
                           remaining_guess_time=remaining_guess_time)

def start_guess_loop():
    global current_guess_index, results, guesses, proxies
    while current_guess_index < len(guesses):
        if is_guessing_paused:
            break
        guess = guesses[current_guess_index]
        proxy = proxies[current_guess_index % len(proxies)] if proxies else "-"
        simulate_guess(guess, proxy)
        results.append({"guess": guess, "proxy": proxy, "status": "Done"})
        current_guess_index += 1
        time.sleep(0.3)  # Simulate delay for each guess

def simulate_guess(guess, proxy):
    # Simulate the guessing process in the web interface
    print(f"[+] Attempting: {guess} with proxy {proxy if proxy != '-' else 'None'}")

def save_results():
    # Save results to an HTML file
    html_content = "<html><head><title>Guessing Results</title></head><body>"
    html_content += "<h2>Guessing Results</h2><table border='1'><tr><th>Index</th><th>Guess</th><th>Proxy</th><th>Status</th></tr>"

    for idx, result in enumerate(results):
        html_content += f"<tr><td>{idx + 1}</td><td>{result['guess']}</td><td>{result['proxy']}</td><td>{result['status']}</td></tr>"

    html_content += "</table></body></html>"
    with open("results.html", "w") as file:
        file.write(html_content)

@app.route("/download")
def download_results():
    return send_from_directory(os.getcwd(), 'results.html')

if __name__ == "__main__":
    app.run(debug=True)
