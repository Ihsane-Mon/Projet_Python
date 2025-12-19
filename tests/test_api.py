import requests

BASE_URL = "http://localhost:5000/api"

# Test liste produits (sans auth)
print("=== GET /products ===")
r = requests.get(f"{BASE_URL}/products", timeout=10)
print(r.json())

# Test login
print("\n=== POST /auth/login ===")
r = requests.post(
    f"{BASE_URL}/auth/login",
    json={ 
        "username": "marie",
        "password": "Xk9mP2qL7nB4vR"})
print(r.json())
token = r.json().get("token")

# Test créer produit (avec auth)
print("\n=== POST /products ===")
headers = {"Authorization": f"Bearer {token}"}
r = requests.post(
    f"{BASE_URL}/products",
    json={
        "nom": "Clé USB 64Go",
        "description": "Clé USB 3.0",
        "prix": 12.99,
        "quantite": 100,
    },
    headers=headers,
    timeout=10
)
print(r.json())

# Test stats
print("\n=== GET /stats ===")
r = requests.get(f"{BASE_URL}/stats", headers=headers, timeout=10)
print(r.json())
