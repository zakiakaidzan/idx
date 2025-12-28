import json
import random
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse
from CryptoJsAesHelper import CryptoJsAes, dec

# GUARD curl-cffi
try:
    from curl_cffi import requests as cffi_requests
except Exception as e:
    cffi_requests = None
    CURL_ERROR = str(e)

BASE_WEB_URL = "https://tv10.idlixku.com/"

# ✅ HEADER LENGKAP (SESUAI PUNYAMU)
BASE_STATIC_HEADERS = {
    "Host": "tv10.idlixku.com",
    "Connection": "keep-alive",
    "sec-ch-ua": "Not)A;Brand;v=99, Google Chrome;v=127, Chromium;v=127",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": BASE_WEB_URL,
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8"
}

def get_m3u8_by_id(video_id: str, content_type: str):
    if cffi_requests is None:
        return {
            "status": False,
            "message": "curl-cffi failed to load",
            "error": CURL_ERROR
        }

    # ✅ session DI DALAM function (WAJIB)
    session = cffi_requests.Session(
        impersonate=random.choice(["chrome124", "chrome119", "chrome104"]),
        headers=BASE_STATIC_HEADERS,
        timeout=15
    )

    # 1. halaman
    page = session.get(f"{BASE_WEB_URL}?p={video_id}")
    if page.status_code != 200:
        return {"status": False, "message": "Video not found"}

    bs = BeautifulSoup(page.text, "html.parser")
    title = unquote(bs.find("meta", {"itemprop": "name"}).get("content"))
    poster = bs.find("img", {"itemprop": "image"}).get("src")

    # 2. ajax embed
    ajax = session.post(
        BASE_WEB_URL + "wp-admin/admin-ajax.php",
        data={
            "action": "doo_player_ajax",
            "post": video_id,
            "nume": "1",
            "type": content_type
        }
    )

    if "embed_url" not in ajax.json():
        return {"status": False, "message": "Embed not found"}

    data = ajax.json()
    embed_url = CryptoJsAes.decrypt(
        data["embed_url"],
        dec(data["key"], json.loads(data["embed_url"])["m"])
    )

    # 3. hash
    if "/video/" in embed_url:
        embed_hash = embed_url.split("/video/")[1]
    else:
        embed_hash = urlparse(embed_url).query.split("=")[1]

    # 4. m3u8
    player = session.post(
        "https://jeniusplay.com/player/index.php",
        params={"data": embed_hash, "do": "getVideo"},
        data={"hash": embed_hash, "r": BASE_WEB_URL},
        headers={
            "X-Requested-With": "XMLHttpRequest",
            "Referer": BASE_WEB_URL,
            "User-Agent": BASE_STATIC_HEADERS["User-Agent"]
        }
    )

    if "videoSource" not in player.json():
        return {"status": False, "message": "Stream not found"}

    m3u8_url = player.json()["videoSource"].rsplit(".", 1)[0] + ".m3u8"

    return {
        "status": True,
        "title": title,
        "poster": poster,
        "m3u8": m3u8_url
    }
