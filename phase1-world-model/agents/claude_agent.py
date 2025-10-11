"""
Claude Agent - Structured and secure task execution

Claude excels at:
- Code quality and structure
- Security-critical operations
- Long context understanding
- API schema design
- Precise instructions

Use for: Core architecture, database operations, security implementations
"""
from anthropic import Anthropic, AnthropicError
from typing import List, Dict, Any, Optional, Literal
from config import settings
import logging
import json

logger = logging.getLogger(__name__)


class ClaudeAgent:
    """Claude AI Agent for structured, secure tasks"""

    def __init__(self, model: Optional[str] = None):
        """
        Initialize Claude agent

        Args:
            model: Claude model to use (defaults to settings)
        """
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = model or settings.claude_model
        logger.info(f"Initialized Claude agent with model: {self.model}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        response_format: Literal["text", "json"] = "text"
    ) -> Dict[str, Any]:
        """
        Generate response from Claude

        Args:
            prompt: User prompt
            system_prompt: System instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            response_format: Output format

        Returns:
            Response dict with content, usage, model info
        """
        try:
            # Prepare system prompt
            system = system_prompt or "You are a helpful, precise AI assistant."

            # Add JSON formatting instruction if needed
            if response_format == "json":
                system += "\n\nIMPORTANT: You must respond with valid JSON only. No markdown, no code blocks, just pure JSON."
                prompt += "\n\nReturn your response as valid JSON."

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract content
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            # Parse JSON if requested
            if response_format == "json":
                try:
                    parsed_content = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Claude returned invalid JSON, attempting to extract")
                    # Try to extract JSON from markdown code block
                    if "```json" in content:
                        content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        content = content.split("```")[1].split("```")[0].strip()
                    parsed_content = json.loads(content)

                content = parsed_content

            return {
                "content": content,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "stop_reason": response.stop_reason,
                "agent": "claude"
            }

        except AnthropicError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Claude generation error: {e}")
            raise

    async def design_api_schema(
        self,
        description: str,
        requirements: List[str],
        existing_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use Claude to design API schemas

        Claude is excellent at structured, secure API design

        Args:
            description: What the API should do
            requirements: List of requirements
            existing_schema: Existing schema to extend (optional)

        Returns:
            API schema design
        """
        system_prompt = """You are an expert API architect specializing in secure, well-structured RESTful and GraphQL APIs.
Your designs follow best practices for:
- Security (authentication, authorization, input validation)
- Performance (caching, pagination, rate limiting)
- Developer experience (clear naming, consistent structure)
- Scalability (stateless design, efficient data models)
"""

        prompt = f"""Design an API schema for the following:

Description: {description}

Requirements:
{chr(10).join(f"- {req}" for req in requirements)}

{"Existing Schema to Extend:" + json.dumps(existing_schema, indent=2) if existing_schema else ""}

Provide:
1. Endpoint definitions
2. Request/response models
3. Authentication requirements
4. Error handling
5. Rate limiting suggestions

Return as JSON with structure:
{{
    "endpoints": [...],
    "models": {{...}},
    "auth": {{...}},
    "errors": [...],
    "rate_limits": {{...}}
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower for more consistent structure
            response_format="json"
        )

        return response["content"]

    async def analyze_security(
        self,
        code: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze code for security vulnerabilities

        Claude has strong security analysis capabilities

        Args:
            code: Code to analyze
            context: Additional context about the code

        Returns:
            Security analysis with vulnerabilities and recommendations
        """
        system_prompt = """You are a security expert specializing in code review and vulnerability detection.
Analyze code for:
- SQL injection
- XSS vulnerabilities
- Authentication/authorization flaws
- Data exposure risks
- Rate limiting issues
- Input validation problems
"""

        prompt = f"""Analyze this code for security vulnerabilities:

{f"Context: {context}" if context else ""}

Code:
```
{code}
```

Return a security analysis as JSON:
{{
    "risk_level": "low|medium|high|critical",
    "vulnerabilities": [
        {{
            "type": "vulnerability type",
            "severity": "low|medium|high|critical",
            "location": "code location",
            "description": "what's wrong",
            "recommendation": "how to fix"
        }}
    ],
    "passed_checks": ["check1", "check2"],
    "overall_score": 0-100
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,  # Very low for consistent security analysis
            response_format="json"
        )

        return response["content"]

    async def generate_database_query(
        self,
        intent: str,
        schema: Dict[str, Any],
        query_language: Literal["cypher", "sql"] = "cypher"
    ) -> Dict[str, Any]:
        """
        Generate optimized database queries

        Claude is excellent at Cypher and SQL generation

        Args:
            intent: What the query should do
            schema: Database schema
            query_language: Query language to use

        Returns:
            Query with explanation
        """
        system_prompt = f"""You are a database expert specializing in {query_language.upper()} query optimization.
Generate efficient, secure queries that:
- Use proper indexing
- Avoid N+1 problems
- Include proper filtering
- Use parameterized queries (no SQL/Cypher injection)
"""

        prompt = f"""Generate a {query_language.upper()} query for:

Intent: {intent}

Schema:
{json.dumps(schema, indent=2)}

Return as JSON:
{{
    "query": "the query",
    "parameters": {{"param1": "value1"}},
    "explanation": "how it works",
    "performance_notes": "optimization notes",
    "estimated_complexity": "O(...)"
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            response_format="json"
        )

        return response["content"]

    async def review_code(
        self,
        code: str,
        language: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive code review

        Claude excels at thorough, thoughtful code reviews

        Args:
            code: Code to review
            language: Programming language
            context: Additional context

        Returns:
            Code review with suggestions
        """
        system_prompt = f"""You are a senior software engineer conducting a code review.
Review for:
- Code quality and readability
- Best practices for {language}
- Performance optimization opportunities
- Potential bugs
- Testing suggestions
- Documentation quality

Be constructive and specific in feedback.
"""

        prompt = f"""Review this {language} code:

{f"Context: {context}" if context else ""}

Code:
```{language}
{code}
```

Return review as JSON:
{{
    "overall_rating": "excellent|good|fair|poor",
    "strengths": ["strength1", "strength2"],
    "improvements": [
        {{
            "category": "performance|readability|security|etc",
            "priority": "high|medium|low",
            "issue": "what needs improvement",
            "suggestion": "specific recommendation",
            "code_example": "example fix (optional)"
        }}
    ],
    "bugs": [...],
    "testing_recommendations": [...],
    "summary": "overall assessment"
}}
"""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            response_format="json"
        )

        return response["content"]


# Singleton instance
_claude_agent: Optional[ClaudeAgent] = None


def get_claude_agent() -> ClaudeAgent:
    """Get Claude agent singleton"""
    global _claude_agent
    if _claude_agent is None:
        _claude_agent = ClaudeAgent()
    return _claude_agent
