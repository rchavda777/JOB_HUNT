import requests
import os

# Replace with your actual API Key
API_KEY = "0e7fd36245bd4de3a0f00d2afb37f8be"
email = "testemail@gmail.com"  # Replace with any email to test

try:
    response = requests.get(
        f"https://api.zerobounce.net/v2/validate?email={email}&apikey={API_KEY}"
    )
    response.raise_for_status()  # Raises error if request fails
    data = response.json()

    print("API Response:", data)  # Check response structure

    if data.get("status") == "valid":
        print("✅ Email is valid. User can sign up.")
    else:
        print("❌ Email is not valid. Signup rejected.")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
