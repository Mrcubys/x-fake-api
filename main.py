from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="X Fake Followers Detection API",
    description="Detect fake or bot followers using heuristic scoring",
    version="1.0.0"
)

# ===================== MODELS =====================

class Follower(BaseModel):
    username: str
    account_age_days: int
    tweets: int
    followers: int
    following: int
    default_pfp: bool


class ScanRequest(BaseModel):
    username: str
    followers_data: List[Follower]


# ===================== SCORING LOGIC =====================

def calculate_bot_score(follower: Follower) -> int:
    score = 0

    # Akun baru
    if follower.account_age_days < 30:
        score += 25

    # Tweet sangat sedikit
    if follower.tweets < 10:
        score += 15

    # Follow banyak tapi follower sedikit
    if follower.followers < follower.following:
        score += 20

    # Foto profil default
    if follower.default_pfp:
        score += 10

    return min(score, 100)


# ===================== API ENDPOINT =====================

@app.post("/api/v1/x-fake-scan")
def scan_followers(data: ScanRequest):
    scores = []
    
    for follower in data.followers_data:
        score = calculate_bot_score(follower)
        scores.append(score)

    total_followers = len(scores)
    fake_followers = len([s for s in scores if s >= 50])

    fake_percent = round((fake_followers / total_followers) * 100, 2) if total_followers > 0 else 0
    real_percent = round(100 - fake_percent, 2)

    if fake_percent > 60:
        risk_level = "HIGH"
    elif fake_percent > 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "username": data.username,
        "total_followers_scanned": total_followers,
        "fake_detected": fake_followers,
        "fake_followers_percentage": fake_percent,
        "real_followers_percentage": real_percent,
        "bot_score": fake_percent / 100,
        "risk_level": risk_level
    }


# ===================== ROOT =====================

@app.get("/")
def root():
    return {"status": "X Fake Followers API is running"}
