from django.db import models
from django.utils import timezone


class Reminder(models.Model):
    """A timed reminder."""

    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    trigger_at = models.DateTimeField(db_index=True)
    triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    dismissed = models.BooleanField(default=False)

    class Meta:
        ordering = ['trigger_at']

    def __str__(self):
        return f"{self.title} @ {self.trigger_at}"

    @property
    def is_due(self) -> bool:
        """Check if this reminder is due."""
        return not self.triggered and timezone.now() >= self.trigger_at

    @property
    def time_until(self) -> str:
        """Human-readable time until trigger."""
        if self.triggered:
            return "triggered"

        delta = self.trigger_at - timezone.now()
        total_seconds = int(delta.total_seconds())

        if total_seconds < 0:
            return "overdue"
        elif total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            mins = total_seconds // 60
            return f"{mins}m"
        else:
            hours = total_seconds // 3600
            mins = (total_seconds % 3600) // 60
            if mins:
                return f"{hours}h {mins}m"
            return f"{hours}h"
