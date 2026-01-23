from inventory.services import add_item, find_items, get_or_create_bin
from projects.services import (
    create_project, list_projects, update_project, delete_project,
    create_task, get_pending_tasks, get_all_tasks, update_task, complete_task, delete_task,
)
from projects.models import Project, Task


def handle_add_inventory_items(bin_code: str, items: list, **kwargs) -> str:
    """Handle adding inventory items to a bin."""
    get_or_create_bin(bin_code)
    added = []
    for item in items:
        if isinstance(item, dict):
            name = item.get('name', str(item))
            category = item.get('category', '')
            quantity = item.get('quantity')
        else:
            name = str(item)
            category = ''
            quantity = None

        inv_item = add_item(
            name=name,
            bin_code=bin_code,
            category=category,
            quantity=quantity,
        )
        added.append(inv_item.name)
    return f"Added {len(added)} item(s) to bin {bin_code}: {', '.join(added)}"


def handle_find_inventory(query: str, **kwargs) -> str:
    """Handle searching for inventory items."""
    items = find_items(query)
    if not items:
        return f"No items found matching '{query}'"

    results = []
    for item in items[:10]:
        loc = f"in bin {item.bin.code}"
        qty = f" ({item.quantity} {item.unit})" if item.quantity else ""
        results.append(f"- {item.name}{qty} {loc}")

    return f"Found {items.count()} item(s):\n" + "\n".join(results)


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


def handle_list_tasks(status: str = None, **kwargs) -> str:
    """Handle listing all tasks."""
    tasks = get_all_tasks(status)
    if not tasks:
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


COMMAND_HANDLERS = {
    'add_inventory_items': handle_add_inventory_items,
    'find_inventory': handle_find_inventory,
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
}
