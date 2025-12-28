from idlix_api import get_m3u8_by_id

def handler(request):
    # health check
    video_id = request.args.get("id")
    content_type = request.args.get("type", "movie").lower()

    if content_type not in ["movie", "tv"]:
        content_type = "movie"

    if not video_id:
        return {
            "statusCode": 200,
            "body": {
                "status": True,
                "message": "IDLIX M3U8 API is running"
            }
        }

    result = get_m3u8_by_id(video_id, content_type)

    return {
        "statusCode": 200,
        "body": result
    }
