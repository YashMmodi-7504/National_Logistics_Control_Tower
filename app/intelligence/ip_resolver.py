import requests


def get_public_ip() -> str | None:
    """Fetch public IP safely."""
    try:
        res = requests.get("https://api.ipify.org?format=json", timeout=2)
        return res.json().get("ip")
    except Exception:
        return None


def resolve_state_from_ip(ip: str) -> str | None:
    """
    Resolve Indian state from IP.
    Uses ipinfo.io (free tier).
    """
    try:
        res = requests.get(f"https://ipinfo.io/{ip}/json", timeout=2)
        data = res.json()

        region = data.get("region")  # e.g. "Gujarat"
        country = data.get("country")

        if country == "IN" and region:
            return region.strip()

        return None

    except Exception:
        return None
