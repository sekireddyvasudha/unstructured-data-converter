import unittest
import os
import shutil
import tempfile
from src.converter import UnstructuredConverter
from src.converter.text_parser import TextParser
from src.converter.html_parser import HTMLParser
from src.converter.exporter import Exporter, TableData

class TestUnstructuredConverter(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.sample_txt = os.path.join(self.tmp_dir, "test.txt")
        with open(self.sample_txt, "w", encoding="utf-8") as f:
            f.write("# Heading 1\nThis is a sample test paragraph.\n\n## Subheading\nSome content here.")

        self.sample_html = os.path.join(self.tmp_dir, "test.html")
        with open(self.sample_html, "w", encoding="utf-8") as f:
            f.write("<html><head><title>Test Doc</title></head><body><h1>Title Header</h1><p>Body text.</p></body></html>")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_text_parser(self):
        parser = TextParser()
        doc = parser.parse(self.sample_txt)
        self.assertEqual(doc.metadata.file_type, "TXT")
        self.assertGreater(doc.metadata.word_count, 0)
        self.assertTrue(len(doc.sections) >= 1)

    def test_html_parser(self):
        parser = HTMLParser()
        doc = parser.parse(self.sample_html)
        self.assertEqual(doc.title, "Test Doc")
        self.assertEqual(doc.metadata.file_type, "HTML")

    def test_exporter_markdown_and_json(self):
        converter = UnstructuredConverter()
        output_dir = os.path.join(self.tmp_dir, "out")
        md_path, json_path, doc = converter.convert_file(self.sample_txt, output_dir)

        self.assertTrue(os.path.exists(md_path))
        self.assertTrue(os.path.exists(json_path))

        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
            self.assertIn("# Test", md_content)

    def test_table_render(self):
        t = TableData(headers=["Col A", "Col B"], rows=[["Val 1", "Val 2"]])
        md_table = Exporter.render_table_to_markdown(t)
        self.assertIn("| Col A | Col B |", md_table)
        self.assertIn("| Val 1 | Val 2 |", md_table)

if __name__ == "__main__":
    unittest.main()
