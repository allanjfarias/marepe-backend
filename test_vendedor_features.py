"""
Test script for vendedor status and location endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response, title):
    """Helper to print formatted response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")


def test_without_auth():
    """Test endpoints without authentication"""
    print("\n### Testing WITHOUT Authentication ###")

    # Test status update without auth
    response = requests.put(
        f"{BASE_URL}/vendedor/status",
        json={"status": "online"}
    )
    print_response(response, "PUT /vendedor/status (No Auth)")

    # Test location save without auth
    response = requests.post(
        f"{BASE_URL}/vendedor/location",
        json={
            "latitude": -8.0476,
            "longitude": -34.8770,
            "accuracy": 10.5
        }
    )
    print_response(response, "POST /vendedor/location (No Auth)")


def test_with_mock_auth():
    """Test endpoints with a mock/invalid token"""
    print("\n### Testing WITH Invalid Token ###")

    headers = {"Authorization": "Bearer invalid_token_here"}

    # Test status update with invalid token
    response = requests.put(
        f"{BASE_URL}/vendedor/status",
        json={"status": "online"},
        headers=headers
    )
    print_response(response, "PUT /vendedor/status (Invalid Token)")

    # Test location save with invalid token
    response = requests.post(
        f"{BASE_URL}/vendedor/location",
        json={
            "latitude": -8.0476,
            "longitude": -34.8770,
            "accuracy": 10.5
        },
        headers=headers
    )
    print_response(response, "POST /vendedor/location (Invalid Token)")


def test_status_validation():
    """Test status validation (only 'online' or 'offline' allowed)"""
    print("\n### Testing Status Validation ###")

    headers = {"Authorization": "Bearer mock_token"}

    # Test with invalid status
    response = requests.put(
        f"{BASE_URL}/vendedor/status",
        json={"status": "busy"},
        headers=headers
    )
    print_response(response, "PUT /vendedor/status (Invalid Status Value)")


def test_location_validation():
    """Test location validation"""
    print("\n### Testing Location Validation ###")

    headers = {"Authorization": "Bearer mock_token"}

    # Test with missing latitude
    response = requests.post(
        f"{BASE_URL}/vendedor/location",
        json={
            "longitude": -34.8770,
            "accuracy": 10.5
        },
        headers=headers
    )
    print_response(response, "POST /vendedor/location (Missing Latitude)")

    # Test with invalid data types
    response = requests.post(
        f"{BASE_URL}/vendedor/location",
        json={
            "latitude": "invalid",
            "longitude": -34.8770,
            "accuracy": 10.5
        },
        headers=headers
    )
    print_response(response, "POST /vendedor/location (Invalid Latitude Type)")


def test_api_docs():
    """Test if API docs are accessible"""
    print("\n### Testing API Documentation ###")

    response = requests.get(f"{BASE_URL}/docs")
    print(f"API Docs accessible: {response.status_code == 200}")

    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"OpenAPI spec accessible: {response.status_code == 200}")

    if response.status_code == 200:
        openapi = response.json()
        print(f"\nEndpoints registered:")
        for path in openapi.get('paths', {}).keys():
            if 'vendedor' in path:
                methods = list(openapi['paths'][path].keys())
                print(f"  - {', '.join([m.upper() for m in methods])} {path}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MAREPE VENDEDOR FEATURES TEST SUITE")
    print("="*60)

    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/")
        print(f"\n[OK] Server is running at {BASE_URL}")
        print(f"  Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Server is not running at {BASE_URL}")
        print("  Please start the server with: uvicorn app.main:app --reload")
        return

    # Run tests
    test_api_docs()
    test_without_auth()
    test_with_mock_auth()
    test_status_validation()
    test_location_validation()

    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
    print("\nNOTE: To fully test with real authentication:")
    print("1. Create a vendedor account via POST /auth/signup")
    print("2. Login via POST /auth/login to get a valid token")
    print("3. Use the token in the Authorization header")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
