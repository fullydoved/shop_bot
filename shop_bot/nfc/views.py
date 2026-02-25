import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from inventory.models import Bin, InventoryItem
from inventory.services import get_or_create_bin, get_items_in_bin, add_item, log_inventory_change
from .services import (
    register_tag, unlink_tag, lookup_tag, log_scan,
    list_tags, get_tag_for_bin, build_bin_url,
)


def bin_detail(request, bin_code):
    """NFC scan landing page — shows bin contents with quick actions."""
    bin_code = bin_code.upper()
    bin_obj = get_or_create_bin(bin_code)
    items = get_items_in_bin(bin_code).order_by('name')
    tag = get_tag_for_bin(bin_code)

    return render(request, 'nfc/bin_detail.html', {
        'bin': bin_obj,
        'items': items,
        'tag': tag,
    })


@require_POST
def quick_add(request, bin_code):
    """HTMX endpoint: add an item to a bin."""
    bin_code = bin_code.upper()
    name = request.POST.get('name', '').strip()
    quantity = request.POST.get('quantity', '').strip()
    category = request.POST.get('category', '').strip()

    if not name:
        return HttpResponse(
            '<p class="text-red-500 text-sm">Item name is required.</p>',
            status=400,
        )

    qty = int(quantity) if quantity.isdigit() else None
    add_item(name=name, bin_code=bin_code, quantity=qty, category=category)

    items = get_items_in_bin(bin_code).order_by('name')
    return render(request, 'nfc/partials/item_list.html', {'items': items, 'bin': get_or_create_bin(bin_code)})


@require_POST
def quick_use(request, bin_code):
    """HTMX endpoint: decrement an item's quantity by 1."""
    bin_code = bin_code.upper()
    item_id = request.POST.get('item_id')
    item = get_object_or_404(InventoryItem, id=item_id, bin__code=bin_code)

    if item.quantity is not None and item.quantity > 0:
        old_qty = item.quantity
        item.quantity -= 1
        item.save()
        log_inventory_change(
            'update', item.name, bin_code,
            quantity_before=old_qty, quantity_after=item.quantity,
        )

    items = get_items_in_bin(bin_code).order_by('name')
    return render(request, 'nfc/partials/item_list.html', {'items': items, 'bin': get_or_create_bin(bin_code)})


@csrf_exempt
@require_POST
def api_tag_scanned(request):
    """JSON API for the reader service: report a tag scan."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    uid = data.get('uid', '').strip()
    source = data.get('source', 'reader')

    if not uid:
        return JsonResponse({'error': 'uid is required'}, status=400)

    tag = lookup_tag(uid)
    if not tag:
        return JsonResponse({'error': 'Tag not registered', 'uid': uid}, status=404)

    log_scan(uid, tag.bin.code, source=source)

    items = list(
        get_items_in_bin(tag.bin.code).values('id', 'name', 'quantity', 'unit', 'category')
    )

    return JsonResponse({
        'bin_code': tag.bin.code,
        'url': build_bin_url(tag.bin.code),
        'items': items,
    })


@csrf_exempt
@require_POST
def api_register_tag(request):
    """JSON API for the reader service: register a tag to a bin."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    uid = data.get('uid', '').strip()
    bin_code = data.get('bin_code', '').strip()

    if not uid or not bin_code:
        return JsonResponse({'error': 'uid and bin_code are required'}, status=400)

    tag = register_tag(uid, bin_code)

    return JsonResponse({
        'uid': tag.uid,
        'bin_code': tag.bin.code,
        'written_url': tag.written_url,
        'status': tag.status,
    })


def tag_manage(request):
    """Admin page to list, register, and unlink NFC tags."""
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'register':
            uid = request.POST.get('uid', '').strip()
            bin_code = request.POST.get('bin_code', '').strip()
            if uid and bin_code:
                register_tag(uid, bin_code)

        elif action == 'unlink':
            uid = request.POST.get('uid', '').strip()
            if uid:
                unlink_tag(uid)

    tags = list_tags()
    bins = Bin.objects.order_by('code')

    return render(request, 'nfc/tag_manage.html', {
        'tags': tags,
        'bins': bins,
    })
