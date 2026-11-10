"""Noor SmartScan — lightweight offline image-to-PDF utility.

The first release works with files produced by a scanner or camera. It does not
claim to acquire images directly from scanners or to perform perspective crop.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageEnhance, ImageOps, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


def open_page(path: str | Path) -> Image.Image:
    """Load one image safely and return an independent, display-oriented RGB copy."""
    source = Path(path)
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported image format: {source.suffix or '(no extension)'}")
    try:
        with Image.open(source) as im:
            im = ImageOps.exif_transpose(im)
            im.load()
            return im.convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"Cannot read image: {source.name}: {exc}") from exc


def enhance_page(image: Image.Image, mode: str = "Original") -> Image.Image:
    """Return an enhanced copy; supported presets are Original, Grayscale, Clear B&W."""
    image = image.convert("RGB")
    if mode == "Original":
        return image.copy()
    if mode == "Grayscale":
        return ImageOps.grayscale(image).convert("RGB")
    if mode == "Clear B&W":
        gray = ImageOps.grayscale(image)
        gray = ImageOps.autocontrast(gray, cutoff=1)
        return gray.point(lambda px: 255 if px > 180 else 0).convert("RGB")
    raise ValueError(f"Unknown enhancement preset: {mode}")


def export_pdf(paths: Iterable[str | Path], output: str | Path, dpi: int = 300,
               mode: str = "Original") -> Path:
    """Export input images in the supplied order to a multi-page PDF.

    Each page uses the image's pixel dimensions at the requested DPI. Source files
    are never modified. Existing output is replaced only after all pages load.
    """
    if not 72 <= int(dpi) <= 1200:
        raise ValueError("DPI must be between 72 and 1200")
    inputs = [Path(p) for p in paths]
    if not inputs:
        raise ValueError("Add at least one image before exporting")
    target = Path(output)
    if target.suffix.lower() != ".pdf":
        raise ValueError("Output filename must end in .pdf")
    if any(p.resolve() == target.resolve() for p in inputs if p.exists()):
        raise ValueError("Output file must not overwrite an input image")

    pages = [enhance_page(open_page(p), mode) for p in inputs]
    target.parent.mkdir(parents=True, exist_ok=True)
    # Save to a temporary sibling first so a failed export does not leave a partial PDF.
    temporary = target.with_name(target.stem + ".tmp.pdf")
    try:
        pages[0].save(temporary, "PDF", resolution=int(dpi), save_all=True,
                      append_images=pages[1:])
        temporary.replace(target)
    finally:
        for page in pages:
            page.close()
        if temporary.exists():
            temporary.unlink()
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Offline image-to-PDF utility")
    parser.add_argument("images", nargs="*", help="Input image files, in page order")
    parser.add_argument("-o", "--output", help="Output PDF path")
    parser.add_argument("--dpi", type=int, default=300)
    parser.add_argument("--preset", choices=("Original", "Grayscale", "Clear B&W"), default="Original")
    args = parser.parse_args()
    if not args.images:
        if sys.platform != "win32":
            parser.error("Run the GUI on Windows, or supply image paths and --output")
        from noor_smartscan_gui import run_gui
        run_gui()
        return
    if not args.output:
        parser.error("--output is required when image paths are supplied")
    try:
        result = export_pdf(args.images, args.output, args.dpi, args.preset)
        print(f"Created: {result}")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
