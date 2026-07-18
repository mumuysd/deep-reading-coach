#!/usr/bin/env python3
"""Inspect and extract supported book files without modifying the source.

Supported formats: PDF, EPUB, DOCX, TXT, Markdown, and HTML.
Outputs are written only after parsing finishes, and extracted text is explicitly
marked as machine-extracted rather than read or understood.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import posixpath
import re
import sys
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urldefrag
import xml.etree.ElementTree as ET


SCHEMA_VERSION = 2
TARGET_FILES = ("inspection.json", "toc.md", "content.md")
EPUB_MAX_ENTRIES = 5_000
EPUB_MAX_TOTAL_UNCOMPRESSED = 512 * 1024 * 1024
EPUB_MAX_MEMBER_UNCOMPRESSED = 64 * 1024 * 1024
EPUB_MAX_COMPRESSION_RATIO = 1_000
SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".epub": "epub",
    ".docx": "docx",
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".html": "html",
    ".htm": "html",
}


class InspectionError(Exception):
    """A controlled inspection failure with a stable diagnostic code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class Unit:
    title: str
    locator: str
    text: str
    role: str = "body"


@dataclass
class ParseResult:
    format: str
    parser: str
    locator_scheme: str
    directory_status: str
    metadata: dict[str, str] = field(default_factory=dict)
    units: list[Unit] = field(default_factory=list)
    toc: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    total_source_units: int = 0


def warning(code: str, message: str, locations: Iterable[str] | None = None,
            severity: str = "warning") -> dict[str, Any]:
    item: dict[str, Any] = {"code": code, "severity": severity, "message": message}
    if locations:
        item["locations"] = list(locations)
    return item


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    text = "\n".join(line.rstrip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_format(path: Path) -> str:
    suffix_format = SUPPORTED_EXTENSIONS.get(path.suffix.lower())
    prefix = path.read_bytes()[:8]

    if prefix.startswith(b"%PDF-"):
        return "pdf"

    if prefix.startswith(b"PK"):
        try:
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                if "mimetype" in names:
                    media = archive.read("mimetype").strip()
                    if media == b"application/epub+zip":
                        return "epub"
                if "word/document.xml" in names and "[Content_Types].xml" in names:
                    return "docx"
        except zipfile.BadZipFile:
            if suffix_format in {"epub", "docx"}:
                return suffix_format

    if suffix_format:
        return suffix_format

    unsupported = path.suffix.lower()
    if unsupported in {".mobi", ".azw", ".azw3"}:
        raise InspectionError(
            "unsupported_ebook_format",
            "MOBI/AZW/AZW3 is not supported in this version; provide a lawful DRM-free EPUB, PDF, DOCX, TXT, Markdown, or HTML copy.",
        )
    raise InspectionError("unsupported_format", f"Unsupported file format: {path.suffix or 'no extension'}")


def decode_text(data: bytes) -> tuple[str, str, list[dict[str, Any]]]:
    warnings: list[dict[str, Any]] = []
    candidates: list[str] = []
    if data.startswith((b"\xff\xfe", b"\xfe\xff")) or data.count(b"\x00") > max(2, len(data) // 20):
        candidates.extend(["utf-16", "utf-16-le", "utf-16-be"])
    candidates.extend(["utf-8-sig", "utf-8", "gb18030", "big5"])

    seen: set[str] = set()
    for encoding in candidates:
        if encoding in seen:
            continue
        seen.add(encoding)
        try:
            text = data.decode(encoding, errors="strict")
        except (UnicodeDecodeError, LookupError):
            continue
        if encoding not in {"utf-8", "utf-8-sig"}:
            warnings.append(warning(
                "non_utf8_encoding",
                f"Decoded with {encoding}; verify passages containing uncommon characters.",
                severity="info",
            ))
        return text, encoding, warnings

    text = data.decode("utf-8", errors="replace")
    warnings.append(warning(
        "lossy_decode",
        "No supported encoding decoded cleanly; replacement characters were inserted.",
    ))
    return text, "utf-8-with-replacement", warnings


def text_quality_warnings(text: str, locator: str) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    replacement_count = text.count("\ufffd")
    control_count = sum(1 for char in text if ord(char) < 32 and char not in "\n\t\r")
    if replacement_count:
        warnings.append(warning(
            "replacement_characters",
            f"Found {replacement_count} Unicode replacement characters.",
            [locator],
        ))
    if control_count:
        warnings.append(warning(
            "control_characters",
            f"Found {control_count} suspicious control characters.",
            [locator],
        ))
    return warnings


class HTMLTextExtractor(HTMLParser):
    BLOCKS = {
        "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt",
        "figcaption", "figure", "footer", "form", "header", "hr", "li", "main", "nav",
        "ol", "p", "pre", "section", "table", "tbody", "td", "tfoot", "th", "thead",
        "tr", "ul",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.heading_level: int | None = None
        self.in_title = False
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
            return
        if re.fullmatch(r"h[1-6]", tag):
            self.heading_level = int(tag[1])
            self.parts.append("\n" + "#" * self.heading_level + " ")
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = False
        if re.fullmatch(r"h[1-6]", tag):
            self.heading_level = None
            self.parts.append("\n")
        elif tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
            return
        if data.strip():
            self.parts.append(data)

    def result(self) -> tuple[str, str]:
        text = clean_text("".join(self.parts))
        title = clean_text(" ".join(self.title_parts))
        return text, title


class AnchorExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.href: str | None = None
        self.text_parts: list[str] = []
        self.entries: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            values = dict(attrs)
            self.href = values.get("href")
            self.text_parts = []

    def handle_data(self, data: str) -> None:
        if self.href is not None:
            self.text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self.href is not None:
            title = clean_text(" ".join(self.text_parts))
            if title:
                self.entries.append((title, self.href))
            self.href = None
            self.text_parts = []


def html_to_markdown(data: bytes) -> tuple[str, str, list[dict[str, Any]]]:
    decoded, encoding, warnings = decode_text(data)
    parser = HTMLTextExtractor()
    parser.feed(decoded)
    text, title = parser.result()
    warnings.extend(text_quality_warnings(text, "HTML extracted body"))
    if encoding:
        pass
    return text, title, warnings


def split_lines_into_units(text: str, format_name: str, source_name: str) -> tuple[list[Unit], list[dict[str, Any]]]:
    lines = text.splitlines()
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    chapter_pattern = re.compile(r"^\s*((?:第.{1,20}[章节卷部篇])|(?:chapter|part)\s+\S.*)\s*$", re.IGNORECASE)
    headings: list[tuple[int, str]] = []

    for index, line in enumerate(lines):
        match = heading_pattern.match(line) if format_name in {"markdown", "html"} else chapter_pattern.match(line)
        if match:
            title = match.group(2) if format_name in {"markdown", "html"} else match.group(1)
            headings.append((index, clean_text(title)))

    units: list[Unit] = []
    toc: list[dict[str, Any]] = []
    label = {"markdown": "Markdown", "html": "HTML", "txt": "TXT"}[format_name]

    if headings:
        for number, (start, title) in enumerate(headings):
            end = headings[number + 1][0] if number + 1 < len(headings) else len(lines)
            section_text = clean_text("\n".join(lines[start:end]))
            locator = f"{label}: {title}（源文本行 {start + 1}-{max(start + 1, end)}）"
            units.append(Unit(title=title, locator=locator, text=section_text))
            toc.append({"title": title, "locator": locator})
    else:
        chunk_size = 400
        for start in range(0, len(lines) or 1, chunk_size):
            end = min(start + chunk_size, len(lines))
            section_text = clean_text("\n".join(lines[start:end])) if lines else ""
            locator = f"{label}: 源文本行 {start + 1}-{max(start + 1, end)}"
            title = f"{source_name} 行 {start + 1}-{max(start + 1, end)}"
            units.append(Unit(title=title, locator=locator, text=section_text))
            toc.append({"title": title, "locator": locator})

    return units, toc


def parse_text_file(path: Path, format_name: str) -> ParseResult:
    data = path.read_bytes()
    decoded, encoding, warnings = decode_text(data)
    decoded = decoded.replace("\x00", "")
    cleaned = clean_text(decoded)
    warnings.extend(text_quality_warnings(cleaned, path.name))
    units, toc = split_lines_into_units(cleaned, format_name, path.name)
    has_headings = any(not item["title"].startswith(path.name + " 行 ") for item in toc)
    directory_status = "available" if has_headings else ("not_applicable" if format_name == "txt" else "missing")
    if directory_status == "missing":
        warnings.append(warning("missing_outline", "No headings were detected; source line ranges are used.", severity="info"))
    return ParseResult(
        format=format_name,
        parser=f"text-decoder:{encoding}",
        locator_scheme="heading and source-line range" if has_headings else "source-line range",
        directory_status=directory_status,
        metadata={"title": path.stem},
        units=units,
        toc=toc,
        warnings=warnings,
        total_source_units=len(units),
    )


def parse_html_file(path: Path) -> ParseResult:
    text, title, warnings = html_to_markdown(path.read_bytes())
    units, toc = split_lines_into_units(text, "html", path.name)
    has_headings = bool(re.search(r"^#{1,6}\s+", text, re.MULTILINE))
    if not has_headings:
        warnings.append(warning("missing_outline", "No HTML headings were detected; extracted line ranges are used.", severity="info"))
    return ParseResult(
        format="html",
        parser="stdlib-html.parser",
        locator_scheme="heading" if has_headings else "extracted source-line range",
        directory_status="available" if has_headings else "missing",
        metadata={"title": title or path.stem},
        units=units,
        toc=toc,
        warnings=warnings,
        total_source_units=len(units),
    )


def epub_nav_entries(archive: zipfile.ZipFile, nav_path: str) -> list[tuple[str, str]]:
    try:
        data = archive.read(nav_path)
    except KeyError:
        return []
    decoded, _, _ = decode_text(data)
    parser = AnchorExtractor()
    parser.feed(decoded)
    base = posixpath.dirname(nav_path)
    entries: list[tuple[str, str]] = []
    for title, href in parser.entries:
        href_no_fragment = urldefrag(unquote(href))[0]
        resolved = posixpath.normpath(posixpath.join(base, href_no_fragment))
        entries.append((title, resolved))
    return entries


def epub_ncx_entries(archive: zipfile.ZipFile, ncx_path: str) -> list[tuple[str, str]]:
    try:
        root = ET.fromstring(archive.read(ncx_path))
    except (KeyError, ET.ParseError):
        return []
    base = posixpath.dirname(ncx_path)
    entries: list[tuple[str, str]] = []
    for nav_point in root.iter():
        if local_name(nav_point.tag) != "navPoint":
            continue
        title = ""
        href = ""
        for child in nav_point.iter():
            name = local_name(child.tag)
            if name == "text" and not title:
                title = clean_text("".join(child.itertext()))
            elif name == "content" and not href:
                href = child.attrib.get("src", "")
        if title and href:
            resolved = posixpath.normpath(posixpath.join(base, urldefrag(unquote(href))[0]))
            entries.append((title, resolved))
    return entries


def validate_epub_archive(archive: zipfile.ZipFile) -> None:
    """Reject EPUB containers whose declared sizes are unsafe to process."""
    members = archive.infolist()
    if len(members) > EPUB_MAX_ENTRIES:
        raise InspectionError(
            "epub_too_many_entries",
            f"The EPUB contains {len(members)} archive entries; the safety limit is {EPUB_MAX_ENTRIES}.",
        )

    total_uncompressed = 0
    for member in members:
        total_uncompressed += member.file_size
        if member.file_size > EPUB_MAX_MEMBER_UNCOMPRESSED:
            raise InspectionError(
                "epub_member_too_large",
                f"The EPUB member {member.filename!r} declares {member.file_size} uncompressed bytes; the per-file safety limit is {EPUB_MAX_MEMBER_UNCOMPRESSED}.",
            )
        if member.file_size and member.compress_size == 0:
            raise InspectionError(
                "epub_suspicious_compression",
                f"The EPUB member {member.filename!r} has an invalid compressed size.",
            )
        if member.compress_size and member.file_size / member.compress_size > EPUB_MAX_COMPRESSION_RATIO:
            raise InspectionError(
                "epub_suspicious_compression",
                f"The EPUB member {member.filename!r} exceeds the compression-ratio safety limit.",
            )
    if total_uncompressed > EPUB_MAX_TOTAL_UNCOMPRESSED:
        raise InspectionError(
            "epub_too_large",
            f"The EPUB declares {total_uncompressed} uncompressed bytes; the total safety limit is {EPUB_MAX_TOTAL_UNCOMPRESSED}.",
        )


def classify_epub_role(title: str, internal_path: str, properties: str) -> str:
    """Classify spine units without discarding provenance-bearing front/back matter."""
    haystack = " ".join((title, internal_path, properties)).casefold()
    normalized = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", haystack)
    tokens = set(normalized.split())

    if "nav" in properties.split() or tokens.intersection({"toc", "contents", "navigation"}) or any(
        phrase in haystack for phrase in ("table of contents", "目录", "目次")
    ):
        return "navigation"
    if tokens.intersection({"cover", "frontcover", "titlepage"}) or any(
        phrase in haystack for phrase in ("title page", "封面", "扉页")
    ):
        return "cover"
    if tokens.intersection({"license", "licence", "copyright", "legal", "colophon"}) or any(
        phrase in haystack for phrase in ("legal notice", "copyright notice", "版权", "许可协议", "授权条款")
    ):
        return "legal"
    return "body"


def parse_epub(path: Path) -> ParseResult:
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        raise InspectionError("damaged_epub", "The EPUB is not a readable ZIP container.") from exc

    with archive:
        validate_epub_archive(archive)
        names = set(archive.namelist())
        warnings: list[dict[str, Any]] = []
        if "META-INF/encryption.xml" in names:
            warnings.append(warning(
                "encrypted_epub_resources",
                "The EPUB declares encrypted resources; some body files may be DRM-protected or unreadable.",
            ))

        try:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            rootfile = next(
                element.attrib.get("full-path", "")
                for element in container.iter()
                if local_name(element.tag) == "rootfile" and element.attrib.get("full-path")
            )
            opf = ET.fromstring(archive.read(rootfile))
        except (KeyError, ET.ParseError, StopIteration) as exc:
            raise InspectionError("damaged_epub", "The EPUB container or package document is missing or malformed.") from exc

        opf_dir = posixpath.dirname(rootfile)
        metadata: dict[str, str] = {}
        for element in opf.iter():
            name = local_name(element.tag)
            value = clean_text("".join(element.itertext()))
            if name == "title" and value and "title" not in metadata:
                metadata["title"] = value
            elif name == "creator" and value and "author" not in metadata:
                metadata["author"] = value

        manifest: dict[str, dict[str, str]] = {}
        spine_ids: list[str] = []
        spine_toc_id = ""
        for element in opf.iter():
            name = local_name(element.tag)
            if name == "item" and element.attrib.get("id") and element.attrib.get("href"):
                manifest[element.attrib["id"]] = {
                    "href": element.attrib["href"],
                    "media_type": element.attrib.get("media-type", ""),
                    "properties": element.attrib.get("properties", ""),
                }
            elif name == "spine":
                spine_toc_id = element.attrib.get("toc", "")
                for child in list(element):
                    if local_name(child.tag) == "itemref" and child.attrib.get("idref"):
                        spine_ids.append(child.attrib["idref"])

        nav_entries: list[tuple[str, str]] = []
        for item in manifest.values():
            if "nav" in item["properties"].split():
                nav_path = posixpath.normpath(posixpath.join(opf_dir, unquote(item["href"])))
                nav_entries = epub_nav_entries(archive, nav_path)
                break
        if not nav_entries and spine_toc_id in manifest:
            ncx_path = posixpath.normpath(posixpath.join(opf_dir, unquote(manifest[spine_toc_id]["href"])))
            nav_entries = epub_ncx_entries(archive, ncx_path)

        nav_titles = {href: title for title, href in nav_entries}
        units: list[Unit] = []
        toc: list[dict[str, Any]] = []
        failed_body_items: list[str] = []
        failed_non_body_items: list[str] = []
        empty_body_items: list[str] = []
        empty_non_body_items: list[str] = []

        for idref in spine_ids:
            item = manifest.get(idref)
            if not item or item["media_type"] not in {"application/xhtml+xml", "text/html"}:
                continue
            internal_path = posixpath.normpath(posixpath.join(opf_dir, unquote(item["href"])))
            role_hint = classify_epub_role(
                nav_titles.get(internal_path) or posixpath.basename(internal_path),
                internal_path,
                item["properties"],
            )
            try:
                body, html_title, item_warnings = html_to_markdown(archive.read(internal_path))
            except (KeyError, UnicodeError, ValueError):
                if role_hint == "body":
                    failed_body_items.append(internal_path)
                else:
                    failed_non_body_items.append(internal_path)
                continue
            warnings.extend(item_warnings)
            first_heading = re.search(r"^#{1,6}\s+(.+)$", body, re.MULTILINE)
            title = nav_titles.get(internal_path) or (first_heading.group(1).strip() if first_heading else "") or html_title or posixpath.basename(internal_path)
            locator = f"EPUB: {title} [{internal_path}]"
            role = classify_epub_role(title, internal_path, item["properties"])
            units.append(Unit(title=title, locator=locator, text=body, role=role))
            toc.append({"title": title, "locator": locator, "role": role})
            if not body:
                if role == "body":
                    empty_body_items.append(locator)
                else:
                    empty_non_body_items.append(locator)

        if failed_body_items:
            warnings.append(warning(
                "unreadable_spine_items",
                f"Failed to read {len(failed_body_items)} EPUB body spine items.",
                failed_body_items,
            ))
        if failed_non_body_items:
            warnings.append(warning(
                "unreadable_non_body_spine_items",
                f"Failed to read {len(failed_non_body_items)} cover, navigation, or legal spine items; readable body status is unchanged.",
                failed_non_body_items,
                severity="info",
            ))
        if empty_body_items:
            warnings.append(warning(
                "empty_spine_items",
                f"Found {len(empty_body_items)} empty EPUB body spine items.",
                empty_body_items,
            ))
        if empty_non_body_items:
            warnings.append(warning(
                "empty_non_body_spine_items",
                f"Found {len(empty_non_body_items)} empty cover, navigation, or legal spine items; they do not reduce body readability.",
                empty_non_body_items,
                severity="info",
            ))
        directory_status = "available" if nav_entries else "missing"
        if not nav_entries:
            warnings.append(warning(
                "missing_epub_navigation",
                "No readable EPUB navigation document was found; spine order is used as a structural index.",
                severity="info",
            ))

        return ParseResult(
            format="epub",
            parser="stdlib-zipfile+xml+html.parser",
            locator_scheme="chapter title and internal source file",
            directory_status=directory_status,
            metadata=metadata or {"title": path.stem},
            units=units,
            toc=toc,
            warnings=warnings,
            total_source_units=len(spine_ids),
        )


def flatten_pdf_outline(reader: Any, items: Any, output: list[dict[str, Any]]) -> None:
    if not isinstance(items, list):
        return
    for item in items:
        if isinstance(item, list):
            flatten_pdf_outline(reader, item, output)
            continue
        title = clean_text(str(getattr(item, "title", "")))
        if not title:
            continue
        try:
            page_number = reader.get_destination_page_number(item) + 1
            locator = f"PDF 第 {page_number} 页"
        except Exception:
            locator = "PDF 书签（页码无法确认）"
        output.append({"title": title, "locator": locator})


def parse_pdf(path: Path) -> ParseResult:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise InspectionError(
            "missing_pdf_dependency",
            "PDF inspection requires pypdf. Use a runtime-provided document environment or install pypdf.",
        ) from exc

    try:
        reader = PdfReader(str(path), strict=False)
    except Exception as exc:
        raise InspectionError("damaged_pdf", f"The PDF could not be opened: {exc}") from exc

    warnings: list[dict[str, Any]] = []
    if reader.is_encrypted:
        try:
            result = reader.decrypt("")
        except Exception:
            result = 0
        if not result:
            raise InspectionError("encrypted_pdf", "The PDF is encrypted and cannot be read without a password.")
        warnings.append(warning(
            "encrypted_pdf_empty_password",
            "The PDF is encrypted but opened with an empty password; verify that all pages extracted correctly.",
        ))

    metadata: dict[str, str] = {}
    raw_metadata = reader.metadata or {}
    if raw_metadata.get("/Title"):
        metadata["title"] = clean_text(str(raw_metadata["/Title"]))
    if raw_metadata.get("/Author"):
        metadata["author"] = clean_text(str(raw_metadata["/Author"]))
    if not metadata.get("title"):
        metadata["title"] = path.stem

    units: list[Unit] = []
    failed_pages: list[str] = []
    blank_pages: list[str] = []
    readable_pages = 0
    for index, page in enumerate(reader.pages, start=1):
        locator = f"PDF 第 {index} 页"
        try:
            text = clean_text(page.extract_text() or "")
        except Exception:
            text = ""
            failed_pages.append(locator)
        if len(text) >= 20:
            readable_pages += 1
        if not text:
            blank_pages.append(locator)
        units.append(Unit(title=locator, locator=locator, text=text))

    toc: list[dict[str, Any]] = []
    try:
        flatten_pdf_outline(reader, reader.outline, toc)
    except Exception:
        toc = []

    total_pages = len(reader.pages)
    total_chars = sum(len(unit.text) for unit in units)
    if failed_pages:
        warnings.append(warning("page_extraction_failed", f"Failed to extract {len(failed_pages)} PDF pages.", failed_pages))
    if blank_pages:
        warnings.append(warning("blank_or_image_pages", f"Found {len(blank_pages)} pages without extractable text.", blank_pages))
    if total_pages and (readable_pages / total_pages < 0.5 or total_chars / total_pages < 50):
        warnings.append(warning(
            "possible_scanned_pdf",
            "Text coverage is low; this may be a scanned or image-heavy PDF. OCR is not included in this Skill version.",
        ))
    if not toc:
        warnings.append(warning(
            "missing_pdf_bookmarks",
            "No readable embedded PDF bookmarks were found; page locators remain available.",
            severity="info",
        ))

    return ParseResult(
        format="pdf",
        parser="pypdf",
        locator_scheme="actual PDF page number",
        directory_status="available" if toc else "missing",
        metadata=metadata,
        units=units,
        toc=toc or [{"title": unit.title, "locator": unit.locator} for unit in units],
        warnings=warnings,
        total_source_units=total_pages,
    )


def iter_docx_blocks(document: Any) -> Iterable[tuple[str, Any]]:
    try:
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise InspectionError(
            "missing_docx_dependency",
            "DOCX inspection requires python-docx. Use a runtime-provided document environment or install python-docx.",
        ) from exc

    for child in document.element.body.iterchildren():
        if local_name(child.tag) == "p":
            yield "paragraph", Paragraph(child, document)
        elif local_name(child.tag) == "tbl":
            yield "table", Table(child, document)


def parse_docx(path: Path) -> ParseResult:
    try:
        from docx import Document
    except ImportError as exc:
        raise InspectionError(
            "missing_docx_dependency",
            "DOCX inspection requires python-docx. Use a runtime-provided document environment or install python-docx.",
        ) from exc

    try:
        document = Document(str(path))
    except Exception as exc:
        raise InspectionError("damaged_docx", f"The DOCX could not be opened: {exc}") from exc

    metadata: dict[str, str] = {}
    try:
        if document.core_properties.title:
            metadata["title"] = clean_text(document.core_properties.title)
        if document.core_properties.author:
            metadata["author"] = clean_text(document.core_properties.author)
    except Exception:
        pass
    if not metadata.get("title"):
        metadata["title"] = path.stem

    sections: list[tuple[str, list[str]]] = []
    current_title = "文档开始"
    current_parts: list[str] = []
    toc: list[dict[str, Any]] = []
    heading_counts: dict[str, int] = {}

    def flush() -> None:
        nonlocal current_parts
        if current_parts or not sections:
            sections.append((current_title, current_parts))
        current_parts = []

    for kind, block in iter_docx_blocks(document):
        if kind == "paragraph":
            text = clean_text(block.text or "")
            style_name = clean_text(getattr(getattr(block, "style", None), "name", "") or "")
            is_heading = bool(re.match(r"^(Heading|标题)\s*\d*", style_name, re.IGNORECASE)) and bool(text)
            if is_heading:
                if current_parts:
                    flush()
                current_title = text
                heading_counts[text] = heading_counts.get(text, 0) + 1
                suffix = f"（第 {heading_counts[text]} 处）" if heading_counts[text] > 1 else ""
                locator = f"DOCX: {text}{suffix}"
                toc.append({"title": text, "locator": locator})
                current_parts.append(f"# {text}")
            elif text:
                current_parts.append(text)
        else:
            rows: list[str] = []
            for row in block.rows:
                cells = [clean_text(cell.text or "").replace("\n", " ") for cell in row.cells]
                rows.append(" | ".join(cells))
            if rows:
                current_parts.append("\n".join(rows))
    if current_parts or not sections:
        flush()

    units: list[Unit] = []
    for index, (title, parts) in enumerate(sections, start=1):
        occurrence = sum(1 for previous, _ in sections[:index] if previous == title)
        suffix = f"（第 {occurrence} 处）" if occurrence > 1 else ""
        locator = f"DOCX: {title}{suffix}"
        units.append(Unit(title=title, locator=locator, text=clean_text("\n\n".join(parts))))

    warnings: list[dict[str, Any]] = []
    if not toc:
        warnings.append(warning(
            "missing_docx_headings",
            "No DOCX heading styles were detected; the document-start locator is used.",
            severity="info",
        ))
        toc = [{"title": unit.title, "locator": unit.locator} for unit in units]

    return ParseResult(
        format="docx",
        parser="python-docx",
        locator_scheme="heading path; no fixed page numbers",
        directory_status="available" if len(toc) > 1 or toc[0]["title"] != "文档开始" else "missing",
        metadata=metadata,
        units=units,
        toc=toc,
        warnings=warnings,
        total_source_units=len(sections),
    )


def parse_book(path: Path, format_name: str) -> ParseResult:
    if format_name == "pdf":
        return parse_pdf(path)
    if format_name == "epub":
        return parse_epub(path)
    if format_name == "docx":
        return parse_docx(path)
    if format_name in {"txt", "markdown"}:
        return parse_text_file(path, format_name)
    if format_name == "html":
        return parse_html_file(path)
    raise InspectionError("unsupported_format", f"Unsupported format: {format_name}")


def build_inspection(path: Path, result: ParseResult) -> dict[str, Any]:
    readable_units = [unit for unit in result.units if clean_text(unit.text)]
    empty_units = [unit.locator for unit in result.units if not clean_text(unit.text)]
    body_units = [unit for unit in result.units if unit.role == "body"]
    readable_body_units = [unit for unit in body_units if clean_text(unit.text)]
    empty_body_units = [unit.locator for unit in body_units if not clean_text(unit.text)]
    total_characters = sum(len(clean_text(unit.text)) for unit in result.units)
    body_characters = sum(len(clean_text(unit.text)) for unit in body_units)
    replacement_characters = sum(unit.text.count("\ufffd") for unit in result.units)
    role_counts: dict[str, int] = {}
    for unit in result.units:
        role_counts[unit.role] = role_counts.get(unit.role, 0) + 1

    if empty_body_units and not any(item["code"] in {"blank_or_image_pages", "empty_spine_items"} for item in result.warnings):
        result.warnings.append(warning(
            "empty_units",
            f"Found {len(empty_body_units)} body units without extractable text.",
            empty_body_units,
        ))

    material_warnings = [item for item in result.warnings if item.get("severity") in {"warning", "error"}]
    if not readable_body_units or body_characters == 0:
        status = "unreadable"
        body_status = "unreadable"
    elif material_warnings:
        status = "partial"
        body_status = "partial"
    else:
        status = "readable"
        body_status = "readable"

    return {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "path": str(path.resolve()),
            "name": path.name,
            "size_bytes": path.stat().st_size,
            "sha256": file_sha256(path),
        },
        "format": result.format,
        "status": status,
        "parser": result.parser,
        "metadata": result.metadata,
        "directory_status": result.directory_status,
        "body_status": body_status,
        "locator_scheme": result.locator_scheme,
        "coverage": {
            "source_units": result.total_source_units,
            "extracted_units": len(result.units),
            "readable_units": len(readable_units),
            "empty_units": len(empty_units),
            "total_characters": total_characters,
            "body_units": len(body_units),
            "readable_body_units": len(readable_body_units),
            "empty_body_units": len(empty_body_units),
            "body_characters": body_characters,
            "role_counts": role_counts,
            "replacement_characters": replacement_characters,
        },
        "mechanical_inspection": {
            "scope": "All units exposed by the parser were mechanically processed.",
            "reading_claim": "Extraction does not mean the book has been fully read or understood.",
        },
        "warnings": result.warnings,
        "outputs": {
            "inspection": "inspection.json",
            "toc": "toc.md" if result.toc else None,
            "content": "content.md" if total_characters else None,
        },
    }


def build_failure_inspection(path: Path, format_name: str | None, error: InspectionError) -> dict[str, Any]:
    source: dict[str, Any] = {"path": str(path.resolve()), "name": path.name}
    if path.exists() and path.is_file():
        source.update({"size_bytes": path.stat().st_size, "sha256": file_sha256(path)})
    return {
        "schema_version": SCHEMA_VERSION,
        "source": source,
        "format": format_name,
        "status": "unreadable",
        "directory_status": "unreadable",
        "body_status": "unreadable",
        "coverage": {
            "source_units": 0,
            "extracted_units": 0,
            "readable_units": 0,
            "empty_units": 0,
            "total_characters": 0,
            "body_units": 0,
            "readable_body_units": 0,
            "empty_body_units": 0,
            "body_characters": 0,
            "role_counts": {},
            "replacement_characters": 0,
        },
        "mechanical_inspection": {
            "scope": "Parsing stopped before readable body units were produced.",
            "reading_claim": "No content analysis is supported by this inspection.",
        },
        "warnings": [warning(error.code, error.message, severity="error")],
        "outputs": {"inspection": "inspection.json", "toc": None, "content": None},
    }


def render_toc(result: ParseResult) -> str:
    lines = [
        "# 临时结构索引",
        "",
        "> 这是解析器生成的定位索引，不代表原书一定提供了同样的正式目录。",
        "",
    ]
    for item in result.toc:
        role = item.get("role", "body")
        lines.append(f"- [{role}] {item['title']} — {item['locator']}")
    return "\n".join(lines).rstrip() + "\n"


def render_content(path: Path, result: ParseResult) -> str:
    lines = [
        "# 临时解析正文",
        "",
        f"来源文件：{path.name}",
        f"格式：{result.format}",
        "",
        "> 以下内容由程序机械提取。成功提取不等于已经完整阅读、理解或验证。",
        "",
    ]
    for index, unit in enumerate(result.units, start=1):
        lines.extend([
            f"## 解析单元 {index}: {unit.title}",
            "",
            f"定位：{unit.locator}",
            "",
            f"内容角色：{unit.role}",
            "",
            unit.text or "[无可提取正文]",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def prepare_output_dir(output_dir: Path) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        raise InspectionError("invalid_output_directory", "The output path exists and is not a directory.")
    output_dir.mkdir(parents=True, exist_ok=True)
    collisions = [name for name in TARGET_FILES if (output_dir / name).exists()]
    if collisions:
        raise InspectionError(
            "output_not_fresh",
            "Use a fresh temporary output directory; existing report files would make the result ambiguous: " + ", ".join(collisions),
        )


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def write_outputs(output_dir: Path, inspection: dict[str, Any], path: Path,
                  result: ParseResult | None) -> None:
    prepare_output_dir(output_dir)
    if result and result.toc:
        atomic_write(output_dir / "toc.md", render_toc(result))
    if result and inspection["coverage"]["total_characters"]:
        atomic_write(output_dir / "content.md", render_content(path, result))
    atomic_write(
        output_dir / "inspection.json",
        json.dumps(inspection, ensure_ascii=False, indent=2) + "\n",
    )


def dependency_report() -> dict[str, Any]:
    dependencies = {
        "pdf": {
            "module": "pypdf",
            "available": importlib.util.find_spec("pypdf") is not None,
        },
        "docx": {
            "module": "docx",
            "available": importlib.util.find_spec("docx") is not None,
        },
    }
    return {
        "status": "ready" if all(item["available"] for item in dependencies.values()) else "partial",
        "standard_library_formats": ["epub", "txt", "markdown", "html"],
        "optional_dependencies": dependencies,
        "note": "A partial result means EPUB/TXT/Markdown/HTML remain available; use a runtime-provided document environment or install the missing PDF or DOCX module.",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect and temporarily extract PDF, EPUB, DOCX, TXT, Markdown, or HTML books.",
    )
    parser.add_argument("book_file", nargs="?", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--check-dependencies",
        action="store_true",
        help="Print dependency availability as JSON without reading a book.",
    )
    args = parser.parse_args(argv)
    if not args.check_dependencies and (args.book_file is None or args.output_dir is None):
        parser.error("book_file and --output-dir are required unless --check-dependencies is used")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.check_dependencies:
        print(json.dumps(dependency_report(), ensure_ascii=False, indent=2))
        return 0

    path: Path = args.book_file.expanduser()
    format_name: str | None = None
    result: ParseResult | None = None

    try:
        if not path.exists():
            raise InspectionError("file_not_found", f"Book file does not exist: {path}")
        if not path.is_file():
            raise InspectionError("not_a_file", f"Book path is not a file: {path}")
        format_name = detect_format(path)
        result = parse_book(path, format_name)
        inspection = build_inspection(path, result)
    except InspectionError as error:
        inspection = build_failure_inspection(path, format_name, error)
    except Exception as error:  # Preserve a report without pretending parsing succeeded.
        controlled = InspectionError("unexpected_parser_error", f"Unexpected parser failure: {type(error).__name__}: {error}")
        inspection = build_failure_inspection(path, format_name, controlled)

    try:
        write_outputs(args.output_dir.expanduser(), inspection, path, result)
    except InspectionError as error:
        print(json.dumps({"status": "unreadable", "error": error.code, "message": error.message}, ensure_ascii=False), file=sys.stderr)
        return 2

    print(json.dumps({
        "status": inspection["status"],
        "inspection": str((args.output_dir / "inspection.json").resolve()),
        "toc": inspection["outputs"].get("toc"),
        "content": inspection["outputs"].get("content"),
    }, ensure_ascii=False))
    return 0 if inspection["status"] in {"readable", "partial"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
