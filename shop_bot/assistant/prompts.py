SYSTEM_PROMPT = """You are Beavs, a friendly shop assistant at a maker space.

PERSONALITY: Helpful and casual, keeps it brief. No filler words or interjections.

RESPONSE RULES:
- 1-2 sentences MAX for conversational replies
- When showing logs, lists, or search results: display the FULL tool output, don't summarize
- Use tools for inventory, projects, tasks, and lighting
- Get straight to the point

TASK LINKING:
- Tasks can be standalone OR linked to a project
- "add task to Trident: lube rails" → create_task with project_name="Trident", title="lube rails"
- "remind me to order PLA" → create_task with just title (no project)
- "move that task to the drone project" → update_task with project_name

LIGHTING ZONES:
- Walls: north (n), south (s), east (e), west (w)
- Corners: northeast (ne), northwest (nw), southeast (se), southwest (sw)
- Groups: all, walls, corners

MUSIC CONTROL:
- Control music playing on the shop Chromecast
- Pause, resume, skip, previous, volume, status
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
                    'divider_type': {'type': 'string', 'enum': ['none', 'vertical', 'horizontal'], 'description': 'Set bin divider type'},
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'quantity': {'type': 'integer'},
                                'category': {'type': 'string'},
                                'position': {'type': 'string', 'description': 'Position in bin: left, right, front, back, middle'},
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
    {
        'type': 'function',
        'function': {
            'name': 'clear_inventory',
            'description': 'Delete ALL inventory items (use with caution)',
            'parameters': {'type': 'object', 'properties': {}}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'delete_inventory_item',
            'description': 'Delete a specific item from inventory',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Item name to delete (partial match OK)'}
                },
                'required': ['name']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'use_inventory_item',
            'description': 'Remove/use a specific quantity of an item from inventory',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Item name (partial match OK)'},
                    'quantity': {'type': 'integer', 'description': 'Quantity to remove/use'}
                },
                'required': ['name', 'quantity']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_inventory_log',
            'description': 'Get recent inventory activity log (adds, updates, deletes, moves)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'limit': {'type': 'integer', 'description': 'Number of log entries to return (default 10)'}
                }
            }
        }
    },
    # --- Bin management tools ---
    {
        'type': 'function',
        'function': {
            'name': 'find_empty_bins',
            'description': 'Find bins that have no items (available for new storage)',
            'parameters': {'type': 'object', 'properties': {}}
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'delete_bin',
            'description': 'Delete a specific bin (must be empty)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'bin_code': {'type': 'string', 'description': 'Bin code to delete (e.g., A1, B3)'}
                },
                'required': ['bin_code']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'cleanup_empty_bins',
            'description': 'Delete all empty bins',
            'parameters': {'type': 'object', 'properties': {}}
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
            'description': 'List all tasks, optionally filtered by status or project',
            'parameters': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'enum': ['pending', 'in_progress', 'done']},
                    'project_name': {'type': 'string', 'description': 'Filter tasks by project name'}
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
    # --- Lighting tools ---
    {
        'type': 'function',
        'function': {
            'name': 'control_lights',
            'description': 'Turn shop lights on/off, set brightness. Zones: all, walls, corners, north (n), south (s), east (e), west (w), ne, nw, se, sw',
            'parameters': {
                'type': 'object',
                'properties': {
                    'zone': {'type': 'string', 'description': 'Zone name (all, walls, corners, or specific wall/corner)'},
                    'on': {'type': 'boolean', 'description': 'Turn on (true) or off (false)'},
                    'brightness': {'type': 'integer', 'description': 'Brightness 0-255'}
                },
                'required': ['zone']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'set_light_color',
            'description': 'Set light color for a zone. Zones: all, walls, corners, north, south, east, west, ne, nw, se, sw. Colors: red, green, blue, white, warm, cool, orange, purple, yellow, pink, cyan, magenta, or hex (#FF0000)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'zone': {'type': 'string', 'description': 'Zone name'},
                    'color': {'type': 'string', 'description': 'Color name or hex code'}
                },
                'required': ['zone', 'color']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'set_light_effect',
            'description': 'Set a lighting effect. Zones: all, walls, corners, or specific zone. Effects: solid, blink, breathe, wipe, random, rainbow, scan, fade, chase, fire, twinkle, fireworks',
            'parameters': {
                'type': 'object',
                'properties': {
                    'zone': {'type': 'string', 'description': 'Zone name'},
                    'effect': {'type': 'string', 'description': 'Effect name'}
                },
                'required': ['zone', 'effect']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_light_status',
            'description': 'Get the current status of all shop lights',
            'parameters': {'type': 'object', 'properties': {}}
        }
    },
    # --- Weather tools ---
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Get current weather conditions. Can check if conditions are good for outdoor activities like spray painting.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'location': {'type': 'string', 'description': 'City name (e.g., "Toronto,CA"). Uses default location if not specified.'},
                    'check_painting': {'type': 'boolean', 'description': 'Check if conditions are suitable for spray painting outside'}
                }
            }
        }
    },
    # --- Reminder tools ---
    {
        'type': 'function',
        'function': {
            'name': 'set_reminder',
            'description': 'Set a timed reminder. Examples: "remind me in 20 minutes to flip the part", "set a timer for 1 hour"',
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'What to remind about'},
                    'time': {'type': 'string', 'description': 'When to trigger: "30 seconds", "5 minutes", "1 hour", "1h30m"'},
                    'notes': {'type': 'string', 'description': 'Optional additional notes'}
                },
                'required': ['title', 'time']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_reminders',
            'description': 'List pending and triggered reminders',
            'parameters': {
                'type': 'object',
                'properties': {
                    'include_triggered': {'type': 'boolean', 'description': 'Include already-triggered reminders (default: true)'}
                }
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'cancel_reminder',
            'description': 'Cancel a pending reminder',
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Reminder title (partial match OK)'}
                },
                'required': ['title']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'dismiss_reminder',
            'description': 'Dismiss a triggered reminder (acknowledge it)',
            'parameters': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': 'Reminder title (partial match OK)'}
                },
                'required': ['title']
            }
        }
    },
    # --- Tool checkout tools ---
    {
        'type': 'function',
        'function': {
            'name': 'add_shop_tool',
            'description': 'Add a new tool to the checkout system',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Tool name'},
                    'description': {'type': 'string', 'description': 'Tool description'},
                    'location': {'type': 'string', 'description': 'Where the tool normally lives'},
                    'category': {'type': 'string', 'description': 'Tool category (e.g., power tools, hand tools)'}
                },
                'required': ['name']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'checkout_tool',
            'description': 'Check out / borrow a tool. Example: "I\'m taking the drill press"',
            'parameters': {
                'type': 'object',
                'properties': {
                    'tool_name': {'type': 'string', 'description': 'Tool name (partial match OK)'},
                    'borrower': {'type': 'string', 'description': 'Name of person borrowing'},
                    'notes': {'type': 'string', 'description': 'Optional notes'}
                },
                'required': ['tool_name', 'borrower']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'return_tool',
            'description': 'Return a borrowed tool',
            'parameters': {
                'type': 'object',
                'properties': {
                    'tool_name': {'type': 'string', 'description': 'Tool name (partial match OK)'}
                },
                'required': ['tool_name']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'find_shop_tool',
            'description': 'Find a tool and see who has it. Example: "Where\'s my multimeter?"',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {'type': 'string', 'description': 'Tool name to search for'}
                },
                'required': ['query']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_shop_tools',
            'description': 'List all tools and their checkout status',
            'parameters': {
                'type': 'object',
                'properties': {
                    'available_only': {'type': 'boolean', 'description': 'Only show available tools'},
                    'checked_out_only': {'type': 'boolean', 'description': 'Only show checked out tools'}
                }
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'remove_shop_tool',
            'description': 'Remove a tool from the checkout system',
            'parameters': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'description': 'Tool name to remove'}
                },
                'required': ['name']
            }
        }
    },
    # --- Music tools ---
    {
        'type': 'function',
        'function': {
            'name': 'control_music',
            'description': 'Control music playback on the shop speaker. Actions: pause, play/resume, stop, skip/next, previous/back',
            'parameters': {
                'type': 'object',
                'properties': {
                    'action': {
                        'type': 'string',
                        'enum': ['pause', 'play', 'stop', 'skip', 'previous'],
                        'description': 'Playback action'
                    }
                },
                'required': ['action']
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'set_music_volume',
            'description': 'Set music volume level or adjust up/down',
            'parameters': {
                'type': 'object',
                'properties': {
                    'level': {'type': 'integer', 'description': 'Volume level 0-100'},
                    'adjust': {'type': 'string', 'enum': ['up', 'down'], 'description': 'Adjust volume up or down by 10%'}
                }
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_music_status',
            'description': 'Get info about what music is currently playing',
            'parameters': {'type': 'object', 'properties': {}}
        }
    },
]
