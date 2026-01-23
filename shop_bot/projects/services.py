from django.db.models import QuerySet
from .models import Project, Task


def create_project(name: str, description: str = '', status: str = 'idea') -> Project:
    """Create a new project."""
    return Project.objects.create(name=name, description=description, status=status)


def list_projects(status: str = None) -> QuerySet:
    """List all projects, optionally filtered by status."""
    qs = Project.objects.all().order_by('-created_at')
    if status:
        qs = qs.filter(status=status)
    return qs


def update_project(project_id: int, **kwargs) -> Project:
    """Update a project's fields."""
    project = Project.objects.get(pk=project_id)
    for key, value in kwargs.items():
        if hasattr(project, key) and value is not None:
            setattr(project, key, value)
    project.save()
    return project


def delete_project(project_id: int) -> bool:
    """Delete a project."""
    project = Project.objects.get(pk=project_id)
    project.delete()
    return True


def create_task(
    title: str,
    project_id: int = None,
    project_name: str = None,
    priority: str = 'medium',
    due_date=None
) -> Task:
    """Create a new task, optionally associated with a project."""
    project = None
    if project_id is not None:
        project = Project.objects.get(pk=project_id)
    elif project_name:
        project = Project.objects.filter(name__iexact=project_name).first()

    return Task.objects.create(
        title=title,
        project=project,
        priority=priority,
        due_date=due_date
    )


def get_pending_tasks() -> QuerySet:
    """Get all tasks with pending status."""
    return Task.objects.filter(status='pending')


def get_all_tasks(status: str = None) -> QuerySet:
    """Get all tasks, optionally filtered by status."""
    qs = Task.objects.all().order_by('status', '-priority')
    if status:
        qs = qs.filter(status=status)
    return qs


def update_task(task_id: int, **kwargs) -> Task:
    """Update a task's fields."""
    task = Task.objects.get(pk=task_id)
    for key, value in kwargs.items():
        if key == 'project_name' and value:
            task.project = Project.objects.filter(name__iexact=value).first()
        elif hasattr(task, key) and value is not None:
            setattr(task, key, value)
    task.save()
    return task


def complete_task(task_id: int) -> Task:
    """Mark a task as done."""
    task = Task.objects.get(pk=task_id)
    task.status = 'done'
    task.save()
    return task


def delete_task(task_id: int) -> bool:
    """Delete a task."""
    task = Task.objects.get(pk=task_id)
    task.delete()
    return True


def get_project_tasks(project_id: int) -> QuerySet:
    """Get all tasks for a specific project."""
    return Task.objects.filter(project_id=project_id)
