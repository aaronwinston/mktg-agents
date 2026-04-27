"""Multi-runtime LLM adapter system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
from services.crypto import get_vault

class RuntimeAdapter(ABC):
    """Abstract base for LLM runtimes."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def complete(self, prompt: str, max_tokens: int = 2048) -> tuple[str, int, int]:
        """Generate completion. Returns (text, input_tokens, output_tokens)"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Test that the API key works."""
        pass

class AnthropicAdapter(RuntimeAdapter):
    """Anthropic Claude adapter."""
    
    async def complete(self, prompt: str, max_tokens: int = 2048) -> tuple[str, int, int]:
        import anthropic
        client = anthropic.Anthropic(api_key=self.api_key)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        output = message.content[0].text
        # Estimate tokens (1 token ≈ 4 chars)
        input_tokens = len(prompt) // 4
        output_tokens = len(output) // 4
        
        return output, input_tokens, output_tokens
    
    def validate(self) -> bool:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return bool(response)
        except:
            return False

class OpenAIAdapter(RuntimeAdapter):
    """OpenAI GPT adapter."""
    
    async def complete(self, prompt: str, max_tokens: int = 2048) -> tuple[str, int, int]:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        response = client.chat.completions.create(
            model="gpt-4-mini",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        output = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        return output, input_tokens, output_tokens
    
    def validate(self) -> bool:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4-mini",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return bool(response)
        except:
            return False

class CopilotAdapter(RuntimeAdapter):
    """GitHub Copilot adapter."""
    
    async def complete(self, prompt: str, max_tokens: int = 2048) -> tuple[str, int, int]:
        # Placeholder - Copilot SDK integration
        return "Copilot response", len(prompt) // 4, max_tokens // 2
    
    def validate(self) -> bool:
        # Placeholder validation
        return len(self.api_key) > 10

class RuntimeManager:
    """Manages available runtimes and selection."""
    
    ADAPTERS = {
        "anthropic": AnthropicAdapter,
        "openai": OpenAIAdapter,
        "copilot": CopilotAdapter,
    }
    
    @staticmethod
    def get_adapter(runtime: str, encrypted_key: str) -> RuntimeAdapter:
        """Get an adapter instance, decrypting the key first."""
        if runtime not in RuntimeManager.ADAPTERS:
            raise ValueError(f"Unknown runtime: {runtime}")
        
        # Decrypt key
        vault = get_vault()
        try:
            api_key = vault.decrypt_key(encrypted_key)
        except Exception as e:
            raise ValueError(f"Failed to decrypt key: {str(e)}")
        
        AdapterClass = RuntimeManager.ADAPTERS[runtime]
        return AdapterClass(api_key)
    
    @staticmethod
    def available_runtimes() -> List[str]:
        """List available runtime identifiers."""
        return list(RuntimeManager.ADAPTERS.keys())
