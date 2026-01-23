from inventory.services import add_item, find_items, get_or_create_bin, clear_inventory, delete_item
from projects.services import (
    create_project, list_projects, update_project, delete_project,
    create_task, get_pending_tasks, get_all_tasks, update_task, complete_task, delete_task,
)
from projects.models import Project, Task
from lighting.services import (
    set_zone_power, set_zone_color, set_zone_brightness, set_zone_effect,
    get_light_status, parse_color,
)
from chromecast.services import (
    music_pause, music_play, music_stop, music_skip, music_previous,
    music_volume, music_volume_up, music_volume_down, music_status,
)


def handle_add_inventory_items(bin_code: str, items: list, divider_type: str = None, **kwargs) -> str:
    """Handle adding or updating inventory items in a bin."""
    from inventory.models import InventoryItem
    from inventory.services import set_bin_divider

    bin_obj = get_or_create_bin(bin_code)

    # Set divider type if specified
    if divider_type:
        set_bin_divider(bin_code, divider_type)

    results = []
    for item in items:
        if isinstance(item, dict):
            name = item.get('name', str(item))
            category = item.get('category', '')
            quantity = item.get('quantity')
            position = item.get('position', '')
        else:
            name = str(item)
            category = ''
            quantity = None
            position = ''

        # Check if exists before adding (to report correctly)
        existed = InventoryItem.objects.filter(name__iexact=name, bin=bin_obj).exists()

        inv_item = add_item(
            name=name,
            bin_code=bin_code,
            category=category,
            quantity=quantity,
            position=position,
        )
        action = "updated" if existed else "added"
        pos_info = f" [{inv_item.position}]" if inv_item.position else ""
        results.append(f"{inv_item.name}{pos_info} ({action})")
    return f"Bin {bin_code}: {', '.join(results)}"


def handle_find_inventory(query: str, **kwargs) -> str:
    """Handle searching for inventory items."""
    items = find_items(query)
    if not items:
        return f"No items found matching '{query}'"

    results = []
    for item in items[:10]:
        pos = f" ({item.position})" if item.position else ""
        loc = f"in bin {item.bin.code}{pos}"
        qty = f" - {item.quantity} {item.unit}" if item.quantity else ""
        results.append(f"- {item.name}{qty} {loc}")

    return f"Found {items.count()} item(s):\n" + "\n".join(results)


def handle_clear_inventory(**kwargs) -> str:
    """Handle clearing all inventory items."""
    count = clear_inventory()
    if count == 0:
        return "Inventory was already empty, bud."
    return f"Cleared {count} item(s) from inventory."


def handle_delete_inventory_item(name: str, **kwargs) -> str:
    """Handle deleting a specific inventory item."""
    if delete_item(name=name):
        return f"Deleted '{name}' from inventory."
    return f"Couldn't find '{name}' in inventory."


# --- Project handlers ---

def handle_create_project(name: str, description: str = '', status: str = 'idea', **kwargs) -> str:
    """Handle creating a new project."""
    project = create_project(name, description, status)
    return f"Created project: {project.name} ({project.status})"


def handle_list_projects(status: str = None, **kwargs) -> str:
    """Handle listing projects."""
    projects = list_projects(status)
    if not projects:
        return "No projects found."

    results = []
    for p in projects[:10]:
        task_count = p.tasks.count()
        tasks_info = f" - {task_count} task(s)" if task_count else ""
        results.append(f"- {p.name} [{p.status}]{tasks_info}")

    return f"Projects:\n" + "\n".join(results)


def handle_update_project(name: str, status: str = None, new_name: str = None, description: str = None, **kwargs) -> str:
    """Handle updating a project."""
    project = Project.objects.filter(name__iexact=name).first()
    if not project:
        return f"Project '{name}' not found."

    updates = {}
    if status:
        updates['status'] = status
    if new_name:
        updates['name'] = new_name
    if description is not None:
        updates['description'] = description

    project = update_project(project.id, **updates)
    return f"Updated project: {project.name} [{project.status}]"


def handle_delete_project(name: str, **kwargs) -> str:
    """Handle deleting a project."""
    project = Project.objects.filter(name__iexact=name).first()
    if not project:
        return f"Project '{name}' not found."

    delete_project(project.id)
    return f"Deleted project: {name}"


# --- Task handlers ---

def handle_create_task(title: str, priority: str = 'medium', project_name: str = None, notes: str = '', **kwargs) -> str:
    """Handle creating a new task."""
    task = create_task(title, priority=priority, project_name=project_name)
    if notes:
        task.notes = notes
        task.save()
    project_info = f" for {task.project.name}" if task.project else ""
    return f"Created task: {task.title}{project_info} (priority: {task.priority})"


def handle_get_pending_tasks(**kwargs) -> str:
    """Handle getting pending tasks."""
    tasks = get_pending_tasks()
    if not tasks:
        return "No pending tasks. You're all caught up!"

    results = []
    for task in tasks[:10]:
        project_info = f" [{task.project.name}]" if task.project else ""
        results.append(f"- {task.title}{project_info} ({task.priority})")

    return f"Pending tasks:\n" + "\n".join(results)


def handle_list_tasks(status: str = None, project_name: str = None, **kwargs) -> str:
    """Handle listing all tasks."""
    tasks = get_all_tasks(status, project_name)
    if not tasks:
        if project_name:
            return f"No tasks found for project '{project_name}'."
        return "No tasks found."

    results = []
    for task in tasks[:15]:
        project_info = f" [{task.project.name}]" if task.project else ""
        status_icon = "✓" if task.status == 'done' else "○" if task.status == 'pending' else "►"
        results.append(f"{status_icon} {task.title}{project_info} ({task.priority})")

    return f"Tasks:\n" + "\n".join(results)


def handle_complete_task(title: str, **kwargs) -> str:
    """Handle marking a task as complete."""
    task = Task.objects.filter(title__icontains=title, status__in=['pending', 'in_progress']).first()
    if not task:
        return f"No pending task found matching '{title}'."

    complete_task(task.id)
    return f"Completed task: {task.title}"


def handle_update_task(title: str, new_title: str = None, priority: str = None, status: str = None, project_name: str = None, notes: str = None, **kwargs) -> str:
    """Handle updating a task."""
    task = Task.objects.filter(title__icontains=title).first()
    if not task:
        return f"No task found matching '{title}'."

    updates = {}
    if new_title:
        updates['title'] = new_title
    if priority:
        updates['priority'] = priority
    if status:
        updates['status'] = status
    if project_name is not None:
        updates['project_name'] = project_name
    if notes is not None:
        updates['notes'] = notes

    task = update_task(task.id, **updates)
    return f"Updated task: {task.title} [{task.status}] ({task.priority})"


def handle_delete_task(title: str, **kwargs) -> str:
    """Handle deleting a task."""
    task = Task.objects.filter(title__icontains=title).first()
    if not task:
        return f"No task found matching '{title}'."

    delete_task(task.id)
    return f"Deleted task: {title}"


# --- Lighting handlers ---

def handle_control_lights(zone: str, on: bool = None, brightness: int = None, **kwargs) -> str:
    """Handle controlling lights (power and brightness)."""
    results = []
    try:
        if on is not None:
            results.append(set_zone_power(zone, on))
        if brightness is not None:
            results.append(set_zone_brightness(zone, brightness))
        if not results:
            # Default: turn on
            results.append(set_zone_power(zone, True))
        return ". ".join(results)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error controlling lights: {e}"


def handle_set_light_color(zone: str, color: str, **kwargs) -> str:
    """Handle setting light color."""
    try:
        rgb = parse_color(color)
        return set_zone_color(zone, rgb)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error setting color: {e}"


def handle_set_light_effect(zone: str, effect: str, **kwargs) -> str:
    """Handle setting a lighting effect."""
    try:
        return set_zone_effect(zone, effect)
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error setting effect: {e}"


def handle_get_light_status(**kwargs) -> str:
    """Handle getting light status."""
    try:
        return get_light_status()
    except Exception as e:
        return f"Error getting light status: {e}"


# --- Music handlers ---

def handle_control_music(action: str, **kwargs) -> str:
    """Handle music playback control."""
    try:
        actions = {
            'pause': music_pause,
            'play': music_play,
            'resume': music_play,
            'stop': music_stop,
            'skip': music_skip,
            'next': music_skip,
            'previous': music_previous,
            'back': music_previous,
        }
        func = actions.get(action.lower())
        if func:
            return func()
        return f"Unknown action: {action}"
    except ConnectionError:
        return "Can't reach the speaker right now, bud"
    except Exception as e:
        return f"Error controlling music: {e}"


def handle_set_music_volume(level: int = None, adjust: str = None, **kwargs) -> str:
    """Handle setting music volume."""
    try:
        if adjust == 'up':
            return music_volume_up()
        elif adjust == 'down':
            return music_volume_down()
        elif level is not None:
            return music_volume(level)
        return "Specify a volume level (0-100) or direction (up/down)"
    except ConnectionError:
        return "Can't reach the speaker right now, bud"
    except Exception as e:
        return f"Error setting volume: {e}"


def handle_get_music_status(**kwargs) -> str:
    """Handle getting music status."""
    try:
        return music_status()
    except ConnectionError:
        return "Can't reach the speaker right now, bud"
    except Exception as e:
        return f"Error getting status: {e}"


COMMAND_HANDLERS = {
    'add_inventory_items': handle_add_inventory_items,
    'find_inventory': handle_find_inventory,
    'clear_inventory': handle_clear_inventory,
    'delete_inventory_item': handle_delete_inventory_item,
    'create_project': handle_create_project,
    'list_projects': handle_list_projects,
    'update_project': handle_update_project,
    'delete_project': handle_delete_project,
    'create_task': handle_create_task,
    'get_pending_tasks': handle_get_pending_tasks,
    'list_tasks': handle_list_tasks,
    'complete_task': handle_complete_task,
    'update_task': handle_update_task,
    'delete_task': handle_delete_task,
    'control_lights': handle_control_lights,
    'set_light_color': handle_set_light_color,
    'set_light_effect': handle_set_light_effect,
    'get_light_status': handle_get_light_status,
    'control_music': handle_control_music,
    'set_music_volume': handle_set_music_volume,
    'get_music_status': handle_get_music_status,
}
