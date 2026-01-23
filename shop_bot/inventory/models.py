from django.db import models


class Bin(models.Model):
    """Storage bin location in the shop."""
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class InventoryItem(models.Model):
    """An item stored in inventory."""
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    bin = models.ForeignKey(Bin, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
