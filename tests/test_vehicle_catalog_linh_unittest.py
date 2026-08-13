import json
import tempfile
import unittest
from pathlib import Path

from pages.category_page import CategoryPage
from services.catalog_import import CatalogImportError, import_catalog_file


class VehicleCatalogLinhTests(unittest.TestCase):
    def test_01_catalog_url(self):
        self.assertTrue(CategoryPage.URL.endswith('/cars/catalog'))

    def test_02_brand_locators_exist(self):
        self.assertGreaterEqual(len(CategoryPage.BRAND_LOCATORS), 4)
        self.assertIn('Bảng danh sách hãng xe', CategoryPage.BRAND_LOCATORS)

    def test_03_model_locators_exist(self):
        self.assertGreaterEqual(len(CategoryPage.MODEL_LOCATORS), 6)
        self.assertIn('Dropdown chọn hãng (modal)', CategoryPage.MODEL_LOCATORS)

    def test_04_csv_import_brand_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.csv'
            path.write_text(
                'loai,ten,hang,trang_thai\n'
                'hang,VinFast,,Đang hoạt động\n'
                'mau,VF3,VinFast,Đang hoạt động\n',
                encoding='utf-8'
            )
            rows, warnings = import_catalog_file(path)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[1]['hang'], 'VinFast')
            self.assertEqual(warnings, [])

    def test_05_json_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.json'
            path.write_text(json.dumps([
                {'loai': 'Hãng xe', 'ten': 'Toyota'},
                {'loai': 'Mẫu xe', 'ten': 'Vios', 'hang': 'Toyota'},
            ], ensure_ascii=False), encoding='utf-8')
            rows, _ = import_catalog_file(path)
            self.assertEqual(rows[0]['loai'], 'hang')
            self.assertEqual(rows[1]['loai'], 'mau')

    def test_06_model_without_brand_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.csv'
            path.write_text('loai,ten,hang\nmau,VF8,\n', encoding='utf-8')
            rows, warnings = import_catalog_file(path)
            self.assertEqual(len(rows), 1)
            self.assertTrue(warnings)

    def test_07_invalid_type_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'data.csv'
            path.write_text('loai,ten,hang\nabc,Test,\n', encoding='utf-8')
            with self.assertRaises(CatalogImportError):
                import_catalog_file(path)

    def test_08_locator_avoids_dynamic_ant_id(self):
        locator_text = ' '.join(
            value for _kind, value in
            list(CategoryPage.BRAND_LOCATORS.values()) + list(CategoryPage.MODEL_LOCATORS.values())
        )
        self.assertNotIn('_r_', locator_text)


if __name__ == '__main__':
    unittest.main()
