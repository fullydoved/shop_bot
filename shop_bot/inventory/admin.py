from django.contrib import admin
from .models import Bin, InventoryItem


@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'created_at', 'updated_at')
    search_fields = ('code', 'description')
    ordering = ('code',)


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'bin', 'quantity', 'unit', 'updated_at')
    search_fields = ('name', 'category', 'notes')
    list_filter = ('category', 'bin')
    ordering = ('name',)
