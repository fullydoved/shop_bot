from django.db import models


class NfcTag(models.Model):
    """An NFC tag physically attached to a storage bin."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('lost', 'Lost'),
    ]

    uid = models.CharField(max_length=32, unique=True, help_text='Tag UID (hex)')
    bin = models.ForeignKey(
        'inventory.Bin',
        on_delete=models.CASCADE,
        related_name='nfc_tags',
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    written_url = models.URLField(blank=True, help_text='NDEF URL written to this tag')
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['bin__code']

    def __str__(self):
        return f'{self.uid} -> {self.bin.code}'


class NfcScanLog(models.Model):
    """Audit trail for NFC tag scans."""
    tag = models.ForeignKey(
        NfcTag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scan_logs',
    )
    uid = models.CharField(max_length=32, help_text='Tag UID at time of scan')
    bin_code = models.CharField(max_length=10)
    source = models.CharField(
        max_length=20,
        default='unknown',
        help_text='How the scan happened: reader, android, web',
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.uid} scanned at {self.timestamp}'
