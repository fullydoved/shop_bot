"""Reminder management services."""

import re
from datetime import timedelta
from django.utils import timezone
from .models import Reminder


def parse_time_string(time_str: str) -> timedelta:
    """Parse a human-readable time string into a timedelta.

    Supports formats like:
    - "30 seconds", "30s", "30 sec"
    - "5 minutes", "5m", "5 min"
    - "2 hours", "2h", "2 hr"
    - "1 hour 30 minutes", "1h30m", "1h 30m"

    Args:
        time_str: Human-readable time string

    Returns:
        timedelta representing the duration

    Raises:
        ValueError: If the string cannot be parsed
    """
    time_str = time_str.lower().strip()

    # Pattern to match number + unit pairs
    pattern = r'(\d+)\s*(s(?:ec(?:ond)?s?)?|m(?:in(?:ute)?s?)?|h(?:(?:ou)?rs?)?)'
    matches = re.findall(pattern, time_str)

    if not matches:
        raise ValueError(f"Could not parse time: {time_str}")

    total = timedelta()
    for value, unit in matches:
        value = int(value)
        if unit.startswith('s'):
            total += timedelta(seconds=value)
        elif unit.startswith('m'):
            total += timedelta(minutes=value)
        elif unit.startswith('h'):
            total += timedelta(hours=value)

    if total.total_seconds() == 0:
        raise ValueError(f"Could not parse time: {time_str}")

    return total


def create_reminder(title: str, time_str: str, notes: str = '') -> Reminder:
    """Create a new reminder.

    Args:
        title: What to remind about
        time_str: When to trigger (e.g., "20 minutes", "1h30m")
        notes: Optional additional notes

    Returns:
        Created Reminder instance
    """
    delta = parse_time_string(time_str)
    trigger_at = timezone.now() + delta

    return Reminder.objects.create(
        title=title,
        notes=notes,
        trigger_at=trigger_at,
    )


def get_pending_reminders() -> list[Reminder]:
    """Get all pending (not triggered, not dismissed) reminders."""
    return list(
        Reminder.objects.filter(triggered=False, dismissed=False)
        .order_by('trigger_at')
    )


def get_triggered_reminders() -> list[Reminder]:
    """Get triggered but not dismissed reminders."""
    return list(
        Reminder.objects.filter(triggered=True, dismissed=False)
        .order_by('-triggered_at')
    )


def dismiss_reminder(reminder_id: int = None, title: str = None) -> bool:
    """Dismiss a reminder by ID or title.

    Args:
        reminder_id: Reminder ID to dismiss
        title: Reminder title (partial match)

    Returns:
        True if dismissed, False if not found
    """
    if reminder_id:
        reminder = Reminder.objects.filter(id=reminder_id).first()
    elif title:
        reminder = Reminder.objects.filter(
            title__icontains=title,
            dismissed=False
        ).first()
    else:
        return False

    if reminder:
        reminder.dismissed = True
        reminder.save()
        return True
    return False


def cancel_reminder(reminder_id: int = None, title: str = None) -> bool:
    """Cancel (delete) a pending reminder.

    Args:
        reminder_id: Reminder ID to cancel
        title: Reminder title (partial match)

    Returns:
        True if cancelled, False if not found
    """
    if reminder_id:
        reminder = Reminder.objects.filter(id=reminder_id, triggered=False).first()
    elif title:
        reminder = Reminder.objects.filter(
            title__icontains=title,
            triggered=False
        ).first()
    else:
        return False

    if reminder:
        reminder.delete()
        return True
    return False


def check_and_trigger_reminders() -> list[Reminder]:
    """Check for due reminders and mark them as triggered.

    Returns:
        List of newly triggered reminders
    """
    now = timezone.now()
    due_reminders = Reminder.objects.filter(
        triggered=False,
        dismissed=False,
        trigger_at__lte=now
    )

    triggered = []
    for reminder in due_reminders:
        reminder.triggered = True
        reminder.triggered_at = now
        reminder.save()
        triggered.append(reminder)

    return triggered


def cleanup_old_reminders(days: int = 7) -> int:
    """Delete old dismissed reminders.

    Args:
        days: Delete reminders older than this many days

    Returns:
        Number of reminders deleted
    """
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = Reminder.objects.filter(
        dismissed=True,
        triggered_at__lt=cutoff
    ).delete()
    return deleted
