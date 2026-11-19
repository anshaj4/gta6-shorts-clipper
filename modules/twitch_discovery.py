import os
import re
import time
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

GTA_VI_GAME_ID = "1867279146"
GTA_V_GAME_ID = "32982"

class TwitchDiscovery:
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("TWITCH_CLIENT_SECRET")
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0
        if not self.client_id or not self.client_secret:
            raise ValueError("TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET must be set.")

    def _ensure_token(self) -> str:
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token

        url = "https://id.twitch.tv/oauth2/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        res = requests.post(url, data=data, timeout=10)
        res.raise_for_status()
        payload = res.json()
        self.access_token = payload["access_token"]
        self.token_expiry = time.time() + payload.get("expires_in", 3600)
        return self.access_token

    def _get_headers(self) -> Dict[str, str]:
        token = self._ensure_token()
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}"
        }

    def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = self._get_headers()
        url = f"https://api.twitch.tv/helix/{endpoint}"
        res = requests.get(url, headers=headers, params=params, timeout=15)
        if res.status_code == 401:
            self.access_token = None
            headers = self._get_headers()
            res = requests.get(url, headers=headers, params=params, timeout=15)
        res.raise_for_status()
        return res.json()

    def get_game_id(self, game_name: str = "Grand Theft Auto VI") -> Optional[str]:
        data = self._request("games", {"name": game_name})
        games = data.get("data", [])
        if games:
            return games[0]["id"]
        return None

    def discover_live_streams(
        self,
        game_id: str = GTA_VI_GAME_ID,
        language: Optional[str] = None,
        min_viewers: int = 0,
        max_viewers: Optional[int] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        params = {"game_id": game_id, "first": min(limit, 100)}
        if language:
            params["language"] = language

        res = self._request("streams", params)
        streams = res.get("data", [])

        filtered = []
        for s in streams:
            vc = s.get("viewer_count", 0)
            if vc < min_viewers:
                continue
            if max_viewers is not None and vc > max_viewers:
                continue
            is_uk = self._check_uk_streamer(s)
            s["is_uk_likely"] = is_uk
            filtered.append(s)

        return filtered

    def discover_vods(
        self,
        game_id: str = GTA_VI_GAME_ID,
        user_id: Optional[str] = None,
        language: Optional[str] = None,
        min_duration_seconds: int = 120,
        max_duration_seconds: int = 1000000,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Discovers GTA 6 VODs both from live streamers' archives and category archives.
        """
        discovered_vods = []
        seen_ids = set()

        # 1. First, check active live streamers and pull their latest VOD archives
        try:
            live_streams = self.discover_live_streams(game_id=game_id, language=language, limit=20)
            for s in live_streams:
                u_id = s.get("user_id")
                u_name = s.get("user_name")
                if not u_id:
                    continue
                res = self._request("videos", {"user_id": u_id, "type": "archive", "first": 3})
                for v in res.get("data", []):
                    vid_id = str(v.get("id"))
                    if vid_id in seen_ids:
                        continue
                    dur_sec = self._parse_duration(v.get("duration", "0s"))
                    v["duration_seconds"] = dur_sec
                    if dur_sec >= min_duration_seconds and dur_sec <= max_duration_seconds:
                        v["is_uk_likely"] = self._check_uk_streamer(v)
                        seen_ids.add(vid_id)
                        discovered_vods.append(v)
                    if len(discovered_vods) >= limit:
                        break
                if len(discovered_vods) >= limit:
                    break
        except Exception:
            pass

        # 2. Also check direct category VODs
        if len(discovered_vods) < limit:
            try:
                cat_vods = self._request("videos", {"game_id": game_id, "first": 50}).get("data", [])
                for v in cat_vods:
                    vid_id = str(v.get("id"))
                    if vid_id in seen_ids:
                        continue
                    dur_sec = self._parse_duration(v.get("duration", "0s"))
                    v["duration_seconds"] = dur_sec
                    if dur_sec >= min_duration_seconds and dur_sec <= max_duration_seconds:
                        v["is_uk_likely"] = self._check_uk_streamer(v)
                        seen_ids.add(vid_id)
                        discovered_vods.append(v)
                    if len(discovered_vods) >= limit:
                        break
            except Exception:
                pass

        # If language filter is specified, sort preferred language first
        if language:
            discovered_vods.sort(key=lambda x: 0 if x.get("language") == language else 1)

        return discovered_vods

    def _parse_duration(self, duration_str: str) -> int:
        hours = re.search(r"(\d+)h", duration_str)
        mins = re.search(r"(\d+)m", duration_str)
        secs = re.search(r"(\d+)s", duration_str)

        h = int(hours.group(1)) if hours else 0
        m = int(mins.group(1)) if mins else 0
        s = int(secs.group(1)) if secs else 0
        return h * 3600 + m * 60 + s

    def _check_uk_streamer(self, item: Dict[str, Any]) -> bool:
        text = f"{item.get('title', '')} {item.get('user_name', '')} {' '.join(item.get('tags', []) or [])}".lower()
        uk_indicators = ["uk", "united kingdom", "london", "british", "brit", "england", "scotland", "wales", "irish", "ireland", "gmt", "bst"]
        for ind in uk_indicators:
            if re.search(rf"\b{ind}\b", text):
                return True
        return False
