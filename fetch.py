"""One-off read-only test: can GitHub Actions fetch MissAV/Jable ranking pages?

- No login, no playback, no video download, no paid service, no proxy.
- Only opens the 6 public ranking pages, records HTTP status / title /
  Turnstile indicators / whether ranking entries can be extracted,
  and writes fetch-result.json.
- Run once via workflow_dispatch; there is NO schedule in the workflow.
"""
import json
import re
import time

from scrapling.fetchers import StealthyFetcher

PAGES = [
    ("missav", "weekly", "https://missav.ws/dm170/cn/weekly-hot"),
    ("missav", "new", "https://missav.ws/dm635/cn/release"),
    ("missav", "actress", "https://missav.ws/cn/actresses/ranking"),
    ("jable", "weekly", "https://jable.tv/hot/"),
    ("jable", "new", "https://jable.tv/new-release/"),
    ("jable", "actress", "https://jable.tv/models/"),
]

CODE_RE = re.compile(r"\b([A-Za-z]{2,8}-\d{2,6}|FC2-PPV-\d{2,7})\b", re.I)
ACTRESS_HREF_RE = re.compile(r"/(?:models|actresses)/[^\"'/#?]+/?")


def extract(page, board):
    html = page.html or ""
    text = page.text or ""
    title = ""
    try:
        title = (page.css("title::text").get() or "").strip()
    except Exception:
        title = ""
    if board == "actress":
        seen, names = [], set()
        for m in ACTRESS_HREF_RE.finditer(html):
            # name is not reliably in the href; count distinct profile links
            if m.group(0) not in seen:
                seen.append(m.group(0))
        return {"title": title, "profile_links": len(seen),
                "sample_links": seen[:12], "text_len": len(text)}
    codes, seen = [], set()
    for m in CODE_RE.finditer(html):
        code = m.group(1).upper()
        if code not in seen:
            seen.add(code)
            codes.append(code)
        if len(codes) >= 12:
            break
    return {"title": title, "codes": codes, "count": len(codes),
            "text_len": len(text)}


def main():
    results = []
    for source, board, url in PAGES:
        started = time.time()
        rec = {"source": source, "board": board, "url": url,
               "status": None, "error": None}
        try:
            page = StealthyFetcher.fetch(
                url, headless=False, solve_cloudflare=True,
                network_idle=True, timeout=120000,
            )
            rec["status"] = getattr(page, "status", None)
            html = page.html or ""
            rec["html_len"] = len(html)
            rec["turnstile"] = any(
                s in html for s in (
                    "Just a moment", "cf-turnstile", "turnstile",
                    "Attention Required", "Checking your browser",
                )
            )
            rec["elapsed_s"] = round(time.time() - started, 1)
            rec.update(extract(page, board))
        except Exception as e:  # one page failing must not kill the run
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["elapsed_s"] = round(time.time() - started, 1)
        print(json.dumps(rec, ensure_ascii=False), flush=True)
        results.append(rec)
    with open("fetch-result.json", "w", encoding="utf-8") as f:
        json.dump({"pages": results}, f, ensure_ascii=False, indent=2)
    blocked = sum(
        1 for r in results
        if r.get("status") in (403, 429, 503) or r.get("turnstile") or r.get("error")
    )
    print(f"BLOCKED_OR_FAILED={blocked}/6", flush=True)


if __name__ == "__main__":
    main()
