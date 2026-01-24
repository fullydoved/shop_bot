from django.db import models
from django.utils import timezone


class Tool(models.Model):
    """A tool that can be checked out."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='', help_text='Where this tool normally lives')
    category = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_available(self) -> bool:
        """Check if tool is currently available (not checked out)."""
        return not self.checkouts.filter(returned_at__isnull=True).exists()

    @property
    def current_checkout(self):
        """Get the current active checkout, if any."""
        return self.checkouts.filter(returned_at__isnull=True).first()

    @property
    def borrower(self) -> str | None:
        """Get the current borrower name, if checked out."""
        checkout = self.current_checkout
        return checkout.borrower if checkout else None


class Checkout(models.Model):
    """A checkout record for a tool."""

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='checkouts')
    borrower = models.CharField(max_length=255)
    checked_out_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-checked_out_at']

    def __str__(self):
        status = "returned" if self.returned_at else "active"
        return f"{self.tool.name} -> {self.borrower} ({status})"

    @property
    def is_active(self) -> bool:
        """Check if this checkout is still active."""
        return self.returned_at is None

    @property
    def duration(self) -> str:
        """Human-readable checkout duration."""
        end_time = self.returned_at or timezone.now()
        delta = end_time - self.checked_out_at
        total_seconds = int(delta.total_seconds())

        if total_seconds < 3600:
            mins = total_seconds // 60
            return f"{mins}m"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours}h"
        else:
            days = total_seconds // 86400
            return f"{days}d"
