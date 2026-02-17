# app/modules/dataset/fetchers/zip.py

import logging
import posixpath
import shutil
import tempfile
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from .base import Fetcher_Interface, FetchError

logger = logging.getLogger(__name__)


class ZipFetcher(Fetcher_Interface):
    EXTRACTABLE_EXTS = {".uvl"}
    MAX_ZIP_ENTRIES = 500

    def supports(self, url):
        try:
            return str(url).lower().endswith(".zip")
        except Exception:
            return False

    def fetch(self, url, dest_root, current_user=None):
        zip_path = Path(str(url))

        if not zip_path.exists():
            raise FetchError(f"ZIP file not found: {zip_path}")

        extract_root = Path(tempfile.mkdtemp(dir=dest_root, prefix="zip_"))
        logger.info(f"[ZipFetcher] Extracting {zip_path} into {extract_root}")

        extracted_any = False

        try:
            with ZipFile(zip_path, "r") as zf:
                infos = zf.infolist()
                if len(infos) > self.MAX_ZIP_ENTRIES:
                    raise FetchError("ZIP has too many entries")

                def safe_extract(member):
                    nonlocal extracted_any

                    if member.is_dir():
                        return None

                    raw_path = member.filename
                    norm_path = posixpath.normpath(raw_path)

                    if norm_path.startswith("/") or norm_path.startswith("..") or "/.." in norm_path:
                        raise FetchError("Unsafe path in ZIP")

                    ext = Path(norm_path).suffix.lower()
                    if ext not in self.EXTRACTABLE_EXTS:
                        return None

                    desired_name = Path(norm_path).name
                    target = extract_root / desired_name

                    i = 1
                    while target.exists():
                        stem = Path(desired_name).stem
                        suffix = Path(desired_name).suffix
                        target = extract_root / f"{stem} ({i}){suffix}"
                        i += 1

                    resolved = target.resolve()
                    base_resolved = extract_root.resolve()
                    if base_resolved not in resolved.parents and base_resolved != resolved:
                        raise FetchError("Unsafe path in ZIP")

                    with zf.open(member, "r") as src, open(resolved, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                    extracted_any = True
                    return resolved

                for info in infos:
                    safe_extract(info)

        except BadZipFile:
            raise FetchError("Invalid ZIP file")
        finally:
            try:
                if zip_path.exists() and zip_path.is_file():
                    zip_path.unlink()
            except Exception:
                pass

        if not extracted_any:
            try:
                extract_root.rmdir()
            except OSError:
                pass
            raise FetchError("ZIP processed, but no .uvl files were found")

        logger.info(f"[ZipFetcher] Extraction completed into {extract_root}")
        return extract_root
