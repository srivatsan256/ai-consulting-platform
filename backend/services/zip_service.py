"""
services/zip_service.py
Service for packaging generated project deliverables into a downloadable ZIP archive.
"""
import zipfile
from pathlib import Path
from typing import Dict
from django.conf import settings  # type: ignore


def package_project_deliverables(project_id: str, files_dict: Dict[str, str]) -> str:
    """
    Creates a ZIP file containing generated deliverable markdown files.

    Args:
        project_id: String UUID of the project.
        files_dict: Dictionary mapping filename (e.g. "BRD.md") to markdown string content.

    Returns:
        Relative URL path to the generated ZIP archive.
    """
    media_root = settings.MEDIA_ROOT if settings.MEDIA_ROOT is not None else "media"
    out_dir = Path(media_root) / "generated" / project_id
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_filename = f"deliverables_{project_id[:8]}.zip"
    zip_path = out_dir / zip_filename

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for fname, content in files_dict.items():
            zip_file.writestr(fname, content)

    relative_url = f"{settings.MEDIA_URL}generated/{project_id}/{zip_filename}"
    return relative_url
