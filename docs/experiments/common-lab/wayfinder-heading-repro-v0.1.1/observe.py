"""Read actual rendered HTML and preserve a one-shot reproduction receipt."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
source = root / "fixture" / "map.md"
output = root / "fixture" / "map.html"
receipt = root / "observation.json"
html = output.read_text(encoding="utf-8")
match = re.search(r"const DATA = (.*);\nconst L =", html)
if not match:
    raise SystemExit("RENDERED_DATA_NOT_FOUND")
data = json.loads(match.group(1))
observed = {key: data[key] for key in ("decisions", "fog", "outOfScope")}
record = {
    "observed_at_utc": datetime.now(timezone.utc).isoformat(),
    "kind": "actual-renderer-output-data-reproduction",
    "scope": "Read generated HTML data; no browser comprehension or model behavior claim.",
    "source": str(source),
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "rendered_html": str(output),
    "rendered_html_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    "source_heading_spelling": ["Decisions-so-far", "Not-yet-specified", "Out-of-scope"],
    "renderer_expected_heading_spelling": ["Decisions so far", "Not yet specified", "Out of scope"],
    "expected_items_per_section": 1,
    "actual": observed,
    "information_loss_reproduced": all(value == [] for value in observed.values()),
    "control": {"ticket_count": len(data["tickets"]), "destination_present": bool(data["destination"])},
}
with receipt.open("x", encoding="utf-8") as stream:
    json.dump(record, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps(record, ensure_ascii=False, indent=2))
if not record["information_loss_reproduced"]:
    raise SystemExit("EXPECTED_REPRODUCTION_CHANGED")
