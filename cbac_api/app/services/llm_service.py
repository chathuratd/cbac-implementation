"""
LLM Service for generating behavioral statements using Azure OpenAI.

Supports:
- Statement generation from behavior texts
- Prompt engineering for consistency
- Error handling with fallback
"""

import logging
from typing import List, Optional
from openai import AzureOpenAI
from app.config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-based generalized statement generation"""
    
    def __init__(self):
        """Initialize Azure OpenAI client"""
        try:
            self.client = AzureOpenAI(
                api_key=settings.OPENAI_API_KEY,
                api_version="2024-02-15-preview",
                azure_endpoint=settings.OPENAI_API_BASE
            )
            # Try common deployment names - make configurable via settings
            self.deployment_name = getattr(settings, 'OPENAI_DEPLOYMENT_NAME', 'gpt-4')
            logger.info(f"LLM Service initialized successfully with deployment: {self.deployment_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Service: {e}")
            self.client = None
    
    def generate_statement(
        self,
        behavior_texts: List[str],
        domain: str,
        max_tokens: int = 100,
        temperature: float = 0.3
    ) -> Optional[str]:
        """
        Generate a generalized statement from behavior texts using LLM.
        
        Args:
            behavior_texts: List of behavior text strings
            domain: Detected domain for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0, lower = more consistent)
            
        Returns:
            Generated statement or None if failed
        """
        if not self.client:
            logger.error("LLM client not initialized")
            return None
        
        if not behavior_texts:
            logger.warning("No behavior texts provided for LLM generation")
            return None
        
        try:
            prompt = self._build_prompt(behavior_texts, domain)
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing user behavior patterns and creating concise, specific summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            statement = response.choices[0].message.content.strip()
            
            # Clean up the response (remove quotes if LLM added them)
            statement = statement.strip('"').strip("'").strip()
            
            logger.info(f"LLM generated statement: {statement}")
            return statement
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            return None
    
    def _build_prompt(self, behavior_texts: List[str], domain: str) -> str:
        """
        Build optimized prompt for statement generation.
        
        Prompt engineering principles:
        - Clear task definition
        - Specific constraints
        - Examples of good/bad outputs
        - Structured input format
        
        Args:
            behavior_texts: List of behavior texts
            domain: Domain context
            
        Returns:
            Formatted prompt string
        """
        # Limit to 10 most recent behaviors to avoid token overflow
        texts_sample = behavior_texts[:10]
        
        texts_formatted = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts_sample)])
        
        prompt = f"""Analyze the following user behaviors and create ONE concise generalized statement that captures the common pattern.

Domain Context: {domain}

Observed Behaviors:
{texts_formatted}

Task: Generate a single statement (15-25 words) that:
1. Describes what the user SPECIFICALLY does (use actual keywords from behaviors)
2. Focuses on the action and subject matter (not just "demonstrates interest")
3. Uses present tense and active voice
4. Is specific enough to be meaningful but general enough to cover all behaviors
5. Avoids generic phrases like "shows engagement" or "exhibits understanding"

Good Examples:
- "User frequently requests simple egg-based breakfast recipes with step-by-step instructions"
- "User seeks beginner-friendly gardening tips for growing vegetables in small spaces"
- "User asks about weather forecasts and temperature trends for outdoor activity planning"

Bad Examples:
- "User demonstrates deep engagement in cooking at novice level"
- "User shows interest in various topics"
- "User exhibits consistent interaction patterns"

Generate ONLY the statement (no explanations, no quotes):"""
        
        return prompt
    
    def test_connection(self) -> bool:
        """
        Test LLM service connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False
