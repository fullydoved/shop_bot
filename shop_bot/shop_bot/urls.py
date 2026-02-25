from django.contrib import admin
from django.urls import path, include
from inventory.views import inventory_list, update_item, delete_item, create_item
from projects.views import (
    project_list, project_detail, task_list,
    create_project, update_project, delete_project,
    create_task, update_task, delete_task,
)
from reminders.views import poll_reminders

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    # Inventory
    path('inventory/', inventory_list, name='inventory'),
    path('inventory/create/', create_item, name='create_item'),
    path('inventory/<int:item_id>/', update_item, name='update_item'),
    path('inventory/<int:item_id>/delete/', delete_item, name='delete_item'),
    # Projects
    path('projects/', project_list, name='projects'),
    path('projects/create/', create_project, name='create_project'),
    path('projects/<int:project_id>/edit/', update_project, name='update_project'),
    path('projects/<int:project_id>/delete/', delete_project, name='delete_project'),
    path('projects/<int:project_id>/', project_detail, name='project_detail'),
    # Tasks
    path('tasks/', task_list, name='tasks'),
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/<int:task_id>/', update_task, name='update_task'),
    path('tasks/<int:task_id>/delete/', delete_task, name='delete_task'),
    # Reminders
    path('reminders/poll/', poll_reminders, name='poll_reminders'),
    # NFC
    path('nfc/', include('nfc.urls')),
]
