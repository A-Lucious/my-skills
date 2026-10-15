"""Resolve project paths without binding the skill to one repository layout."""
import os
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]


def project_root():
    configured = os.environ.get("PIXEL_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    if SKILL.parent.name == "skills" and SKILL.parent.parent.name == ".agents":
        return SKILL.parents[2]
    return Path.cwd().resolve()


ROOT = project_root()


if __name__ == "__main__":
    print(ROOT)
