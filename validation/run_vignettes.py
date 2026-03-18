"""
hummingbird/validation/run_vignettes.py
Automated validation runner — runs all vignettes through the decision engine.

Usage:
    python validation/run_vignettes.py [--site lower_gi] [--verbose]

Minimum pass threshold: 96% (48/50)
Any failure on a Layer 1 case is an automatic block regardless of overall score.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from logic.hard_rules import check_hard_rules
from logic.claude_layer import call_claude, build_hard_rule_response


def load_vignettes(cancer_site: str) -> list[dict]:
    path = Path(__file__).parent / cancer_site / "vignettes.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # Filter out meta/notes entries
    return [v for v in data if "id" in v]


def run_single(vignette: dict) -> dict:
    inputs = vignette["inputs"]
    age_band = inputs["age_band"]
    sex = inputs["sex"]
    smoking = inputs.get("smoking", "Never")
    symptoms = inputs["symptoms"]
    modifiers = inputs.get("modifiers", [])
    free_text = inputs.get("free_text", "")

    hard_result = check_hard_rules(age_band, sex, symptoms, modifiers)

    if hard_result.triggered:
        result = build_hard_rule_response(hard_result.rule_name, hard_result.rule_description)
    else:
        result = call_claude(
            age_band=age_band,
            sex=sex,
            smoking=smoking,
            symptoms=symptoms,
            modifiers=modifiers,
            free_text=free_text,
        )

    return result


def main():
    parser = argparse.ArgumentParser(description="Run Hummingbird validation vignettes")
    parser.add_argument("--site", default="lower_gi", help="Cancer site (default: lower_gi)")
    parser.add_argument("--verbose", action="store_true", help="Show per-vignette detail")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"HUMMINGBIRD VALIDATION RUN")
    print(f"Cancer site: {args.site}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    vignettes = load_vignettes(args.site)
    if not vignettes:
        print("No vignettes found. Populate validation/lower_gi/vignettes.json first.")
        sys.exit(1)

    total = len(vignettes)
    passed = 0
    failed = []
    layer1_failed = []

    for v in vignettes:
        vid = v["id"]
        expected = v["expected_tier"]
        category = v.get("category", "ai_reasoning")

        try:
            result = run_single(v)
            actual = result.get("tier")
            ok = actual == expected
        except Exception as e:
            actual = f"ERROR: {e}"
            ok = False

        if ok:
            passed += 1
            if args.verbose:
                print(f"  ✓ {vid}: {actual}")
        else:
            failed.append({"id": vid, "expected": expected, "actual": actual, "description": v["description"]})
            if category == "layer1_hard_rule":
                layer1_failed.append(vid)
            if args.verbose:
                print(f"  ✗ {vid}: expected {expected}, got {actual}")
                print(f"    {v['description']}")

    # ── Results ──────────────────────────────────────────────────────────────
    pct = (passed / total * 100) if total else 0
    threshold = 96.0
    passed_overall = pct >= threshold and len(layer1_failed) == 0

    print(f"\nRESULTS: {passed}/{total} passed ({pct:.1f}%)")
    print(f"Threshold: {threshold}%")
    print(f"Layer 1 failures: {len(layer1_failed)}")

    if failed:
        print(f"\nFAILED CASES ({len(failed)}):")
        for f in failed:
            print(f"  {f['id']}: expected {f['expected']}, got {f['actual']}")
            print(f"    → {f['description']}")

    if layer1_failed:
        print(f"\n⛔ AUTOMATIC BLOCK: Layer 1 failures: {layer1_failed}")

    print(f"\n{'='*60}")
    if passed_overall:
        print("✅ VALIDATION PASSED — prompt may proceed to live deployment")
    else:
        print("❌ VALIDATION FAILED — do not deploy until issues resolved")
    print(f"{'='*60}\n")

    sys.exit(0 if passed_overall else 1)


if __name__ == "__main__":
    main()
