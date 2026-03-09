"""Generate TZD Labs logo mark via Gemini illustration.

Runs once to produce src/assets/tzdlabs_mark.png — a transparent PNG
suitable for embedding in charts via add_brand_mark().

Usage:
    uv run python scripts/generate_tzdlabs_logo.py
"""

from pathlib import Path

from flowmpl.illustrations import generate_illustration, remove_background

STORY = """
A network of interconnected physical nodes — substations, data centers, transmission
towers — seen from above as a systems diagram. Capital flows as arrows entering from
one edge and converting into physical infrastructure as they reach each node. Some
nodes are solid and permanent (structural); others are dashed (uncertain, contingent).
The overall composition suggests a map of consequences, not a map of geography.
This is the moment where financial decisions become physical commitments.
Clean, minimal, whiteboard aesthetic. No text or labels.
"""

VOCABULARY = [
    "transmission tower silhouette",
    "data center rectangular block",
    "substation node circle",
    "arrows showing directional flow between nodes",
    "solid bold lines for durable connections",
    "dashed thin lines for uncertain connections",
    "overhead aerial perspective, like a systems diagram",
    "white background, black ink only",
    "no text, no labels, no legends",
]

OUT_DIR = Path(__file__).parent.parent / "src" / "assets"
OUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_PATH = OUT_DIR / "tzdlabs_mark_raw.png"
FINAL_PATH = OUT_DIR / "tzdlabs_mark.png"


def main() -> None:
    print("Generating TZD Labs logo mark via Gemini...")
    generate_illustration(STORY, vocabulary=VOCABULARY, out_path=RAW_PATH)
    print(f"Raw image saved: {RAW_PATH}")

    print("Removing background for transparent PNG...")
    transparent = remove_background(RAW_PATH)
    FINAL_PATH.write_bytes(transparent)
    print(f"Done: {FINAL_PATH}")
    print()
    print("Next steps:")
    print("  open src/assets/tzdlabs_mark.png  # inspect result")
    print("  # If unsatisfactory, edit STORY/VOCABULARY and re-run")


if __name__ == "__main__":
    main()
