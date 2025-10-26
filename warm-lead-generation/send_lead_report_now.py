#!/usr/bin/env python3
"""
즉시 Lead 리포트 발송 (Railway API 사용)
"""
import requests
import sys

def send_lead_report(email: str):
    """Railway API를 통해 Lead 리포트 발송"""
    print("="*60)
    print("NERDX Lead Report - Immediate Send")
    print("="*60)
    print(f"Recipient: {email}")
    print()

    # Railway API 호출
    url = f"https://warm-lead-generation-production.up.railway.app/api/v1/lead-report/send?email={email}"

    print(f"Calling API: {url}")
    print()

    try:
        response = requests.post(url, timeout=60)

        if response.status_code == 200:
            result = response.json()
            print("SUCCESS! Lead report sent")
            print(f"  Message: {result.get('message')}")
            print(f"  Total Leads: {result.get('total_leads')}")
            print(f"  TIER 1: {result.get('tier1_count')}")
            print(f"  TIER 2: {result.get('tier2_count')}")
            print(f"  Email: {result.get('email')}")
        else:
            print(f"ERROR: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"ERROR: {e}")

    print("="*60)


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "sean@koreafnbpartners.com"
    send_lead_report(email)
