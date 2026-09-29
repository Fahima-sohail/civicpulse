"""Check common CivicPulse submission mistakes before pushing a release branch.

This is intentionally a lightweight repository lint, not a replacement for the
test suites, Docker Compose smoke test, Kubernetes deployment, or manual evidence.
Run it from the repository root with: ``python scripts/check_submission.py``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked(path: str) -> bool:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def require(path: str, failures: list[str]) -> None:
    if not (ROOT / path).is_file():
        failures.append(f"missing required file: {path}")


def require_text(path: str, expected: str, failures: list[str]) -> None:
    content = (ROOT / path).read_text(encoding="utf-8")
    if expected not in content:
        failures.append(f"{path} must contain: {expected}")


def main() -> int:
    failures: list[str] = []
    required_files = [
        "README.md",
        "docker-compose.yml",
        "compose.prod.yaml",
        "backend/Dockerfile",
        "frontend/Dockerfile",
        "backend/alembic/versions/0001_initial.py",
        "docs/ENGINEERING-NOTES.md",
        "docs/RUNBOOK.md",
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml",
        ".github/workflows/release.yml",
    ]
    for path in required_files:
        require(path, failures)

    if tracked(".env"):
        failures.append(".env is tracked; remove it from Git history and rotate any exposed credentials")

    if not failures:
        require_text("docker-compose.yml", "internal: true", failures)
        require_text("compose.prod.yaml", "${IMAGE_TAG}", failures)
        require_text(".github/workflows/ci.yml", "TRIAGE_PROVIDER: simulated", failures)
        require_text(".github/workflows/cd.yml", "needs: build_push", failures)
        require_text("backend/alembic/versions/0001_initial.py", "create_type=False", failures)

        production_compose = (ROOT / "compose.prod.yaml").read_text(encoding="utf-8")
        if "build:" in production_compose:
            failures.append("compose.prod.yaml must deploy images, not build from source")

        manifests = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "k8s").rglob("*.yaml"))
        if ":latest" in manifests:
            failures.append("Kubernetes manifests must not deploy a :latest image")

    if failures:
        print("Submission check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Submission check passed: core files and high-risk configuration guards are present.")
    print("Manual checks still required: branch protection, PR review evidence, demo video, GHCR/CD links, and load-test captures.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
