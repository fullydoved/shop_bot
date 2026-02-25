from django.contrib import admin
from .models import NfcTag, NfcScanLog


@admin.register(NfcTag)
class NfcTagAdmin(admin.ModelAdmin):
    list_display = ('uid', 'bin', 'status', 'last_scanned_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('uid', 'bin__code')
    ordering = ('bin__code',)


@admin.register(NfcScanLog)
class NfcScanLogAdmin(admin.ModelAdmin):
    list_display = ('uid', 'bin_code', 'source', 'timestamp')
    list_filter = ('source',)
    search_fields = ('uid', 'bin_code')
    ordering = ('-timestamp',)
