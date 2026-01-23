from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import InventoryItem, Bin


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

    item.name = request.POST.get('name', item.name).strip()
    item.quantity = request.POST.get('quantity') or None
    item.unit = request.POST.get('unit', 'pcs').strip() or 'pcs'

    # Handle category with "new category" option
    category = request.POST.get('category', '').strip()
    new_category = request.POST.get('new_category', '').strip()
    item.category = new_category if new_category else category

    # Handle bin change
    bin_id = request.POST.get('bin_id')
    if bin_id:
        item.bin_id = bin_id

    item.save()

    return HttpResponse('<span class="text-green-600 text-sm">Saved!</span>')


@require_http_methods(["DELETE"])
def delete_item(request, item_id):
    """Delete an item."""
    item = get_object_or_404(InventoryItem, id=item_id)
    item.delete()
    return HttpResponse('')


@require_POST
def create_item(request):
    """Create a new item."""
    name = request.POST.get('name', '').strip()
    bin_id = request.POST.get('bin_id')

    if not name or not bin_id:
        return HttpResponse('<span class="text-red-600 text-sm">Name and bin required</span>', status=400)

    bin_obj = get_object_or_404(Bin, id=bin_id)

    item = InventoryItem.objects.create(
        name=name,
        bin=bin_obj,
        quantity=request.POST.get('quantity') or None,
        unit=request.POST.get('unit', 'pcs').strip() or 'pcs',
        category=request.POST.get('category', '').strip(),
    )

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
