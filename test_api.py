import requests

BASE = "http://127.0.0.1:8000"


def show(name, response):
    try:
        body = response.json()
    except Exception:
        body = response.text

    print(f"\n{name}: {response.status_code}")
    print(body)


# 1. Health check
r = requests.get(f"{BASE}/health")
show("Health", r)

# 2. Register user
r = requests.post(
    f"{BASE}/auth/register",
    json={
        "email": "test@rayhub.com",
        "password": "Test1234!",
        "full_name": "Test User",
        "username": "testuser",
        "cpa_level": "Foundation",
    },
)
show("Register", r)

# 3. Login
r = requests.post(
    f"{BASE}/auth/login",
    json={
        "email": "test@rayhub.com",
        "password": "Test1234!",
    },
)
show("Login", r)

token = None
try:
    token = r.json().get("access_token")
except Exception:
    pass

headers = {"Authorization": f"Bearer {token}"} if token else {}

# 4. Get me
r = requests.get(f"{BASE}/auth/me", headers=headers)
show("Me", r)

# 5. Get levels
r = requests.get(f"{BASE}/levels/", headers=headers)
show("Levels", r)

# 6. Get courses
r = requests.get(f"{BASE}/courses/", headers=headers)
show("Courses", r)

# 7. Get units
r = requests.get(f"{BASE}/units/", headers=headers)
show("Units", r)

# 8. Get topics
r = requests.get(f"{BASE}/topics/", headers=headers)
show("Topics", r)

# 9. Progress summary
r = requests.get(f"{BASE}/progress/summary", headers=headers)
show("Progress", r)

# 10. Gamification
r = requests.get(f"{BASE}/gamification/profile", headers=headers)
show("Gamification", r)

# 11. Leaderboard
r = requests.get(f"{BASE}/gamification/leaderboard", headers=headers)
show("Leaderboard", r)