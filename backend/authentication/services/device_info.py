"""
Lightweight user-agent parsing.

Used to populate UserSession device metadata without external dependencies.
"""

from __future__ import annotations

from typing import Tuple


def parse_user_agent(user_agent: str) -> Tuple[str, str, str]:
    """
    Parse a User-Agent string into (browser, operating_system, device_type).

    Returns
    -------
    tuple[str, str, str]
        Browser, operating system and device type.
    """
    if not user_agent:
        return "", "", ""

    ua = user_agent.lower()

    # Browser
    browser = ""
    for name, markers in {
        "Edge": ("edg/", "edge/"),
        "Opera": ("opr/", "opera/"),
        "Chrome": ("chrome/", "crios/"),
        "Firefox": ("firefox/", "fxios/"),
        "Safari": ("safari/",),
    }.items():
        if any(marker in ua for marker in markers):
            browser = name
            break

    # Operating system
    if "android" in ua:
        operating_system = "Android"
    elif "iphone" in ua or "ipad" in ua or "ios" in ua:
        operating_system = "iOS"
    elif "windows" in ua:
        operating_system = "Windows"
    elif "mac os" in ua or "macintosh" in ua:
        operating_system = "macOS"
    elif "linux" in ua:
        operating_system = "Linux"
    else:
        operating_system = ""

    # Device type
    if "ipad" in ua or "tablet" in ua:
        device_type = "Tablet"
    elif "iphone" in ua or "mobile" in ua or "android" in ua:
        device_type = "Mobile"
    else:
        device_type = "Desktop"

    return browser, operating_system, device_type
