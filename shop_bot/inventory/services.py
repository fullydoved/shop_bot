from django.db.models import Q, QuerySet
from .models import Bin, InventoryItem, InventoryLog
from .aliases import expand_query
from .normalize import normalize_fastener_name


def log_inventory_change(
    action: str,
    item_name: str,
    bin_code: str,
    quantity_before: int = None,
    quantity_after: int = None,
    details: dict = None
) -> InventoryLog:
    """Create an audit log entry for an inventory change."""
    return InventoryLog.objects.create(
        action=action,
        item_name=item_name,
        bin_code=bin_code,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        details=details or {}
    )


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

    Fastener names are automatically normalized to standard format:
    - "socket head cap screw M3x6mm" -> "SHCS M3x6mm"
    - "M5 hex nut" -> "HEX NUT M5"
    - "washer M4" -> "WASHER M4"
    """
    # Normalize fastener names to standard format
    name = normalize_fastener_name(name)

    bin_obj = get_or_create_bin(bin_code)

    # Check if item already exists in this bin
    existing = InventoryItem.objects.filter(
        name__iexact=name,
        bin=bin_obj
    ).first()

    if existing:
        # Update existing item
        old_qty = existing.quantity
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
        log_inventory_change(
            'update', existing.name, bin_code,
            quantity_before=old_qty, quantity_after=existing.quantity
        )
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
    log_inventory_change('add', item.name, bin_code, quantity_after=item.quantity)
    return item


def set_bin_divider(bin_code: str, divider_type: str) -> Bin:
    """Set the divider type for a bin."""
    bin_obj = get_or_create_bin(bin_code)
    bin_obj.divider_type = divider_type
    bin_obj.save()
    return bin_obj


def find_items(query: str) -> QuerySet:
    """Search for items by name with query expansion."""
    terms = expand_query(query)

    # Build OR query for all expanded terms
    q_objects = Q()
    for term in terms:
        q_objects |= Q(name__icontains=term)

    return InventoryItem.objects.filter(q_objects).distinct()


def get_items_in_bin(bin_code: str) -> QuerySet:
    """Get all items in a specific bin."""
    return InventoryItem.objects.filter(bin__code=bin_code)


def clear_inventory() -> int:
    """Delete all inventory items. Returns count of deleted items."""
    count = InventoryItem.objects.count()
    if count > 0:
        log_inventory_change('clear', 'ALL', '-', details={'items_deleted': count})
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
        log_inventory_change(
            'delete', item.name, item.bin.code,
            quantity_before=item.quantity
        )
        item.delete()
        return True
    return False
