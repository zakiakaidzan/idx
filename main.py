from flask import Flask, request, jsonify
from idlix_api import get_m3u8_by_id

app = Flask(__name__)

@app.route("/api/idlix", methods=["GET"])
def idlix():
    video_id = request.args.get("id")
    content_type = request.args.get("type", "movie").lower()

    if content_type not in ["movie", "tv"]:
        content_type = "movie"

    # health check
    if not video_id:
        return jsonify({
            "status": True,
            "message": "IDLIX M3U8 API is running"
        })

    try:
        result = get_m3u8_by_id(video_id, content_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": False,
            "error": str(e)
        }), 500
