from .claude_client import ClaudeClient
from .prompts import SYSTEM_PROMPT, TOOL_DEFINITIONS
from .commands import COMMAND_HANDLERS


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
        """Keep only recent messages to control token costs."""
        if len(self.conversation_history) > self.MAX_HISTORY_MESSAGES:
            self.conversation_history = self.conversation_history[-self.MAX_HISTORY_MESSAGES:]

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

                # Add assistant's tool use to history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': response.content
                })

                # Add tool results to history
                tool_result_content = []
                for tc, tr in zip(tool_calls, tool_results):
                    tool_result_content.append({
                        'type': 'tool_result',
                        'tool_use_id': tc.get('id'),
                        'content': tr['result']
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

                final_text = self.client.get_response_text(final_response)

                # Add final response to history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': final_text
                })

                return final_text

            else:
                # Regular text response (no tools)
                response_text = self.client.get_response_text(response)
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
