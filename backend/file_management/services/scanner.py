"""
Virus scan hook for uploaded files.

``run_virus_scan`` is a pluggable hook called from the upload pipeline. It
prefers a real ClamAV daemon (``clamd``) when configured, and otherwise
falls back to a lightweight signature scanner so the File Management module
still records scan results out of the box. Results are persisted on the
related ``FileScan`` record and never raise, so a scanner outage cannot
break uploads.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils import timezone as dj_timezone

from .models import FileScan

if TYPE_CHECKING:
    from projects.models import ProjectDocument

logger = logging.getLogger(__name__)

#: Known plain-text test / malicious signatures checked by the fallback scanner.
SIGNATURES = {
    b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE": "EICAR-Test-Signature",
    b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR": "EICAR-Test-Signature",
    b"ClamAV-Test-Signature": "ClamAV-Test-Signature",
}

#: Extensions that are never allowed to be stored as project files.
BLOCKED_EXTENSIONS = {
    ".exe", ".dll", ".bat", ".cmd", ".com", ".scr", ".vbs", ".ps1",
    ".msi", ".js", ".jse", ".wsf", ".jar", ".sh", ".bin", ".apk",
    ".cpl", ".drv", ".hta", ".ocx", ".pif", ".reg", ".sys",
}


def _scan_with_clamav(file_obj) -> dict:
    """Scan with a live ClamAV daemon when ``clamd`` is available."""
    try:
        import clamd  # type: ignore
    except ImportError:
        return {"backend": "clamav", "available": False}

    host = getattr(settings, "CLAMD_HOST", "127.0.0.1")
    port = int(getattr(settings, "CLAMD_PORT", "3310"))
    timeout = int(getattr(settings, "CLAMD_TIMEOUT", "30"))
    try:
        if host == "unix":
            socket_path = getattr(settings, "CLAMD_UNIX_SOCKET", "/var/run/clamav/clamd.ctl")
            client = clamd.ClamdUnixSocket(path=socket_path, timeout=timeout)  # type: ignore
        else:
            client = clamd.ClamdNetworkSocket(host=host, port=port, timeout=timeout)  # type: ignore
        status = client.ping()
        if status.get("status") != "PONG":
            return {"backend": "clamav", "available": False}
    except Exception:  # noqa: BLE001 - daemon simply unreachable
        logger.warning("ClamAV daemon unreachable; falling back to signature scan")
        return {"backend": "clamav", "available": False}

    try:
        result = client.instream(file_obj.file)
    except Exception:  # noqa: BLE001
        return {"backend": "clamav", "available": True, "error": "scan failed"}
    file_obj.file.seek(0)

    verdict = (result or {}).get("stream", {})
    status = verdict.get("status", "ERROR").upper()
    signature = verdict.get("description") or ""
    if status in ("FOUND", "OK", "CLEAN"):
        clean = status in ("OK", "CLEAN")
        return {
            "backend": "clamav",
            "available": True,
            "clean": clean,
            "signature": "" if clean else signature,
        }
    return {"backend": "clamav", "available": True, "error": "unknown response"}


def _scan_with_signatures(file_obj) -> dict:
    """Read the head of the file and look for known signatures / extensions."""
    original_name = getattr(file_obj, "original_name", None) or getattr(
        getattr(file_obj, "file", None), "name", ""
    )
    ext = os.path.splitext(str(original_name))[1].lower()
    if ext in BLOCKED_EXTENSIONS:
        return {
            "backend": "signature",
            "clean": False,
            "signature": f"Blocked extension: {ext}",
        }

    head = b""
    try:
        file_obj.file.seek(0)
        head = file_obj.file.read(65536)
        file_obj.file.seek(0)
    except Exception:  # noqa: BLE001
        head = b""

    for pattern, name in SIGNATURES.items():
        if pattern in head:
            return {
                "backend": "signature",
                "clean": False,
                "signature": name,
            }
    return {"backend": "signature", "clean": True, "signature": ""}


def run_virus_scan(document: "ProjectDocument") -> FileScan:
    """
    Run the scan hook against ``document.file`` and persist the result.

    Creates or updates the related ``FileScan`` record. Never raises.
    """
    scan, _ = FileScan.objects.get_or_create(file=document)

    try:
        result = _scan_with_clamav(document)
        if not result.get("available") and not result.get("error"):
            result = _scan_with_signatures(document)

        clean = result.get("clean")
        if clean is True:
            scan.status = "clean"
        elif clean is False:
            scan.status = "infected"
        else:
            scan.status = "error"
        scan.scanner = result.get("backend", "unknown")
        scan.signature = result.get("signature", "") or ""
        scan.findings = {
            "backend": result.get("backend", "unknown"),
            "available": bool(result.get("available")),
            "error": result.get("error", ""),
        }
    except Exception as exc:  # noqa: BLE001 - hook must not break uploads
        logger.exception("Virus scan failed for file #%s", document.pk)
        scan.status = "error"
        scan.findings = {"error": str(exc)}
        scan.scanner = "unknown"

    scan.scanned_at = dj_timezone.now()
    scan.save()
    return scan
