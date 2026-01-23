from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.template.loader import render_to_string
from .models import Project, Task


def project_list(request):
    """List all projects."""
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/list.html', {'projects': projects})


def project_detail(request, project_id):
    """Show project details with its tasks."""
    project = get_object_or_404(Project, id=project_id)
    pending_tasks = project.tasks.exclude(status='done').order_by('-priority', 'created_at')
    completed_tasks = project.tasks.filter(status='done').order_by('-updated_at')

    return render(request, 'projects/detail.html', {
        'project': project,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'projects': Project.objects.all().order_by('name'),
    })


def task_list(request):
    """List all tasks with filtering."""
    project_filter = request.GET.get('project', '')
    status_filter = request.GET.get('status', '')

    tasks = Task.objects.all().select_related('project')

    if project_filter == 'none':
        tasks = tasks.filter(project__isnull=True)
    elif project_filter:
        tasks = tasks.filter(project_id=project_filter)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Group tasks by project
    tasks = tasks.order_by('project__name', 'status', '-priority')

    projects = Project.objects.all().order_by('name')

    return render(request, 'projects/tasks.html', {
        'tasks': tasks,
        'projects': projects,
        'project_filter': project_filter,
        'status_filter': status_filter,
    })


# --- Project CRUD ---

@require_POST
def create_project(request):
    name = request.POST.get('name', '').strip()
    if not name:
        return HttpResponse('<span class="text-red-600 text-sm">Name required</span>', status=400)

    project = Project.objects.create(
        name=name,
        status=request.POST.get('status', 'idea'),
        description=request.POST.get('description', '').strip(),
    )

    html = render_to_string('projects/project_row.html', {'project': project}, request=request)
    return HttpResponse(html)


@require_POST
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    project.name = request.POST.get('name', project.name).strip()
    project.status = request.POST.get('status', project.status)
    project.description = request.POST.get('description', project.description).strip()
    project.save()

    return HttpResponse('<span class="text-green-600 text-sm">Saved!</span>')


@require_http_methods(["DELETE"])
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return HttpResponse('')


# --- Task CRUD ---

@require_POST
def create_task(request):
    title = request.POST.get('title', '').strip()
    if not title:
        return HttpResponse('<span class="text-red-600 text-sm">Title required</span>', status=400)

    project_id = request.POST.get('project_id')
    project = Project.objects.filter(id=project_id).first() if project_id else None

    task = Task.objects.create(
        title=title,
        project=project,
        priority=request.POST.get('priority', 'medium'),
        status=request.POST.get('status', 'pending'),
        notes=request.POST.get('notes', '').strip(),
    )

    projects = Project.objects.all().order_by('name')
    html = render_to_string('projects/task_row.html', {'task': task, 'projects': projects}, request=request)
    return HttpResponse(html)


@require_POST
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    task.title = request.POST.get('title', task.title).strip()
    task.priority = request.POST.get('priority', task.priority)
    task.status = request.POST.get('status', task.status)
    task.notes = request.POST.get('notes', task.notes).strip()

    project_id = request.POST.get('project_id')
    task.project = Project.objects.filter(id=project_id).first() if project_id else None

    task.save()

    return HttpResponse('<span class="text-green-600 text-sm">Saved!</span>')


@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return HttpResponse('')
