"""
Gemini API Service
Direct integration with Google Gemini 2.0 Flash Thinking
"""
import logging
import json
from typing import Dict, Any, Optional, List
import httpx
from config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service for interacting with Google Gemini API

    Uses Gemini 2.0 Flash Thinking for:
    - Strategic planning
    - PRD generation
    - Code review
    - Requirements analysis
    """

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.api_base = "https://generativelanguage.googleapis.com/v1beta"
        self.http_client = httpx.AsyncClient(timeout=120.0)

    async def close(self):
        """Cleanup resources"""
        await self.http_client.aclose()

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 8192,
        response_format: str = "text"  # "text" or "json"
    ) -> str:
        """
        Generate content using Gemini

        Args:
            prompt: User prompt
            system_instruction: System instructions (optional)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum response tokens
            response_format: Response format (text or json)

        Returns:
            Generated content as string
        """
        try:
            url = f"{self.api_base}/models/{self.model}:generateContent?key={self.api_key}"

            contents = []

            # Add system instruction if provided
            if system_instruction:
                contents.append({
                    "role": "user",
                    "parts": [{"text": system_instruction}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Understood. I will follow these instructions."}]
                })

            # Add user prompt
            contents.append({
                "role": "user",
                "parts": [{"text": prompt}]
            })

            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.95,
                    "topK": 40
                }
            }

            # Add JSON mode if requested
            if response_format == "json":
                payload["generationConfig"]["responseMimeType"] = "application/json"

            logger.debug(f"Calling Gemini API: {self.model}")

            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()

            # Extract text from response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]

            logger.error(f"Unexpected Gemini response format: {result}")
            raise ValueError("Invalid response format from Gemini")

        except httpx.HTTPError as e:
            logger.error(f"Gemini API HTTP error: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response body: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def generate_structured_output(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output

        Args:
            prompt: User prompt
            system_instruction: System instructions
            schema: Expected JSON schema (optional)
            temperature: Sampling temperature

        Returns:
            Parsed JSON object
        """
        try:
            # Add schema to system instruction if provided
            full_system = system_instruction or ""
            if schema:
                full_system += f"\n\nExpected output schema:\n{json.dumps(schema, indent=2)}"

            full_system += "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no explanations, just pure JSON."

            response_text = await self.generate_content(
                prompt=prompt,
                system_instruction=full_system,
                temperature=temperature,
                max_tokens=8192,
                response_format="json"
            )

            # Parse JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to extract JSON from markdown code blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                    return json.loads(json_text)
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                    return json.loads(json_text)
                else:
                    logger.error(f"Failed to parse JSON: {response_text}")
                    raise

        except Exception as e:
            logger.error(f"Structured output generation failed: {e}")
            raise

    async def analyze_multimodal(
        self,
        prompt: str,
        images: List[str] = [],  # Base64 encoded images or URLs
        system_instruction: Optional[str] = None,
        temperature: float = 1.0
    ) -> str:
        """
        Analyze multimodal content (text + images)

        Args:
            prompt: Text prompt
            images: List of base64 images or URLs
            system_instruction: System instructions
            temperature: Sampling temperature

        Returns:
            Analysis result
        """
        try:
            url = f"{self.api_base}/models/{self.model}:generateContent?key={self.api_key}"

            parts = [{"text": prompt}]

            # Add images
            for img in images:
                if img.startswith("http"):
                    # URL image
                    parts.append({
                        "fileData": {
                            "mimeType": "image/jpeg",
                            "fileUri": img
                        }
                    })
                else:
                    # Base64 image
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img
                        }
                    })

            contents = []

            if system_instruction:
                contents.append({
                    "role": "user",
                    "parts": [{"text": system_instruction}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Understood."}]
                })

            contents.append({
                "role": "user",
                "parts": parts
            })

            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 8192
                }
            }

            response = await self.http_client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()

            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]

            raise ValueError("Invalid response format")

        except Exception as e:
            logger.error(f"Multimodal analysis failed: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            await self.generate_content("Hello", max_tokens=10)
            return True
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False


# Global instance
gemini_service = GeminiService()
