#!/usr/bin/env python3
"""Generate images using the Gemini API.

Usage:
    uv run scripts/generate_image.py "your prompt here" -o path/to/output.png
    uv run scripts/generate_image.py "your prompt here"  # prints to stdout-like temp file
    uv run scripts/generate_image.py -f prompt.txt -o path/to/output.png

Examples:
    # Single image with aspect ratio
    uv run scripts/generate_image.py \
        "A photorealistic cat on a windowsill, golden hour lighting" \
        -o notebooks/images/cat.png --aspect-ratio 16:9

    # Prompt from a file
    uv run scripts/generate_image.py -f prompts/transformer_diptych.txt \
        -o notebooks/images/bespoke_vs_modular.png

    # Multiple images from the same prompt
    uv run scripts/generate_image.py "abstract geometry" \
        -o notebooks/images/geo.png --count 3

Environment:
    Reads NANOBANANA_GEMINI_API_KEY from .env in the project root,
    or from the environment directly.
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import shutil
import sys
from pathlib import Path

# Project root = two levels up from this script (scripts/ -> Systems/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    """Load .env file from project root if it exists."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = value


def get_api_key() -> str:
    """Get the Gemini API key from environment."""
    key = os.environ.get("NANOBANANA_GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        print(
            "Error: No API key found. Set NANOBANANA_GEMINI_API_KEY or GEMINI_API_KEY "
            "in .env or your environment.",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def generate_image(
    prompt: str,
    output_path: Path,
    *,
    aspect_ratio: str = "16:9",
    image_size: str = "1K",
    model: str = "gemini-3-pro-image-preview",
) -> bool:
    """Generate an image from a text prompt and save it to output_path."""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=get_api_key())

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)],
        ),
    ]
    config = types.GenerateContentConfig(
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size,
        ),
        response_modalities=["IMAGE", "TEXT"],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config,
    ):
        if chunk.parts is None:
            continue
        part = chunk.parts[0]
        if part.inline_data and part.inline_data.data:
            ext = mimetypes.guess_extension(part.inline_data.mime_type) or ".png"
            temp_path = output_path.parent / f".tmp_genimg{ext}"
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_bytes(part.inline_data.data)
            shutil.move(str(temp_path), str(output_path))
            print(f"Saved: {output_path}")
            return True
        elif hasattr(part, "text") and part.text:
            print(f"Model response: {part.text}", file=sys.stderr)

    print("Error: No image data received from the API.", file=sys.stderr)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate images using the Gemini API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", nargs="?", help="Text prompt for image generation")
    parser.add_argument("-f", "--file", type=Path, help="Read prompt from a text file")
    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Output file path (e.g. images/out.png)"
    )
    parser.add_argument("--aspect-ratio", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--image-size", default="1K", help="Image size (default: 1K)")
    parser.add_argument(
        "--model", default="gemini-3-pro-image-preview", help="Gemini model to use"
    )
    parser.add_argument(
        "--count", type=int, default=1, help="Number of images to generate (default: 1)"
    )

    args = parser.parse_args()

    # Resolve prompt source
    if args.file:
        if not args.file.exists():
            print(f"Error: Prompt file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        prompt = args.file.read_text().strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        parser.error("Provide a prompt as an argument or via --file")

    load_env()

    # Generate image(s)
    if args.count == 1:
        success = generate_image(
            prompt,
            args.output,
            aspect_ratio=args.aspect_ratio,
            image_size=args.image_size,
            model=args.model,
        )
        sys.exit(0 if success else 1)
    else:
        stem = args.output.stem
        suffix = args.output.suffix or ".png"
        parent = args.output.parent
        failures = 0
        for i in range(1, args.count + 1):
            out = parent / f"{stem}_{i}{suffix}"
            print(f"[{i}/{args.count}] Generating {out}...")
            if not generate_image(
                prompt,
                out,
                aspect_ratio=args.aspect_ratio,
                image_size=args.image_size,
                model=args.model,
            ):
                failures += 1
        if failures:
            print(f"{failures}/{args.count} images failed.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
