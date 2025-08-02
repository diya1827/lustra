from flask import Flask, render_template, request
from deepface import DeepFace
import requests
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

YOUTUBE_API_KEY = "AIzaSyBiO1eSSuaHZlqsmqHHDh_-lIUC9rSqUg4"

skin_map = {
    'white': 'fair',
    'black': 'deep',
    'asian': 'light-medium',
    'indian': 'medium',
    'latino hispanic': 'medium-tan',
    'middle eastern': 'olive'
}

def search_youtube(query, max_results=5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'key': YOUTUBE_API_KEY,
        'type': 'video',
        'maxResults': max_results
    }
    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        results.append({"title": title, "thumbnail": thumbnail, "url": video_url})

    return results

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["image"]
        event = request.form.get("event")
        skin_type = request.form.get("skin_type")
        style = request.form.get("style")
        duration = request.form.get("duration")
        focus_area = request.form.get("focus_area")
        manual_skin = request.form.get("manual_skin")

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            detected_skin = "medium"
            try:
                analysis = DeepFace.analyze(img_path=filepath, actions=["race"], enforce_detection=False)[0]
                raw_skin = analysis["dominant_race"]
                detected_skin = skin_map.get(raw_skin, raw_skin)
            except Exception:
                detected_skin = "medium"

            final_skin = manual_skin if manual_skin else detected_skin

            youtube_query = f"{final_skin} skin {skin_type} {style} {event} makeup tutorial {focus_area} {duration}"
            videos = search_youtube(youtube_query)

            return render_template("results.html", query=youtube_query, videos=videos)

    return render_template("index.html")

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)

