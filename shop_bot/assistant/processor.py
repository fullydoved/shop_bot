from .claude_client import ClaudeClient
from .prompts import SYSTEM_PROMPT, TOOL_DEFINITIONS
from .commands import COMMAND_HANDLERS

# Tools that return data to display directly (don't let Claude summarize)
DISPLAY_TOOLS = {
    'get_inventory_log',
    'find_inventory',
    'list_projects',
    'list_tasks',
    'get_pending_tasks',
    'get_light_status',
    'get_music_status',
}


class InputProcessor:
    """
    Unified input processor for all interfaces (CLI, web, voice).
    Handles natural language input and returns responses via Claude API.
    """

    # Keep last N messages to control token usage
    MAX_HISTORY_MESSAGES = 10

    def __init__(self):
        self.client = ClaudeClient()
        self.conversation_history = []

    def _trim_history(self):
        """Keep only recent messages to control token costs.

        Be careful not to cut in the middle of a tool use sequence.
        """
        if len(self.conversation_history) <= self.MAX_HISTORY_MESSAGES:
            return

        # Start from the trim point and find a safe place to cut
        # (should be at a user message that's not a tool_result)
        trimmed = self.conversation_history[-self.MAX_HISTORY_MESSAGES:]

        # If first message is a tool_result or assistant, we need to go back further
        # to find a clean user message start
        while trimmed and len(trimmed) > 2:
            first = trimmed[0]
            if first.get('role') == 'user':
                content = first.get('content')
                # Check if it's a tool_result (list of dicts with 'type': 'tool_result')
                if isinstance(content, list) and content and isinstance(content[0], dict) and content[0].get('type') == 'tool_result':
                    trimmed = trimmed[1:]  # Skip this, it's orphaned
                else:
                    break  # Good, it's a regular user message
            else:
                trimmed = trimmed[1:]  # Skip orphaned assistant message

        self.conversation_history = trimmed

    def _execute_tool_calls(self, tool_calls: list) -> list:
        """Execute tool calls and return results."""
        results = []
        for tool_call in tool_calls:
            func_name = tool_call['function']['name']
            func_args = tool_call['function']['arguments']
            tool_id = tool_call.get('id', 'unknown')

            if func_name in COMMAND_HANDLERS:
                try:
                    result = COMMAND_HANDLERS[func_name](**func_args)
                    results.append({
                        'tool_id': tool_id,
                        'result': result,
                        'success': True
                    })
                except Exception as e:
                    results.append({
                        'tool_id': tool_id,
                        'result': f"Error: {str(e)}",
                        'success': False
                    })
            else:
                results.append({
                    'tool_id': tool_id,
                    'result': f"Unknown tool: {func_name}",
                    'success': False
                })

        return results

    def process(self, user_input: str) -> str:
        """
        Process user input and return a response.
        This is the main entry point used by all interfaces.
        """
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_input
        })

        # Trim history to control costs
        self._trim_history()

        try:
            # Send to Claude with tools
            response = self.client.chat(
                messages=self.conversation_history,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS
            )

            # Check for tool calls
            tool_calls = self.client.get_tool_calls(response)

            if tool_calls:
                # Execute tools
                tool_results = self._execute_tool_calls(tool_calls)

                # Check if any tools are display tools (output shown directly)
                display_outputs = []
                for tc, tr in zip(tool_calls, tool_results):
                    func_name = tc['function']['name']
                    if func_name in DISPLAY_TOOLS and tr['result']:
                        display_outputs.append(tr['result'])

                # Add assistant's tool use to history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response.content
                })

                # Add tool results to history
                tool_result_content = []
                for tc, tr in zip(tool_calls, tool_results):
                    # Ensure content is never empty (API requirement)
                    result_content = tr['result'] if tr['result'] else "Done"
                    tool_result_content.append({
                        'type': 'tool_result',
                        'tool_use_id': tc.get('id'),
                        'content': str(result_content)
                    })

                self.conversation_history.append({
                    'role': 'user',
                    'content': tool_result_content
                })

                # Get Claude's final response after tool execution
                final_response = self.client.chat(
                    messages=self.conversation_history,
                    system=SYSTEM_PROMPT,
                    tools=TOOL_DEFINITIONS
                )

                final_text = self.client.get_response_text(final_response) or "Done, eh!"

                # Add final response to history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': final_text
                })

                # For display tools, append the raw output after Claude's response
                if display_outputs:
                    final_text = final_text + "\n\n" + "\n\n".join(display_outputs)

                return final_text

            else:
                # Regular text response (no tools)
                response_text = self.client.get_response_text(response) or "I'm here, bud!"
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response_text
                })
                return response_text

        except Exception as e:
            error_msg = f"Sorry, I ran into an issue: {str(e)}"
            return error_msg

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
