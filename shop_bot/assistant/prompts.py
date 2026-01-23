SYSTEM_PROMPT = """You are Beavs, a Canadian shop assistant at a maker space.

PERSONALITY: Friendly hoser, says "eh" and "bud", keeps it brief.

RESPONSE RULES:
- 1-2 sentences MAX
- Use tools for inventory, projects, and tasks
- Get to the point, eh

TASK LINKING:
- Tasks can be standalone OR linked to a project
- "add task to Trident: lube rails" → create_task with project_name="Trident", title="lube rails"
- "remind me to order PLA" → create_task with just title (no project)
- "move that task to the drone project" → update_task with project_name
"""

TOOL_DEFINITIONS = [
    # --- Inventory tools ---
    {
        'type': 'function',
        'function': {
            'name': 'add_inventory_items',
            'description': 'Add one or more items to a bin',
            'parameters': {
                'type': 'object',
                'properties': {
                    'bin_code': {'type': 'string', 'description': 'Bin location code (e.g., A1, B3)'},
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'quantity': {'type': 'integer'},
                                'category': {'type': 'string'},
                            },
                            'required': ['name']
                        }
                    }
                },
                'required': ['bin_code', 'items']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'find_inventory',
            'description': 'Search for items in inventory',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'Search term for item name'}
                },
                'required': ['query']
            }
        }
    },
    # --- Project tools ---
    {
        'type': 'function',
        'function': {
            'name': 'create_project',
            'description': 'Create a new project',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'status': {'type': 'string', 'enum': ['idea', 'active', 'paused'], 'default': 'idea'}
                },
                'required': ['name']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_projects',
            'description': 'List all projects, optionally filtered by status',
            'parameters': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['idea', 'active', 'paused', 'completed'], 'description': 'Filter by status'}
                }
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'update_project',
            'description': 'Update a project (change status, name, or description)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Current project name to find'},
                    'status': {'type': 'string', 'enum': ['idea', 'active', 'paused', 'completed']},
                    'new_name': {'type': 'string', 'description': 'New name for the project'},
                    'description': {'type': 'string'}
                },
                'required': ['name']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'delete_project',
            'description': 'Delete a project',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Project name to delete'}
                },
                'required': ['name']
            }
        }
    },
    # --- Task tools ---
    {
        'type': 'function',
        'function': {
            'name': 'create_task',
            'description': 'Create a new task. Can be standalone or linked to a project. Examples: "remind me to order screws" (standalone), "add task to Trident project: lube the rails" (linked to project)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'What needs to be done'},
                    'priority': {'type': 'string', 'enum': ['low', 'medium', 'high'], 'default': 'medium'},
                    'project_name': {'type': 'string', 'description': 'Project name to attach task to (optional)'},
                    'notes': {'type': 'string', 'description': 'Additional context or notes (e.g., "waiting on parts")'}
                },
                'required': ['title']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_pending_tasks',
            'description': 'Get all pending tasks',
            'parameters': {'type': 'object', 'properties': {}}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_tasks',
            'description': 'List all tasks, optionally filtered by status',
            'parameters': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['pending', 'in_progress', 'done']}
                }
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'complete_task',
            'description': 'Mark a task as done/complete',
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Task title (partial match OK)'}
                },
                'required': ['title']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'update_task',
            'description': 'Update a task: change title, priority, status, notes, or assign/move to a project',
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Current task title to find (partial match OK)'},
                    'new_title': {'type': 'string', 'description': 'New title for the task'},
                    'priority': {'type': 'string', 'enum': ['low', 'medium', 'high']},
                    'status': {'type': 'string', 'enum': ['pending', 'in_progress', 'done']},
                    'project_name': {'type': 'string', 'description': 'Assign task to this project'},
                    'notes': {'type': 'string', 'description': 'Update notes/context for the task'}
                },
                'required': ['title']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'delete_task',
            'description': 'Delete a task',
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Task title to delete (partial match OK)'}
                },
                'required': ['title']
            }
        }
    },
]
