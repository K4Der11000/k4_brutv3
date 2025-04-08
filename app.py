from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Secret for storing the session

# Password
PASSWORD = 'kader11000'

guesses = []
proxies = []
results = []
remaining_guess_time = 0
current_guess_index = 0
is_guessing_paused = False
variable_url = ""

# Login page with password
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered_password = request.form.get('password')
        if entered_password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return "Invalid password. Try again.", 403

    return render_template_string("""
    <html><head><title>Login</title></head>
    <body>
        <h2>Enter Password</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </body></html>
    """)

# Ensure that the user is logged in
def require_authentication():
    if not session.get('authenticated'):
        return redirect(url_for('login'))

# Route to render the main page
@app.route('/app', methods=['GET'])
def index():
    if require_authentication():
        return require_authentication()
    
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en" dir="ltr">
    <head>
      <meta charset="UTF-8">
      <title>Advanced URL Guessing Tool</title>
      <style>
        body { background-color: #000; color: #0f0; font-family: monospace; padding: 20px; }
        textarea, input, button, select { background-color: #111; color: #0f0; border: 1px solid #0f0; padding: 8px; margin: 5px 0; width: 100%; border-radius: 6px; }
        button { cursor: pointer; }
        #guessOutput { background-color: #111; border: 1px solid #0f0; padding: 10px; margin-top: 20px; height: 200px; overflow-y: scroll; }
        #guessTimerBanner { display: none; background: #111; color: #0f0; padding: 6px 10px; border-top: 2px solid #0f0; font-weight: bold; text-align: center; margin-top: 10px; }
        #resultButtons { margin-top: 10px; text-align: center; }
        .result-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .result-table th, .result-table td { border: 1px solid #0f0; padding: 6px; text-align: center; }
        .result-table th { background-color: #060; }
        .result-table td { background-color: #020; }
      </style>
    </head>
    <body>

    <h2>URL Guessing Tool</h2>

    <h3>Target URL</h3>
    <textarea id="urlInput" placeholder="Enter the URL here...">https://example.com/item/1234/details</textarea>
    <button onclick="markVariable()">Mark Selected Text as Variable</button>
    <textarea id="urlWithVariable" readonly placeholder="URL with variable will appear here..."></textarea>

    <h3>Guess List</h3>
    <textarea id="guessList" placeholder="Enter the guesses here..."></textarea>

    <h3>Proxy List (Optional)</h3>
    <textarea id="proxyList" placeholder="Enter proxies here..."></textarea>

    <div>
      <button onclick="startGuessing()">Start Guessing</button>
      <button id="pauseResumeBtn" onclick="togglePauseGuessing()">Pause</button>
    </div>

    <div id="guessTimerBanner">Time Remaining: <span id="guessTimeLeft">--:--</span></div>

    <div id="resultButtons">
      <button onclick="showResults()">Show Results</button>
      <button onclick="saveResults()">Save Results</button>
    </div>

    <div id="guessOutput"></div>

    <script>
    let isGuessingPaused = false;
    let guessInterval = null;
    let guessTimerInterval = null;
    let remainingGuessTime = 0;
    let currentGuessIndex = 0;
    let guesses = [];
    let proxies = [];
    let results = [];
    let variableUrl = "";  // Variable for holding the modified URL with {{VAR}}

    function getGuessList() {
      const raw = document.getElementById("guessList").value;
      return raw.split("\n").map(x => x.trim()).filter(x => x);
    }

    function getProxyList() {
      const raw = document.getElementById("proxyList").value;
      return raw.split("\n").map(x => x.trim()).filter(x => x);
    }

    function markVariable() {
      const urlInput = document.getElementById("urlInput");
      const urlWithVar = document.getElementById("urlWithVariable");
      const start = urlInput.selectionStart;
      const end = urlInput.selectionEnd;

      if (start === end) {
        alert("Please select the part of the URL to be replaced with a variable.");
        return;
      }

      const original = urlInput.value;
      const selected = original.substring(start, end);
      const modified = original.substring(0, start) + "{{VAR}}" + original.substring(end);

      urlWithVar.value = modified;

      variableUrl = modified;  // Save the modified URL for use later
    }

    function startGuessing() {
      guesses = getGuessList();
      proxies = getProxyList();
      currentGuessIndex = 0;
      results = [];

      const guessCount = guesses.length;
      const estimatedTime = Math.ceil(guessCount * 0.3 / Math.max(proxies.length || 1, 1));
      remainingGuessTime = estimatedTime;

      startGuessTimer(remainingGuessTime);
      startGuessLoop();
    }

    function startGuessLoop() {
      isGuessingPaused = false;

      if (guessInterval) clearInterval(guessInterval);
      guessInterval = setInterval(() => {
        if (isGuessingPaused || currentGuessIndex >= guesses.length) return;

        const guess = guesses[currentGuessIndex];
        const proxy = proxies[currentGuessIndex % (proxies.length || 1)] || "-";

        simulateGuess(guess, proxy);

        results.push({ guess, proxy, status: "Completed" });
        currentGuessIndex++;

        if (currentGuessIndex >= guesses.length) {
          clearInterval(guessInterval);
        }
      }, 300);
    }

    function simulateGuess(guess, proxy) {
      const terminal = document.getElementById("guessOutput");
      const url = variableUrl.replace("{{VAR}}", guess);  // Replace the {{VAR}} placeholder with the guess
      terminal.innerHTML += `<div style="color:#0f0;">[+]: Tested: ${url} ${proxy !== "-" ? ' via ' + proxy : ''}</div>`;
      terminal.scrollTop = terminal.scrollHeight;
    }

    function startGuessTimer(durationInSeconds) {
      const banner = document.getElementById("guessTimerBanner");
      const text = document.getElementById("guessTimeLeft");

      remainingGuessTime = durationInSeconds;
      banner.style.display = "block";

      if (guessTimerInterval) clearInterval(guessTimerInterval);
      guessTimerInterval = setInterval(() => {
        if (!isGuessingPaused && remainingGuessTime > 0) {
          remainingGuessTime--;
          let m = Math.floor(remainingGuessTime / 60);
          let s = remainingGuessTime % 60;
          text.textContent = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        }

        if (remainingGuessTime <= 0) {
          clearInterval(guessTimerInterval);
          text.textContent = "00:00";
          setTimeout(() => banner.style.display = "none", 3000);
        }
      }, 1000);
    }

    function togglePauseGuessing() {
      const btn = document.getElementById("pauseResumeBtn");
      isGuessingPaused = !isGuessingPaused;
      btn.textContent = isGuessingPaused ? "Resume" : "Pause";
      btn.style.backgroundColor = isGuessingPaused ? "#550" : "#222";
    }

    function showResults() {
      const win = window.open("", "_blank");
      let html = `
      <html><head><title>Guessing Results</title>
      <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #0f0; padding: 8px; text-align: center; }
        th { background-color: #060; }
        td { background-color: #020; }
      </style></head><body>
      <h2>Guessing Results</h2>
      <table>
        <
