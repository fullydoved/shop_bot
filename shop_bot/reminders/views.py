import random
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Reminder

# Varied reminder announcement phrases
REMINDER_PHRASES = [
    "Hey, just a reminder: {}",
    "It's time for me to remind you about {}",
    "Heads up! {}",
    "Don't forget: {}",
    "Quick reminder: {}",
    "Hey! You wanted me to remind you about {}",
    "Reminder time! {}",
    "Just so you know, {}",
    "Time to {}",
    "Yo! {}",
]


@require_GET
def poll_reminders(request):
    """Poll for triggered reminders that need to be announced.

    Returns JSON with list of reminders to announce, marks them as announced.
    """
    # Find triggered but not announced reminders
    reminders = Reminder.objects.filter(
        triggered=True,
        announced=False,
        dismissed=False
    )

    announcements = []
    for reminder in reminders:
        phrase = random.choice(REMINDER_PHRASES)
        message = phrase.format(reminder.title)
        announcements.append({
            'id': reminder.id,
            'title': reminder.title,
            'message': message,
        })
        # Mark as announced
        reminder.announced = True
        reminder.save()

    return JsonResponse({'reminders': announcements})
