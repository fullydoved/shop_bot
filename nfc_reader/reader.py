#!/usr/bin/env python3
"""
NFC Reader Service for B.E.A.V.S.

Runs on the Mac Mini with an ACR1252U USB NFC reader.
Communicates with the BEAVS Django app over HTTP.

Usage:
    python reader.py              # Scan mode: poll for tags, open browser
    python reader.py --write A1   # Write mode: write NDEF URL for bin A1 to tag
"""

import argparse
import os
import struct
import subprocess
import sys
import time
import webbrowser

import ndef
import requests
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString, toBytes

# Configuration
BEAVS_HOST = os.environ.get('NFC_HOST', '192.168.1.85:42070')
BEAVS_BASE = f'http://{BEAVS_HOST}'
POLL_INTERVAL = 0.5  # seconds between card checks


def build_bin_url(bin_code: str) -> str:
    """Build the NDEF URL for a bin."""
    return f'{BEAVS_BASE}/nfc/bin/{bin_code.upper()}/'


def get_uid(connection) -> str | None:
    """Read the UID from the card via GET DATA command."""
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    try:
        data, sw1, sw2 = connection.transmit(GET_UID)
        if sw1 == 0x90 and sw2 == 0x00:
            return toHexString(data).replace(' ', '')
    except Exception:
        pass
    return None


def read_ndef_url(connection) -> str | None:
    """Read NDEF URL record from an NFC Forum Type 2 tag.

    Reads pages 4+ (user memory after the CC) and parses the NDEF message.
    """
    # Read pages 4-7 (16 bytes starting at page 4)
    READ_CMD = [0xFF, 0xB0, 0x00, 0x04, 0x10]
    try:
        data, sw1, sw2 = connection.transmit(READ_CMD)
        if sw1 != 0x90 or sw2 != 0x00:
            return None
    except Exception:
        return None

    # Parse NDEF TLV: find type 0x03 (NDEF Message)
    raw = bytes(data)
    i = 0
    while i < len(raw):
        tlv_type = raw[i]
        if tlv_type == 0x00:  # NULL TLV
            i += 1
            continue
        if tlv_type == 0xFE:  # Terminator
            break
        if i + 1 >= len(raw):
            break
        tlv_len = raw[i + 1]
        if tlv_type == 0x03:  # NDEF Message
            ndef_bytes = raw[i + 2:i + 2 + tlv_len]
            # We may need more data for longer messages
            if len(ndef_bytes) < tlv_len:
                # Read more pages
                extra_pages = (tlv_len - len(ndef_bytes) + 15) // 16
                for p in range(1, extra_pages + 1):
                    page = 4 + (p * 4)
                    cmd = [0xFF, 0xB0, 0x00, page, 0x10]
                    try:
                        more, sw1, sw2 = connection.transmit(cmd)
                        if sw1 == 0x90 and sw2 == 0x00:
                            raw += bytes(more)
                    except Exception:
                        break
                ndef_bytes = raw[i + 2:i + 2 + tlv_len]

            try:
                records = list(ndef.message_decoder(ndef_bytes))
                for record in records:
                    if isinstance(record, ndef.UriRecord):
                        return record.iri
            except Exception:
                pass
            return None
        i += 2 + tlv_len

    return None


def write_ndef_url(connection, url: str) -> bool:
    """Write an NDEF URL record to an NFC Forum Type 2 tag.

    Encodes the URL as an NDEF message, wraps in TLV, and writes to pages 4+.
    """
    # Build NDEF message
    record = ndef.UriRecord(url)
    ndef_bytes = b''.join(ndef.message_encoder([record]))

    # Wrap in TLV: 0x03 <len> <ndef_bytes> 0xFE
    tlv = bytes([0x03, len(ndef_bytes)]) + ndef_bytes + bytes([0xFE])

    # Pad to 4-byte page boundary
    while len(tlv) % 4 != 0:
        tlv += b'\x00'

    # Write 4 bytes at a time starting at page 4
    for page_offset in range(len(tlv) // 4):
        page = 4 + page_offset
        page_data = list(tlv[page_offset * 4:(page_offset + 1) * 4])
        # UPDATE BINARY command
        cmd = [0xFF, 0xD6, 0x00, page, 0x04] + page_data
        try:
            data, sw1, sw2 = connection.transmit(cmd)
            if sw1 != 0x90 or sw2 != 0x00:
                print(f'  Write failed at page {page}: SW={sw1:02X}{sw2:02X}')
                return False
        except Exception as e:
            print(f'  Write error at page {page}: {e}')
            return False

    return True


def notify_beavs_scan(uid: str) -> dict | None:
    """Notify BEAVS API that a tag was scanned."""
    try:
        resp = requests.post(
            f'{BEAVS_BASE}/nfc/api/scanned/',
            json={'uid': uid, 'source': 'reader'},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
        else:
            print(f'  API error: {resp.status_code} {resp.text}')
    except requests.RequestException as e:
        print(f'  Connection error: {e}')
    return None


def register_with_beavs(uid: str, bin_code: str) -> dict | None:
    """Register a tag with the BEAVS API."""
    try:
        resp = requests.post(
            f'{BEAVS_BASE}/nfc/api/register/',
            json={'uid': uid, 'bin_code': bin_code},
            timeout=5,
        )
        if resp.ok:
            return resp.json()
        else:
            print(f'  API error: {resp.status_code} {resp.text}')
    except requests.RequestException as e:
        print(f'  Connection error: {e}')
    return None


def scan_mode():
    """Poll for NFC tags and open the bin page in the browser."""
    from smartcard.System import readers

    print(f'NFC Reader - Scan Mode')
    print(f'BEAVS: {BEAVS_BASE}')
    print(f'Waiting for reader...')

    last_uid = None
    last_uid_time = 0
    DEBOUNCE = 3  # seconds before re-scanning same tag

    while True:
        try:
            reader_list = readers()
            if not reader_list:
                time.sleep(1)
                continue

            reader = reader_list[0]
            connection = reader.createConnection()

            try:
                connection.connect()
            except Exception:
                time.sleep(POLL_INTERVAL)
                continue

            uid = get_uid(connection)
            if not uid:
                last_uid = None
                time.sleep(POLL_INTERVAL)
                continue

            now = time.time()
            if uid == last_uid and (now - last_uid_time) < DEBOUNCE:
                time.sleep(POLL_INTERVAL)
                continue

            last_uid = uid
            last_uid_time = now

            print(f'\nTag detected: {uid}')

            # Try reading NDEF URL
            url = read_ndef_url(connection)
            if url:
                print(f'  NDEF URL: {url}')
                webbrowser.open(url)
            else:
                print(f'  No NDEF URL, checking API...')

            # Notify BEAVS
            result = notify_beavs_scan(uid)
            if result:
                print(f'  Bin: {result["bin_code"]}')
                if not url:
                    webbrowser.open(result['url'])
            elif not url:
                print(f'  Tag not registered. Use --write to register.')

        except KeyboardInterrupt:
            print('\nExiting.')
            break
        except Exception as e:
            print(f'Error: {e}')

        time.sleep(POLL_INTERVAL)


def write_mode(bin_code: str):
    """Write an NDEF URL to a tag and register it with BEAVS."""
    from smartcard.System import readers

    bin_code = bin_code.upper()
    url = build_bin_url(bin_code)

    print(f'NFC Reader - Write Mode')
    print(f'Bin: {bin_code}')
    print(f'URL: {url}')
    print(f'Place tag on reader...')

    while True:
        try:
            reader_list = readers()
            if not reader_list:
                time.sleep(0.5)
                continue

            reader = reader_list[0]
            connection = reader.createConnection()

            try:
                connection.connect()
            except Exception:
                time.sleep(0.5)
                continue

            uid = get_uid(connection)
            if not uid:
                time.sleep(0.5)
                continue

            print(f'\nTag detected: {uid}')
            print(f'  Writing NDEF URL: {url}')

            if write_ndef_url(connection, url):
                print(f'  Write OK')

                # Register with BEAVS
                result = register_with_beavs(uid, bin_code)
                if result:
                    print(f'  Registered: {result["uid"]} -> {result["bin_code"]}')
                else:
                    print(f'  Warning: write succeeded but API registration failed')

                print(f'\nDone! Remove tag.')
                break
            else:
                print(f'  Write FAILED. Try again.')
                break

        except KeyboardInterrupt:
            print('\nCancelled.')
            break
        except Exception as e:
            print(f'Error: {e}')
            break


def main():
    parser = argparse.ArgumentParser(description='B.E.A.V.S. NFC Reader Service')
    parser.add_argument(
        '--write',
        metavar='BIN_CODE',
        help='Write mode: write NDEF URL for the given bin code to a tag',
    )
    args = parser.parse_args()

    if args.write:
        write_mode(args.write)
    else:
        scan_mode()


if __name__ == '__main__':
    main()
