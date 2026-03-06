import re, html, requests
from flask import Flask, request, redirect

app = Flask(__name__)
MAX_LEN = 150


def e(s):
    return html.escape(str(s), quote=True)


def get_og(url):
    news_id = re.search(r"/news/(\d+)", url).group(1)
    news = requests.get(
        f"https://api.saveticker.com/api/news/detail/{news_id}", timeout=10
    ).json()["news"]

    title = news.get("title", "SaveTicker")
    src = (news.get("source") or "").strip()

    text = " ".join(
        i["content"] for i in news.get("content", []) if i.get("type") == "text"
    )
    text = re.sub(r"\s+", " ", text).replace("- ", "").strip()

    desc = text[:MAX_LEN].rstrip()
    if len(text) > MAX_LEN:
        desc += ".."
    if src:
        desc = f"[{src}] {desc}"

    return {
        "title": title,
        "description": desc or title,
        "url": url if url.startswith("http") else f"https://{url}",
    }


@app.route("/")
def index():
    return redirect("https://saveticker.com")

@app.route("/og/<path:url>")
def og(url):

    url = url.replace("https:/", "https://").replace("http:/", "http://")

    if not url.startswith("http"):
        url = f"https://{url}"

    d = get_og(url)

    img = request.url_root.rstrip("/") + "/static/og_image.png"
    t, desc, u = map(e, (d["title"], d["description"], d["url"]))

    return f"""
    <!DOCTYPE html>
    <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta property="og:type" content="article">
            <meta property="og:title" content="{t}">
            <meta property="og:description" content="{desc}">
            <meta property="og:image" content="{img}">
            <meta property="og:url" content="{u}">
            <meta http-equiv="refresh" content="0; url={u}">
            <script>location.replace("{u}")</script>
        </head>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, port=5000)
