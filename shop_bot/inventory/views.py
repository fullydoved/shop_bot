from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import InventoryItem, Bin
from .services import log_inventory_change


def inventory_list(request):
    query = request.GET.get('q', '')
    items = InventoryItem.objects.select_related('bin').order_by('bin__code', 'name')

    if query:
        items = items.filter(name__icontains=query)

    # Get distinct categories for the dropdown
    categories = (
        InventoryItem.objects
        .exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )

    # Get all bins for the dropdown
    bins = Bin.objects.order_by('code')

    return render(request, 'inventory/list.html', {
        'items': items,
        'query': query,
        'categories': list(categories),
        'bins': bins,
    })


@require_POST
def update_item(request, item_id):
    """Update an item's fields."""
    item = get_object_or_404(InventoryItem, id=item_id)

    # Capture old values for logging
    old_bin_code = item.bin.code
    old_quantity = item.quantity

    item.name = request.POST.get('name', item.name).strip()
    item.quantity = request.POST.get('quantity') or None
    item.unit = request.POST.get('unit', 'pcs').strip() or 'pcs'

    # Handle category with "new category" option
    category = request.POST.get('category', '').strip()
    new_category = request.POST.get('new_category', '').strip()
    item.category = new_category if new_category else category

    # Handle bin change (existing or new)
    new_bin = request.POST.get('new_bin', '').strip()
    if new_bin:
        bin_obj, _ = Bin.objects.get_or_create(code=new_bin.upper())
        item.bin = bin_obj
    else:
        bin_id = request.POST.get('bin_id')
        if bin_id:
            item.bin_id = bin_id

    # Handle position
    item.position = request.POST.get('position', '').strip()

    item.save()

    # Log the change (move or update)
    new_bin_code = item.bin.code
    if old_bin_code != new_bin_code:
        log_inventory_change(
            'move', item.name, new_bin_code,
            quantity_before=old_quantity, quantity_after=item.quantity,
            details={'from_bin': old_bin_code, 'to_bin': new_bin_code}
        )
    else:
        log_inventory_change(
            'update', item.name, new_bin_code,
            quantity_before=old_quantity, quantity_after=item.quantity
        )

    return HttpResponse('<span class="text-green-600 text-sm">Saved!</span>')


@require_http_methods(["DELETE"])
def delete_item(request, item_id):
    """Delete an item."""
    item = get_object_or_404(InventoryItem, id=item_id)
    log_inventory_change(
        'delete', item.name, item.bin.code,
        quantity_before=item.quantity
    )
    item.delete()
    return HttpResponse('')


@require_POST
def create_item(request):
    """Create a new item."""
    name = request.POST.get('name', '').strip()
    bin_id = request.POST.get('bin_id')
    new_bin = request.POST.get('new_bin', '').strip()

    if not name or (not bin_id and not new_bin):
        return HttpResponse('<span class="text-red-600 text-sm">Name and bin required</span>', status=400)

    # Handle new bin or existing bin
    if new_bin:
        bin_obj, _ = Bin.objects.get_or_create(code=new_bin.upper())
    else:
        bin_obj = get_object_or_404(Bin, id=bin_id)

    item = InventoryItem.objects.create(
        name=name,
        bin=bin_obj,
        quantity=request.POST.get('quantity') or None,
        unit=request.POST.get('unit', 'pcs').strip() or 'pcs',
        category=request.POST.get('category', '').strip(),
        position=request.POST.get('position', '').strip(),
    )

    log_inventory_change('add', item.name, bin_obj.code, quantity_after=item.quantity)

    # Return the new row HTML
    categories = list(
        InventoryItem.objects
        .exclude(category='')
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )
    bins = Bin.objects.order_by('code')

    from django.template.loader import render_to_string
    html = render_to_string('inventory/item_row.html', {
        'item': item,
        'categories': categories,
        'bins': bins,
    }, request=request)

    return HttpResponse(html)
