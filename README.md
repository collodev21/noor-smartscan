# Noor SmartScan — Day 1 foundation

A lightweight, offline-first Windows utility for turning scanned or photographed pages into a multi-page PDF. It is designed for small print/copy shops and ordinary office computers.

## Day 1 scope

Implemented: select common image files; arrange page order; remove pages; rotate a selected page; preview; apply Original, Grayscale or Clear B&W; export a multi-page PDF at a selectable DPI. Source images are not intentionally overwritten. Unicode file paths are supported by Python's path handling.

**Not implemented yet:** direct TWAIN/WIA scanner acquisition, automatic document-edge detection, four-corner perspective correction, manual crop handles, OCR, duplex/card-specific templates, installer, code signing and tested Windows executable. Do not treat this first foundation as a replacement for a dedicated scanner driver or as completed SmartScan.

All image processing is local. The application does not upload documents, require an account, use telemetry or contact a server.

## Requirements

- Windows 10/11, 64-bit recommended.
- Python 3.10 or newer for source execution, with Tkinter included in the standard Windows installer.
- Pillow, installed from `requirements.txt`.
- No .NET SDK is required.

## Run from source (Windows)

1. Install Python from [python.org](https://www.python.org/downloads/windows/). In the installer, enable **Add python.exe to PATH** and include **tcl/tk and IDLE**.
2. Download or clone this repository and open PowerShell in `day-01-noor-smartscan`.
3. Create an isolated environment and install the dependency:

   ```powershell
   py -3 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Launch the GUI:

   ```powershell
   python .\src\noor_smartscan_gui.py
   ```

5. Add pages, reorder them, select an enhancement and DPI, then choose **Export multi-page PDF**.

If PowerShell blocks environment activation, run `\.venv\Scripts\python.exe .\src\noor_smartscan_gui.py` after installing dependencies into the virtual environment.

## Command-line export

From the project folder:

```powershell
python .\src\noor_smartscan.py "C:\Scans\page 1.jpg" "C:\Scans\page 2.png" --output "C:\Scans\result.pdf" --dpi 300 --preset Original
```

Presets: `Original`, `Grayscale`, `Clear B&W`. Inputs are exported in the supplied order. The supported image types are JPEG, PNG, TIFF, BMP and WebP.

## Tests

Core tests use Python's built-in `unittest` and Pillow. From the project folder:

```powershell
python -m unittest discover -s tests -v
```

The core tests can run on Linux/macOS as well. The Tk GUI and Windows-specific workflow have not yet been executed in this Linux environment.

## Build status and limitations

- The image-to-PDF core and test suite are platform-neutral.
- This sandbox has Python 3.12 and Pillow, but no Tkinter package, Windows host, scanner or printer. GUI launch, Windows packaging, Arabic text rendering in Windows controls, and scanner/printer compatibility remain unverified.
- The PDF pages preserve each input image's pixel aspect ratio and use that size at the selected DPI; this version does not impose A4 layout or claim physical card dimensions.
- Enhancement preview refreshes when a page is selected; use the preset before exporting. Clear B&W uses a fixed threshold and may lose faint details.
- Large image batches may consume substantial memory because pages are prepared before export.
- Do not use this app to forge or alter identity documents. It performs local image preparation only.

## Roadmap

See the central [30-day roadmap](https://github.com/collodev21/NOOR-OPEN-SOURCE-FACTORY/blob/main/ROADMAP.md). Planned next steps include stable in-memory rotation edits, page crop/perspective correction, explicit paper-size layouts, test-print calibration and scanner acquisition.

## Contributing

Bug reports and focused pull requests are welcome. Include steps to reproduce and sample documents that contain no real customer personal data. Run the unit tests before submitting changes.

## Security and privacy

See [SECURITY.md](SECURITY.md). Never report real customer identity documents in an issue; use synthetic or fully redacted test files.

## License

MIT; see [LICENSE](LICENSE).
