from django.urls import path
from . import views

app_name = 'nfc'

urlpatterns = [
    # Scan landing pages
    path('bin/<str:bin_code>/', views.bin_detail, name='bin_detail'),
    path('bin/<str:bin_code>/add/', views.quick_add, name='quick_add'),
    path('bin/<str:bin_code>/use/', views.quick_use, name='quick_use'),

    # JSON API for reader service
    path('api/scanned/', views.api_tag_scanned, name='api_tag_scanned'),
    path('api/register/', views.api_register_tag, name='api_register_tag'),

    # Tag management
    path('tags/', views.tag_manage, name='tag_manage'),
]
