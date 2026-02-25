from django.conf import settings
from django.utils import timezone

from inventory.services import get_or_create_bin, get_items_in_bin
from .models import NfcTag, NfcScanLog


def get_nfc_host() -> str:
    """Return the NFC_HOST setting (host:port for NDEF URLs)."""
    return getattr(settings, 'NFC_HOST', '192.168.1.85:42070')


def build_bin_url(bin_code: str) -> str:
    """Build the NDEF URL for a bin tag."""
    host = get_nfc_host()
    return f'http://{host}/nfc/bin/{bin_code}/'


def register_tag(uid: str, bin_code: str) -> NfcTag:
    """Register a new NFC tag or re-link an existing one to a bin."""
    bin_obj = get_or_create_bin(bin_code.upper())
    url = build_bin_url(bin_obj.code)

    tag, created = NfcTag.objects.update_or_create(
        uid=uid.upper(),
        defaults={
            'bin': bin_obj,
            'status': 'active',
            'written_url': url,
        },
    )
    return tag


def unlink_tag(uid: str) -> bool:
    """Mark a tag as inactive (unlink from bin without deleting)."""
    tag = NfcTag.objects.filter(uid=uid.upper()).first()
    if not tag:
        return False
    tag.status = 'inactive'
    tag.save()
    return True


def lookup_tag(uid: str) -> NfcTag | None:
    """Find an active tag by UID."""
    return NfcTag.objects.filter(uid=uid.upper(), status='active').first()


def log_scan(uid: str, bin_code: str, source: str = 'unknown') -> NfcScanLog:
    """Record a tag scan in the audit log and update last_scanned_at."""
    tag = NfcTag.objects.filter(uid=uid.upper()).first()
    if tag:
        tag.last_scanned_at = timezone.now()
        tag.save(update_fields=['last_scanned_at'])

    return NfcScanLog.objects.create(
        tag=tag,
        uid=uid.upper(),
        bin_code=bin_code,
        source=source,
    )


def list_tags() -> list:
    """Return all tags ordered by bin code."""
    return list(NfcTag.objects.select_related('bin').all())


def get_tag_for_bin(bin_code: str) -> NfcTag | None:
    """Get the active tag linked to a bin."""
    return NfcTag.objects.filter(
        bin__code=bin_code.upper(),
        status='active',
    ).first()
