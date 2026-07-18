#!/usr/bin/env python3
"""Validate the public repository wrapper and its installable skill."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "deep-reading-coach"
REQUIRED = [
    ROOT / "README.md",
    ROOT / "README.en.md",
    ROOT / "LICENSE",
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / "assets" / "demo.gif",
    ROOT / "examples" / "first-whole-book-response.md",
    ROOT / "examples" / "install-smoke-test.md",
    ROOT / "evals" / "evals.json",
    ROOT / "evals" / "results.md",
    ROOT / "examples" / "note-review-response.md",
    ROOT / "examples" / "technical-boundary-response.md",
    ROOT / "CHANGELOG.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "SECURITY.md",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "scripts" / "inspect_book.py",
    SKILL / "test-prompts.json",
]
TEXT_SUFFIXES = {".md", ".json", ".py", ".txt", ".yaml", ".yml", ".html"}
RELEASE_PLACEHOLDER = "YOUR_" + "GITHUB_USERNAME"
PRIVATE_PATTERNS = [
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"/home/[A-Za-z0-9._-]+/"),
    re.compile(r"(?i)(api[_-]?key|access[_-]?token)\s*[:=]\s*['\"][^'\"]+"),
]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def validate(release: bool) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.is_file() or path.stat().st_size == 0:
            fail(f"missing or empty required file: {path.relative_to(ROOT)}", errors)

    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\n(.*?)\n---\n", skill_text, re.DOTALL)
    if not frontmatter:
        fail("SKILL.md frontmatter is missing or malformed", errors)
    else:
        header = frontmatter.group(1)
        try:
            metadata = yaml.safe_load(header)
            if not isinstance(metadata, dict):
                fail("SKILL.md frontmatter must be a YAML mapping", errors)
            else:
                if set(metadata) != {"name", "description"}:
                    fail("SKILL.md frontmatter must contain only name and description", errors)
                if metadata.get("name") != "deep-reading-coach":
                    fail("SKILL.md name must be deep-reading-coach", errors)
                if len(str(metadata.get("description", "")).strip()) < 120:
                    fail("SKILL.md description is too short for reliable public triggering", errors)
        except yaml.YAMLError as exc:
            fail(f"SKILL.md frontmatter is invalid YAML: {exc}", errors)
    for phase_heading in (
        "### Phase 1 — Source Reconstruction",
        "### Phase 2 — Critical Verification",
        "### Phase 3 — Integration and Transfer",
    ):
        if phase_heading not in skill_text:
            fail(f"SKILL.md is missing three-phase heading: {phase_heading}", errors)
    if "【读者判断】" in skill_text:
        fail("SKILL.md must keep reader judgment separate without adding a sixth evidence label", errors)

    try:
        marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        plugin = marketplace["plugins"][0]
        if plugin.get("strict") is not False:
            fail("skill-bundle marketplace entry must set strict=false", errors)
        for relative in plugin.get("skills", []):
            target = ROOT / relative
            if not (target / "SKILL.md").is_file():
                fail(f"marketplace skill path is invalid: {relative}", errors)
    except (OSError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        fail(f"invalid marketplace.json: {exc}", errors)

    try:
        evals = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        cases = evals.get("cases", [])
        if len(cases) < 8:
            fail("evals/evals.json must contain at least eight behavior cases", errors)
        case_ids = {case.get("id") for case in cases}
        for required_id in (
            "note-review",
            "notes-only-provisional-review",
            "phase-2-critical-verification",
            "phase-3-integration-without-browsing",
            "phase-3-partial-scope",
        ):
            if required_id not in case_ids:
                fail(f"evals/evals.json is missing phase behavior case: {required_id}", errors)
        for case in cases:
            if not case.get("prompt") or not case.get("assertions"):
                fail(f"eval case is incomplete: {case.get('id', '<missing id>')}", errors)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        fail(f"invalid evals/evals.json: {exc}", errors)

    try:
        prompts = json.loads((SKILL / "test-prompts.json").read_text(encoding="utf-8"))
        prompt_ids = {case.get("id") for case in prompts.get("evals", [])}
        for required_id in (
            "note-review-preserves-thinking",
            "notes-only-provisional-review",
            "phase-2-critical-verification",
            "phase-3-integration-without-browsing",
            "phase-3-partial-scope",
        ):
            if required_id not in prompt_ids:
                fail(f"test-prompts.json is missing phase behavior case: {required_id}", errors)
    except (OSError, json.JSONDecodeError, TypeError) as exc:
        fail(f"invalid test-prompts.json: {exc}", errors)

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                fail(f"private path or credential-like value in {path.relative_to(ROOT)}", errors)
        if release and RELEASE_PLACEHOLDER in text:
            fail(f"release placeholder remains in {path.relative_to(ROOT)}", errors)
        if path.suffix.lower() == ".md":
            for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
                target = target.strip().strip("<>")
                if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                relative_target = target.split("#", 1)[0]
                if relative_target and not (path.parent / relative_target).exists():
                    fail(f"broken relative Markdown link in {path.relative_to(ROOT)}: {target}", errors)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required_phrase in (
        "npx skills add",
        "## 三阶段阅读流程",
        "## 阅读笔记优先导航",
        "## 安全边界",
        "assets/demo.gif",
        "## 致谢",
    ):
        if required_phrase not in readme:
            fail(f"README is missing required public section or phrase: {required_phrase}", errors)

    if "MIT License" not in (ROOT / "LICENSE").read_text(encoding="utf-8"):
        fail("LICENSE is not an MIT license", errors)

    fixture = ROOT / "examples" / "fixtures" / "judgment.html"
    with tempfile.TemporaryDirectory(prefix="deep-reading-public-check-") as temporary:
        process = subprocess.run(
            [
                sys.executable,
                str(SKILL / "scripts" / "inspect_book.py"),
                str(fixture),
                "--output-dir",
                temporary,
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            fail(f"public example fixture failed inspection: {process.stderr.strip()}", errors)
        else:
            report = json.loads((Path(temporary) / "inspection.json").read_text(encoding="utf-8"))
            characters = report["coverage"]["total_characters"]
            units = report["coverage"]["source_units"]
            example = (ROOT / "examples" / "first-whole-book-response.md").read_text(encoding="utf-8")
            if report["status"] != "readable" or units != 3:
                fail("public example fixture no longer produces a readable three-unit report", errors)
            if f"共 {characters} 个字符" not in example:
                fail("public example character count is stale relative to the fixture", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true", help="Also reject publication placeholders.")
    args = parser.parse_args()
    errors = validate(args.release)
    if errors:
        for item in errors:
            print(f"FAIL: {item}")
        return 1
    print("PASS: public repository structure is valid")
    if not args.release:
        print(f"NOTE: run with --release after replacing {RELEASE_PLACEHOLDER}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
