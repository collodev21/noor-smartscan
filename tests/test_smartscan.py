import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from noor_smartscan import enhance_page, export_pdf, open_page


class SmartScanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="noor-épreuve- العربية-")
        self.folder = Path(self.temp.name)
        self.first = self.folder / "صفحة ١.png"
        self.second = self.folder / "page-02.jpg"
        Image.new("RGB", (120, 80), (240, 40, 40)).save(self.first)
        Image.new("RGB", (70, 100), (40, 200, 40)).save(self.second)

    def tearDown(self):
        self.temp.cleanup()

    def test_unicode_path_and_image_dimensions(self):
        image = open_page(self.first)
        self.assertEqual(image.size, (120, 80))
        self.assertEqual(image.mode, "RGB")

    def test_enhancement_presets_return_rgb(self):
        original = open_page(self.first)
        for preset in ("Original", "Grayscale", "Clear B&W"):
            result = enhance_page(original, preset)
            self.assertEqual(result.mode, "RGB")
            self.assertEqual(result.size, original.size)
        with self.assertRaises(ValueError):
            enhance_page(original, "invented")

    def test_pdf_export_page_count_and_order(self):
        output = self.folder / "résultat.pdf"
        export_pdf([self.first, self.second], output, dpi=150)
        self.assertTrue(output.is_file())
        reader = PdfReader(str(output))
        self.assertEqual(len(reader.pages), 2)
        first = reader.pages[0].mediabox
        second = reader.pages[1].mediabox
        self.assertAlmostEqual(float(first.width), 120 * 72 / 150, places=2)
        self.assertAlmostEqual(float(first.height), 80 * 72 / 150, places=2)
        self.assertAlmostEqual(float(second.width), 70 * 72 / 150, places=2)
        self.assertAlmostEqual(float(second.height), 100 * 72 / 150, places=2)

    def test_validation_and_no_overwrite(self):
        output = self.folder / "out.pdf"
        with self.assertRaises(ValueError):
            export_pdf([], output)
        with self.assertRaises(ValueError):
            export_pdf([self.first], output, dpi=10)
        with self.assertRaises(ValueError):
            export_pdf([self.first], self.first)
        with self.assertRaises(ValueError):
            export_pdf([self.first], self.folder / "out.txt")
        with self.assertRaises(ValueError):
            open_page(self.folder / "missing.xyz")

    def test_corrupt_input_fails_without_partial_pdf(self):
        bad = self.folder / "broken.png"
        bad.write_text("not an image", encoding="utf-8")
        output = self.folder / "broken-output.pdf"
        with self.assertRaises(ValueError):
            export_pdf([self.first, bad], output)
        self.assertFalse(output.exists())
        self.assertFalse((self.folder / "broken-output.tmp.pdf").exists())


if __name__ == "__main__":
    unittest.main()
