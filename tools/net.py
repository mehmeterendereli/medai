from typing import Dict, Any
import httpx


def http_get(args: Dict[str, Any]) -> Dict[str, Any]:
    url = args.get("url")
    with httpx.Client(timeout=30) as c:
        r = c.get(url)
        return {"status": r.status_code, "text": r.text[:200000]}


def download(args: Dict[str, Any]) -> str:
    url = args.get("url")
    dest = args.get("dest")
    with httpx.Client(timeout=None) as c:
        with c.stream("GET", url) as r:
            r.raise_for_status()
            with open(dest, 'wb') as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
    return dest
