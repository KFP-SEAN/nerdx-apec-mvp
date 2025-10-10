"""
Simple API test script for Phase 2: Agentic System
"""
import asyncio
import httpx
import json
from datetime import datetime


BASE_URL = "http://localhost:8002"


async def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*50)
    print("Testing Health Check")
    print("="*50)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        # Detailed health check
        response = await client.get(f"{BASE_URL}/health/detailed")
        print(f"\nDetailed Health Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_queue_status():
    """Test queue status endpoint"""
    print("\n" + "="*50)
    print("Testing Queue Status")
    print("="*50)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/cameo/queue/status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_rate_limit():
    """Test rate limit info endpoint"""
    print("\n" + "="*50)
    print("Testing Rate Limit Info")
    print("="*50)

    user_id = "test_user_123"

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/cameo/rate-limit/{user_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_video_generation():
    """Test video generation endpoint"""
    print("\n" + "="*50)
    print("Testing Video Generation")
    print("="*50)

    request_data = {
        "user_id": "test_user_123",
        "user_face_image": "https://example.com/test-face.jpg",
        "template": "sam_altman_apec",
        "prompt": "Create a professional video of me discussing AI innovations at APEC summit",
        "duration": 15,
        "quality": "high",
        "resolution": "1920x1080",
        "audio_enabled": True
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/cameo/generate",
            json=request_data
        )
        print(f"\nStatus: {response.status_code}")

        if response.status_code == 202:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            job_id = result.get("job_id")

            # Test status check
            if job_id:
                await asyncio.sleep(2)
                print(f"\n--- Checking job status for: {job_id} ---")
                status_response = await client.get(
                    f"{BASE_URL}/api/v1/cameo/status/{job_id}"
                )
                print(f"Status Check Response: {json.dumps(status_response.json(), indent=2)}")

                return job_id
        else:
            print(f"Error: {response.text}")

    return None


async def test_list_videos():
    """Test list videos endpoint"""
    print("\n" + "="*50)
    print("Testing List User Videos")
    print("="*50)

    user_id = "test_user_123"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/cameo/videos/{user_id}?page=1&page_size=10"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_storage_stats():
    """Test storage stats endpoint"""
    print("\n" + "="*50)
    print("Testing Storage Stats (Admin)")
    print("="*50)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/admin/storage/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def test_config():
    """Test config endpoint"""
    print("\n" + "="*50)
    print("Testing Configuration")
    print("="*50)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/admin/config")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Phase 2: Agentic System - API Test Suite")
    print("="*60)
    print(f"  Base URL: {BASE_URL}")
    print(f"  Time: {datetime.now().isoformat()}")
    print("="*60)

    try:
        # Basic tests
        await test_health_check()
        await test_config()
        await test_queue_status()
        await test_rate_limit()

        # Video generation tests
        job_id = await test_video_generation()

        # List videos
        await test_list_videos()

        # Admin tests
        await test_storage_stats()

        print("\n" + "="*60)
        print("  All tests completed!")
        print("="*60 + "\n")

    except httpx.ConnectError:
        print("\n[ERROR] Could not connect to API. Make sure it's running:")
        print("  python main.py")
        print("  OR")
        print("  docker-compose up\n")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
