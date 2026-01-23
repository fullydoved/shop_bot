import ollama
from django.conf import settings


class OllamaClient:
    def __init__(self, host=None, model=None):
        self.host = host or getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434')
        self.model = model or getattr(settings, 'OLLAMA_MODEL', 'llama3.2')
        self.client = ollama.Client(host=self.host)

    def chat(self, messages: list, tools: list = None) -> dict:
        """Send a chat request to Ollama with optional tool definitions."""
        kwargs = {
            'model': self.model,
            'messages': messages,
        }
        if tools:
            kwargs['tools'] = tools

        response = self.client.chat(**kwargs)
        return response

    def get_response_text(self, response: dict) -> str:
        """Extract the text content from an Ollama response."""
        return response.get('message', {}).get('content', '')

    def get_tool_calls(self, response: dict) -> list:
        """Extract tool calls from an Ollama response."""
        return response.get('message', {}).get('tool_calls', [])
