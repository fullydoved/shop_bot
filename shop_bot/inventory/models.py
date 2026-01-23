from django.db import models


class Bin(models.Model):
    """Storage bin location in the shop."""
    DIVIDER_CHOICES = [
        ('none', 'No dividers'),
        ('vertical', 'Vertical (left/right)'),
        ('horizontal', 'Horizontal (front/back)'),
    ]

    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    divider_type = models.CharField(max_length=20, choices=DIVIDER_CHOICES, default='none')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class InventoryItem(models.Model):
    """An item stored in inventory."""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE, related_name='items')
    position = models.CharField(max_length=20, blank=True, help_text='Position in bin: left, right, front, back, etc.')
    quantity = models.PositiveIntegerField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
