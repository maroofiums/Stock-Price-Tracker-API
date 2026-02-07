import os
import requests

UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

HEADERS = {"Authorization": f"Bearer {UPSTASH_REDIS_TOKEN}"} if UPSTASH_REDIS_TOKEN else {}


def redis_get(key: str):
    if not UPSTASH_REDIS_URL or not UPSTASH_REDIS_TOKEN:
        return None
    try:
        r = requests.get(f"{UPSTASH_REDIS_URL}/get/{key}", headers=HEADERS, timeout=5)
        return r.json().get("result")
    except Exception as e:
        print("Redis GET error:", e)
        return None


def redis_setex(key: str, ttl: int, value: str):
    if not UPSTASH_REDIS_URL or not UPSTASH_REDIS_TOKEN:
        return
    try:
        requests.post(
            f"{UPSTASH_REDIS_URL}/setex/{key}/{ttl}",
            headers=HEADERS,
            data=value,
            timeout=5
        )
    except Exception as e:
        print("Redis SETEX error:", e)
