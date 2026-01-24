from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from inventory.models import Bin, InventoryItem
from projects.models import Project, Task
from assistant.processor import InputProcessor
from assistant.tts import synthesize
from assistant.stt import transcribe

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
        'wled_host': settings.WLED_HOST,
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


def tts(request):
    """Generate TTS audio for given text."""
    text = request.GET.get('text', '')
    if not text or len(text) > 1000:  # Limit text length
        return HttpResponse(status=400)

    try:
        audio_data = synthesize(text)
        return HttpResponse(audio_data, content_type='audio/wav')
    except Exception:
        return HttpResponse(status=500)


def stt(request):
    """Transcribe audio to text using Whisper."""
    import json

    if request.method != 'POST':
        return HttpResponse(status=405)

    audio_file = request.FILES.get('audio')
    if not audio_file:
        return HttpResponse(
            json.dumps({'error': 'No audio file provided'}),
            content_type='application/json',
            status=400
        )

    # Check file size (10MB max)
    if audio_file.size > 10 * 1024 * 1024:
        return HttpResponse(
            json.dumps({'error': 'File too large (max 10MB)'}),
            content_type='application/json',
            status=400
        )

    # Detect format from content type
    content_type = audio_file.content_type or ''
    if 'webm' in content_type:
        format_hint = 'webm'
    elif 'wav' in content_type:
        format_hint = 'wav'
    elif 'ogg' in content_type:
        format_hint = 'ogg'
    else:
        format_hint = 'webm'  # Default to webm

    try:
        audio_bytes = audio_file.read()
        text = transcribe(audio_bytes, format_hint)
        return HttpResponse(
            json.dumps({'text': text}),
            content_type='application/json'
        )
    except Exception as e:
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500
        )
