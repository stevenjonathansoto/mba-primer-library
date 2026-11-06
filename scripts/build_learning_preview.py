"""Compatibility entry point for the reusable learning-page builder."""
from build_learning import ROOT, build
if __name__ == "__main__":
    for path in sorted((ROOT / "content").glob("*.json")): build(path)
