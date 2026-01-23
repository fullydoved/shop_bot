from django.db.models import QuerySet
from .models import Bin, InventoryItem


def get_or_create_bin(code: str) -> Bin:
    """Get an existing bin or create a new one with the given code."""
    bin_obj, _ = Bin.objects.get_or_create(code=code)
    return bin_obj


def add_item(
    name: str,
    bin_code: str,
    category: str = '',
    quantity: int = None,
    unit: str = '',
    notes: str = ''
) -> InventoryItem:
    """Add a new inventory item to the specified bin."""
    bin_obj = get_or_create_bin(bin_code)
    item = InventoryItem.objects.create(
        name=name,
        bin=bin_obj,
        category=category,
        quantity=quantity,
        unit=unit,
        notes=notes
    )
    return item


def find_items(query: str) -> QuerySet:
    """Search for items by name (case-insensitive contains)."""
    return InventoryItem.objects.filter(name__icontains=query)


def get_items_in_bin(bin_code: str) -> QuerySet:
    """Get all items in a specific bin."""
    return InventoryItem.objects.filter(bin__code=bin_code)
