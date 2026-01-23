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
    notes: str = '',
    position: str = ''
) -> InventoryItem:
    """Add or update an inventory item in the specified bin.

    If an item with the same name exists in the bin, updates the quantity.
    Otherwise creates a new item.
    """
    bin_obj = get_or_create_bin(bin_code)

    # Check if item already exists in this bin
    existing = InventoryItem.objects.filter(
        name__iexact=name,
        bin=bin_obj
    ).first()

    if existing:
        # Update existing item
        if quantity is not None:
            existing.quantity = quantity
        if category:
            existing.category = category
        if unit:
            existing.unit = unit
        if notes:
            existing.notes = notes
        if position:
            existing.position = position
        existing.save()
        return existing

    # Create new item
    item = InventoryItem.objects.create(
        name=name,
        bin=bin_obj,
        category=category,
        quantity=quantity,
        unit=unit,
        notes=notes,
        position=position
    )
    return item


def set_bin_divider(bin_code: str, divider_type: str) -> Bin:
    """Set the divider type for a bin."""
    bin_obj = get_or_create_bin(bin_code)
    bin_obj.divider_type = divider_type
    bin_obj.save()
    return bin_obj


def find_items(query: str) -> QuerySet:
    """Search for items by name (case-insensitive contains)."""
    return InventoryItem.objects.filter(name__icontains=query)


def get_items_in_bin(bin_code: str) -> QuerySet:
    """Get all items in a specific bin."""
    return InventoryItem.objects.filter(bin__code=bin_code)


def clear_inventory() -> int:
    """Delete all inventory items. Returns count of deleted items."""
    count = InventoryItem.objects.count()
    InventoryItem.objects.all().delete()
    return count


def delete_item(item_id: int = None, name: str = None) -> bool:
    """Delete an inventory item by ID or name."""
    if item_id:
        item = InventoryItem.objects.filter(id=item_id).first()
    elif name:
        item = InventoryItem.objects.filter(name__icontains=name).first()
    else:
        return False

    if item:
        item.delete()
        return True
    return False
