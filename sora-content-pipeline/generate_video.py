#!/usr/bin/env python3
"""
NERDX APEC MVP - Sora 2 비디오 생성 스크립트
샘 올트먼의 경주 불국사 소개 영상 생성

Requirements:
- OpenAI API key with Sora 2 access
- Python 3.11+
- openai library (pip install openai)

Usage:
    python generate_video.py --prompt-file bulguksa_sam_altman_prompt.md --output bulguksa_sam.mp4
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI library not found. Installing...")
    os.system(f"{sys.executable} -m pip install openai --quiet")
    from openai import OpenAI


class SoraVideoGenerator:
    """Sora 2 API를 사용한 비디오 생성 클래스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Args:
            api_key: OpenAI API Key (없으면 환경변수에서 가져옴)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API Key가 필요합니다. "
                "환경변수 OPENAI_API_KEY를 설정하거나 --api-key 인자를 사용하세요."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.output_dir = Path("./outputs")
        self.output_dir.mkdir(exist_ok=True)

    def extract_main_prompt(self, prompt_file: Path) -> str:
        """
        마크다운 파일에서 메인 Sora 프롬프트 추출

        Args:
            prompt_file: 프롬프트 마크다운 파일 경로

        Returns:
            추출된 프롬프트 텍스트
        """
        content = prompt_file.read_text(encoding='utf-8')

        # 메인 프롬프트 블록 찾기 (코드 블록 내부)
        start_marker = "[Sora 2 Prompt - Duration: 90 seconds"
        end_marker = "=== END ==="

        start_idx = content.find(start_marker)
        if start_idx == -1:
            raise ValueError(f"프롬프트 시작 마커를 찾을 수 없습니다: {start_marker}")

        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            raise ValueError(f"프롬프트 종료 마커를 찾을 수 없습니다: {end_marker}")

        prompt = content[start_idx:end_idx].strip()

        print(f"✅ 프롬프트 추출 완료 (길이: {len(prompt)} 문자)")
        return prompt

    def generate_video(
        self,
        prompt: str,
        duration: int = 90,
        aspect_ratio: str = "16:9",
        quality: str = "high",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Sora 2를 사용하여 비디오 생성

        Args:
            prompt: 비디오 생성 프롬프트
            duration: 비디오 길이 (초)
            aspect_ratio: 화면 비율
            quality: 품질 설정
            **kwargs: 추가 파라미터

        Returns:
            생성된 비디오 정보
        """
        print(f"\n🎬 Sora 2 비디오 생성 시작...")
        print(f"   - Duration: {duration}초")
        print(f"   - Aspect Ratio: {aspect_ratio}")
        print(f"   - Quality: {quality}")

        # Sora 2 API 파라미터 구성
        # 주의: 실제 Sora 2 API 스펙에 맞게 수정 필요
        sora_params = {
            "model": "sora-2",  # 또는 실제 모델명
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "fps": kwargs.get("fps", 24),
            **kwargs
        }

        try:
            # 참고: 이 API는 현재 실제 Sora 2 API가 공개되지 않았으므로
            # 가상의 엔드포인트입니다. 실제 사용 시 OpenAI 공식 문서를 참조하세요.

            # Option 1: OpenAI의 통합 API 사용 (예상)
            response = self.client.videos.create(**sora_params)

            # 생성 작업이 비동기일 경우 폴링
            if hasattr(response, 'id'):
                print(f"📤 생성 요청 ID: {response.id}")
                return self._poll_video_status(response.id)

            return response

        except Exception as e:
            print(f"❌ 비디오 생성 중 오류 발생: {e}")
            print(f"\n💡 참고: Sora 2 API가 아직 공개되지 않았을 수 있습니다.")
            print(f"   OpenAI의 공식 Sora API 문서를 확인하세요:")
            print(f"   https://platform.openai.com/docs/")
            raise

    def _poll_video_status(self, video_id: str, max_wait: int = 600) -> Dict[str, Any]:
        """
        비디오 생성 상태 폴링

        Args:
            video_id: 비디오 생성 작업 ID
            max_wait: 최대 대기 시간 (초)

        Returns:
            완성된 비디오 정보
        """
        print(f"\n⏳ 비디오 생성 중... (최대 {max_wait}초 대기)")

        start_time = time.time()
        dots = 0

        while time.time() - start_time < max_wait:
            try:
                # 상태 확인 (실제 API에 맞게 수정 필요)
                status = self.client.videos.retrieve(video_id)

                if status.status == "completed":
                    elapsed = int(time.time() - start_time)
                    print(f"\n✅ 비디오 생성 완료! (소요 시간: {elapsed}초)")
                    return status

                elif status.status == "failed":
                    raise Exception(f"비디오 생성 실패: {status.error}")

                # 진행 중
                dots = (dots + 1) % 4
                print(f"\r   진행 중{'.' * dots}{' ' * (3 - dots)}", end='', flush=True)
                time.sleep(5)

            except Exception as e:
                print(f"\n❌ 상태 확인 중 오류: {e}")
                raise

        raise TimeoutError(f"비디오 생성이 {max_wait}초 내에 완료되지 않았습니다.")

    def download_video(self, video_url: str, output_path: Path) -> Path:
        """
        생성된 비디오 다운로드

        Args:
            video_url: 비디오 URL
            output_path: 저장 경로

        Returns:
            저장된 파일 경로
        """
        print(f"\n💾 비디오 다운로드 중...")

        import requests

        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        print(f"\r   진행률: {percent}%", end='', flush=True)

        print(f"\n✅ 다운로드 완료: {output_path}")
        return output_path

    def create_metadata(self, video_info: Dict[str, Any], output_path: Path):
        """
        비디오 메타데이터 JSON 파일 생성

        Args:
            video_info: 비디오 정보
            output_path: 저장 경로
        """
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "model": "sora-2",
            "project": "NERDX APEC MVP",
            "content": "Sam Altman - Bulguksa Temple Journey",
            "video_info": video_info,
            "prompt_file": "bulguksa_sam_altman_prompt.md"
        }

        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"📄 메타데이터 저장: {metadata_path}")


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="Sora 2를 사용하여 샘 올트먼의 경주 불국사 소개 영상 생성"
    )
    parser.add_argument(
        "--prompt-file",
        type=Path,
        default=Path("bulguksa_sam_altman_prompt.md"),
        help="프롬프트 마크다운 파일 경로"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/bulguksa_sam_altman.mp4"),
        help="출력 비디오 파일 경로"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API Key (환경변수 OPENAI_API_KEY 사용 가능)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=90,
        help="비디오 길이 (초)"
    )
    parser.add_argument(
        "--quality",
        type=str,
        choices=["low", "medium", "high", "maximum"],
        default="high",
        help="비디오 품질"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제로 생성하지 않고 프롬프트만 출력"
    )

    args = parser.parse_args()

    # 배너 출력
    print("=" * 70)
    print("🎬 NERDX APEC MVP - Sora 2 Video Generator")
    print("   Sam Altman's Bulguksa Temple Journey")
    print("=" * 70)

    # 프롬프트 파일 확인
    if not args.prompt_file.exists():
        print(f"❌ 프롬프트 파일을 찾을 수 없습니다: {args.prompt_file}")
        return 1

    try:
        # Generator 초기화
        generator = SoraVideoGenerator(api_key=args.api_key)

        # 프롬프트 추출
        prompt = generator.extract_main_prompt(args.prompt_file)

        if args.dry_run:
            print("\n" + "=" * 70)
            print("📝 추출된 프롬프트:")
            print("=" * 70)
            print(prompt)
            print("=" * 70)
            print("\n💡 --dry-run 모드: 실제 생성은 하지 않았습니다.")
            return 0

        # 비디오 생성
        video_info = generator.generate_video(
            prompt=prompt,
            duration=args.duration,
            quality=args.quality,
            # CAMEO 설정
            cameo_integration={
                "enabled": True,
                "character_name": "Sam Altman",
                "face_reference_urls": [
                    "https://storage.nerdx.com/references/sam_altman_ref1.jpg",
                    "https://storage.nerdx.com/references/sam_altman_ref2.jpg"
                ],
                "performance_style": "documentary_natural",
                "blend_quality": "seamless"
            },
            # 기타 설정
            aspect_ratio="16:9",
            fps=24,
            style_consistency=True,
            cultural_sensitivity="high"
        )

        # 비디오 다운로드
        if hasattr(video_info, 'url'):
            output_path = generator.download_video(video_info.url, args.output)
            generator.create_metadata(video_info, output_path)

            print("\n" + "=" * 70)
            print("🎉 모든 작업 완료!")
            print(f"📹 비디오: {output_path}")
            print(f"📄 메타데이터: {output_path.with_suffix('.json')}")
            print("=" * 70)

        return 0

    except ValueError as e:
        print(f"\n❌ 설정 오류: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
