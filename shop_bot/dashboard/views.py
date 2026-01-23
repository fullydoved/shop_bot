from django.shortcuts import render
from django.http import HttpResponse
from inventory.models import Bin, InventoryItem
from projects.models import Project, Task
from assistant.processor import InputProcessor

# Max messages to keep in session (matches processor history limit)
MAX_CHAT_MESSAGES = 10

# Shared processor instance for web chat
_processor = None


def get_processor():
    global _processor
    if _processor is None:
        _processor = InputProcessor()
    return _processor


def home(request):
    # Get chat history from session
    chat_messages = request.session.get('chat_messages', [])

    context = {
        'item_count': InventoryItem.objects.count(),
        'bin_count': Bin.objects.count(),
        'active_projects': Project.objects.filter(status='active').count(),
        'pending_tasks': Task.objects.filter(status='pending').count(),
        'tasks': Task.objects.filter(status='pending').order_by('-priority')[:5],
        'chat_messages': chat_messages,
    }
    return render(request, 'dashboard/home.html', context)


def chat(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            processor = get_processor()
            response = processor.process(message)

            # Store in session
            chat_messages = request.session.get('chat_messages', [])
            chat_messages.append({'role': 'user', 'content': message})
            chat_messages.append({'role': 'assistant', 'content': response})

            # Keep only last N messages
            if len(chat_messages) > MAX_CHAT_MESSAGES * 2:
                chat_messages = chat_messages[-(MAX_CHAT_MESSAGES * 2):]

            request.session['chat_messages'] = chat_messages

            return render(request, 'dashboard/chat_message.html', {
                'bot_response': response,
            })
    return HttpResponse('')


def clear_chat(request):
    """Clear chat history from session and processor."""
    if request.method == 'POST':
        request.session['chat_messages'] = []
        processor = get_processor()
        processor.clear_history()
    return HttpResponse('')
