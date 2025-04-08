from flask import Flask, request, Response, send_file
import time, json, os

app = Flask(__name__)
results = []

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>URL Guessing Tool</title>
</head>
<body style="background:#000;color:#0f0;font-family:monospace;padding:20px;">
    <h2>Advanced URL Guessing Tool</h2>

    <label>Base URLs:</label>
    <div style="display:flex;gap:10px;">
        <textarea id="base-url" placeholder="Enter one or more base URLs, one per line" rows="4" style="width:100%;"></textarea>
        <button id="save-urls">Save</button>
        <button id="load-urls">Restore</button>
    </div>

    <br>
    <label>Wordlist:</label>
    <textarea id="wordlist" placeholder="Paste words from Excel or CSV here..." rows="5" style="width:100%;"></textarea>
    <br>
    <input type="file" id="wordlist-file" accept=".txt,.csv">
    <button type="button" id="load-wordlist">Load Wordlist from File</button>
    <p id="word-count" style="color:gray;">Word count: 0</p>

    <br>
    <label>Proxy Mode:</label>
    <select id="proxy-mode">
        <option value="none">None</option>
        <option value="auto">Auto</option>
    </select>

    <br><br>
    <button onclick="start()">Start Guessing</button>
    <div id="info" style="margin-top:15px;"></div>
    <div id="results" style="margin-top:15px;"></div>
    <button id="download-btn" style="display:none;margin-top:15px;">Download Results</button>

<script>
    function start() {
        document.getElementById("results").innerHTML = "";
        document.getElementById("info").innerHTML = "Guessing in progress...";
        document.getElementById("download-btn").style.display = "none";

        const base_urls = document.getElementById("base-url").value.split("\n").map(x => x.trim()).filter(Boolean);
        const wordlist = document.getElementById("wordlist").value;
        const proxy_mode = document.getElementById("proxy-mode").value;

        fetch("/stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ base_urls, wordlist, proxy_mode })
        }).then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) return;
                    const chunk = decoder.decode(value, { stream: true });
                    chunk.trim().split("data: ").forEach(line => {
                        if (line) {
                            const data = JSON.parse(line);
                            if (data.done) {
                                document.getElementById("info").innerHTML += `<br><strong>Completed in ${data.elapsed} seconds</strong>`;
                                document.getElementById("download-btn").style.display = "block";
                                return;
                            }
                            if (data.status === 200) {
                                document.getElementById("results").innerHTML += `<p><strong>[${data.base_url}]</strong> ${data.url} - ${data.status} - ${data.proxy}</p>`;
                            }
                        }
                    });
                    read();
                });
            }
            read();
        });
    }

    function updateWordCount() {
        const words = document.getElementById("wordlist").value.split('\n').map(w => w.trim()).filter(Boolean);
        document.getElementById("word-count").textContent = `Word count: ${words.length}`;
    }
    document.getElementById("wordlist").addEventListener("input", updateWordCount);

    document.getElementById("load-wordlist").addEventListener("click", () => {
        const file = document.getElementById("wordlist-file").files[0];
        if (!file) return alert("Choose a file first.");
        const reader = new FileReader();
        reader.onload = e => {
            document.getElementById("wordlist").value = e.target.result;
            updateWordCount();
        };
        reader.readAsText(file);
    });

    document.getElementById("wordlist").addEventListener("paste", (e) => {
        e.preventDefault();
        const pasted = (e.clipboardData || window.clipboardData).getData("text");
        const cleaned = pasted.replace(/[\t,;]/g, '\n').split('\n').map(w => w.trim()).filter(Boolean).join('\n');
        document.getElementById("wordlist").value += (document.getElementById("wordlist").value ? '\n' : '') + cleaned;
        updateWordCount();
    });

    document.getElementById("save-urls").addEventListener("click", () => {
        localStorage.setItem("saved_base_urls", document.getElementById("base-url").value);
        alert("URLs saved.");
    });

    document.getElementById("load-urls").addEventListener("click", () => {
        const saved = localStorage.getItem("saved_base_urls");
        if (saved) {
            document.getElementById("base-url").value = saved;
            alert("URLs restored.");
        } else {
            alert("No saved URLs.");
        }
    });

    document.getElementById("download-btn").addEventListener("click", () => {
        window.open('/download-results', '_blank');
    });
</script>
</body>
</html>
"""  # ØªÙ… Ø§Ø®ØªØµØ§Ø± Ø§Ù„Ù…Ø­ØªÙˆÙ‰ Ù‡Ù†Ø§ Ù„Ù„ØªÙˆÙÙŠØ±ØŒ Ø³ÙŠØªÙ… Ø¥Ø¯Ø±Ø§Ø¬Ù‡ Ø¨Ø§Ù„ÙƒØ§Ù…Ù„ ÙÙŠ Ø§Ù„Ù…Ù„Ù Ø§Ù„Ù†Ù‡Ø§Ø¦ÙŠ

@app.route("/")
def index():
    return HTML_TEMPLATE

def get_proxies(mode):
    return ["proxy1", "proxy2"] if mode == "auto" else []

@app.route("/stream", methods=["POST"])
def stream():
    data = request.json
    base_urls = data.get("base_urls", [])
    wordlist = data.get("wordlist", "").split("\n")
    proxy_mode = data.get("proxy_mode", "none")
    proxies = get_proxies(proxy_mode)
    results.clear()
    start_time = time.time()

    def generate():
        count = 0
        for base_url in base_urls:
            for word in wordlist:
                proxy = proxies[count % len(proxies)] if proxies else "none"
                guessed_url = base_url.replace("{{var1}}", word)
                status = 200 if "admin" in guessed_url else 404
                result = {
                    "url": guessed_url,
                    "status": status,
                    "proxy": proxy,
                    "base_url": base_url
                }
                results.append(result)
                count += 1
                time.sleep(0.1)
                yield f"data: {json.dumps(result)}\n\n"
        yield f"data: {json.dumps({'done': True, 'elapsed': round(time.time() - start_time, 2)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route("/download-results")
def download_results():
    html = "<html><head><style>body{background:#111;color:#0f0;font-family:monospace;}table{width:100%;border-collapse:collapse;}td,th{border:1px solid #0f0;padding:5px;}</style></head><body><h2>Results</h2><table><tr><th>Base URL</th><th>Guessed URL</th><th>Status</th><th>Proxy</th></tr>"
    for r in results:
        html += f"<tr><td>{r['base_url']}</td><td>{r['url']}</td><td>{r['status']}</td><td>{r['proxy']}</td></tr>"
    html += "</table></body></html>"
    with open("results.html", "w") as f:
        f.write(html)
    return send_file("results.html", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
