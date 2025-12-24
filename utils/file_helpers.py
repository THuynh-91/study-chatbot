import json
from pathlib import Path
from datetime import datetime, timezone


def project_dirs(project_id: str):
    base = Path("data") / "projects" / project_id

    # Points UPLOAD_DIR -> data/uploads
    upload_dir = base / "uploads"
    manifest_path = base / "manifest.json"

    # Makes the dir if it doesn't exist
    upload_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir, manifest_path


def load_manifest(manifest_path: Path):
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return []


def save_manifest(manifest_path: Path, manifest: list[dict]):
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def short_ts(iso_str: str) -> str:
    if not iso_str:
        return ""
    return iso_str.replace("T", " ")[:16]


def human_kb(nbytes: int) -> str:
    return f"{nbytes/1024:.1f} KB" if nbytes < 1024*1024 else f"{nbytes/1024/1024:.2f} MB"
