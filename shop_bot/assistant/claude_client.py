import anthropic
from django.conf import settings


class ClaudeClient:
    """Client for interacting with Claude API."""

    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or getattr(settings, 'ANTHROPIC_API_KEY', '')
        self.model = model or getattr(settings, 'CLAUDE_MODEL', 'claude-haiku-4-5-20251001')

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def chat(self, messages: list, system: str = None, tools: list = None) -> dict:
        """
        Send a chat request to Claude.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt
            tools: List of tool definitions

        Returns:
            Claude API response
        """
        kwargs = {
            'model': self.model,
            'max_tokens': 300,
            'messages': messages,
        }

        if system:
            kwargs['system'] = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"}
                }
            ]

        if tools:
            # Convert our tool format to Claude's format
            kwargs['tools'] = self._convert_tools(tools)

        response = self.client.messages.create(**kwargs)
        return response

    def _convert_tools(self, tools: list) -> list:
        """Convert tool definitions to Claude's expected format."""
        claude_tools = []
        for tool in tools:
            if tool.get('type') == 'function':
                func = tool['function']
                claude_tools.append({
                    'name': func['name'],
                    'description': func.get('description', ''),
                    'input_schema': func.get('parameters', {'type': 'object', 'properties': {}})
                })
        # Cache the tools (mark last item with cache_control)
        if claude_tools:
            claude_tools[-1]['cache_control'] = {"type": "ephemeral"}
        return claude_tools

    def get_response_text(self, response) -> str:
        """Extract text content from Claude response."""
        for block in response.content:
            if block.type == 'text':
                return block.text
        return ''

    def get_tool_calls(self, response) -> list:
        """Extract tool use blocks from Claude response."""
        tool_calls = []
        for block in response.content:
            if block.type == 'tool_use':
                tool_calls.append({
                    'id': block.id,
                    'function': {
                        'name': block.name,
                        'arguments': block.input
                    }
                })
        return tool_calls
