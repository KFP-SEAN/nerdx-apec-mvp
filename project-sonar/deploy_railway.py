#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Sonar - Railway 배포 자동화 스크립트
"""
import subprocess
import sys
import time
import io

# Windows 콘솔 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def run_command(cmd, timeout=60):
    """명령어 실행"""
    print(f"\n> Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        print(result.stdout)
        if result.stderr:
            print(f"Warning/Errors:\n{result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Project Sonar - Railway Deployment")
    print("=" * 60)

    # Step 1: Railway 로그인 확인
    print("\n[1/5] Railway login check...")
    if not run_command("railway whoami"):
        print("ERROR: Not logged in to Railway.")
        print("Please login: railway login")
        sys.exit(1)

    # Step 2: requirements.txt를 Railway용으로 교체
    print("\n[2/5] Switch to Railway requirements...")
    try:
        import shutil
        shutil.copy("requirements-railway.txt", "requirements.txt")
        print("OK: requirements.txt updated")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Step 3: Git 커밋 (requirements.txt 변경사항)
    print("\n[3/5] Git 변경사항 커밋...")
    run_command("git add requirements.txt")
    run_command('git commit -m "Switch to Railway requirements"')

    # Step 4: Railway project setup
    print("\n[4/5] Railway project setup...")
    print("WARNING: Complete these steps manually:")
    print("1. Go to https://railway.app/dashboard and click New Project")
    print("2. Select 'Deploy from GitHub repo'")
    print("3. Choose nerdx-apec-mvp repository")
    print("4. Set Root Directory to: project-sonar")
    print("5. Configure environment variables (see next section)")

    # Step 5: Environment variables guide
    print("\n[5/5] Environment Variables Setup Guide")
    print("=" * 60)
    print("Add these in Railway Dashboard -> Settings -> Variables:")
    print("=" * 60)

    env_vars = {
        "API_ENVIRONMENT": "production",
        "API_HOST": "0.0.0.0",
        "PORT": "$PORT (Railway 자동 할당)",
        "WIPO_API_KEY": "your_wipo_api_key_here",
        "KIS_API_KEY": "your_kis_api_key_here",
        "KIS_API_SECRET": "your_kis_api_secret_here",
        "NEWS_API_CLIENT_ID": "your_naver_client_id_here",
        "NEWS_API_CLIENT_SECRET": "your_naver_client_secret_here",
        "ANTHROPIC_API_KEY": "your_anthropic_key_here",
        "OPENAI_API_KEY": "(선택) your_openai_key_here",
        "GEMINI_API_KEY": "(선택) your_gemini_key_here",
    }

    for key, value in env_vars.items():
        print(f"  {key}={value}")

    print("\n" + "=" * 60)
    print("See RAILWAY_DEPLOYMENT.md for details")
    print("=" * 60)

    # Step 6: Deployment check guide
    print("\nOK: Setup complete!")
    print("\nCheck deployment status:")
    print("  railway status")
    print("  railway logs")
    print("\nTest after deployment:")
    print("  curl https://your-app.up.railway.app/health")
    print("=" * 60)

if __name__ == "__main__":
    main()
