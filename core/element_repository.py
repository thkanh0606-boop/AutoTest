import os
import sqlite3
from core.config import Config


class ElementRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(Config.BASE_DIR, "autotest.sqlite3")
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pages_def (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url_route TEXT NOT NULL,
                    profile TEXT DEFAULT 'ADMIN'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS elements_def (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    page_id INTEGER NOT NULL,
                    element_key TEXT NOT NULL,
                    element_name TEXT NOT NULL,
                    module_name TEXT NOT NULL,
                    locator_type TEXT NOT NULL,
                    locator_value TEXT NOT NULL,
                    fallback_type TEXT,
                    fallback_value TEXT,
                    actual_result TEXT,
                    FOREIGN KEY(page_id) REFERENCES pages_def(id)
                )
            """)
            
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pages_def")
            if cursor.fetchone()[0] == 0:
                # Seed 5 Domain chuẩn (Đã bỏ Tài chính)
                domains = [
                    ("Trang tổng quan", "https://courses.plt.pro.vn/dashboard", "ADMIN"),
                    ("Đặt xe", "https://courses.plt.pro.vn/bookings", "ADMIN"),
                    ("Xe", "https://courses.plt.pro.vn/cars", "ADMIN"),
                    ("Danh mục xe", "https://courses.plt.pro.vn/cars/catalog", "ADMIN"),
                    ("Người dùng", "https://courses.plt.pro.vn/users", "ADMIN"),
                ]
                for name, url, prof in domains:
                    conn.execute("INSERT INTO pages_def (name, url_route, profile) VALUES (?, ?, ?)", (name, url, prof))

                # Seed sample elements cho Dashboard
                sample_elements = [
                    (1, "btn_lang", "Dropdown ngôn ngữ", "Dropdown List", "css", ".ant-select", "xpath", "//div[@class='ant-select']", ""),
                    (1, "lbl_title", "Tiêu đề Dashboard", "Tiêu đề", "xpath", "//h1[contains(text(),'Dashboard')]", "css", "h1.title", ""),
                    (1, "tbl_summary", "Bảng thống kê", "Table", "css", "table.summary-table", "xpath", "//table", ""),
                    (1, "menu_booking", "Menu Đặt xe", "Menu website", "xpath", "//a[@href='/bookings']", "css", "a.menu-booking", ""),
                ]
                for p_id, key, name, mod, loc_t, loc_v, fb_t, fb_v, act in sample_elements:
                    conn.execute("""
                        INSERT INTO elements_def 
                        (page_id, element_key, element_name, module_name, locator_type, locator_value, fallback_type, fallback_value, actual_result)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (p_id, key, name, mod, loc_t, loc_v, fb_t, fb_v, act))

    def list_pages(self):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT p.*, COUNT(e.id) as element_count 
                FROM pages_def p 
                LEFT JOIN elements_def e ON p.id = e.page_id 
                GROUP BY p.id
            """).fetchall()
            return [dict(r) for r in rows]

    def list_elements_by_page(self, page_id, module_filter=None):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            if module_filter and module_filter != "Tất cả Module":
                rows = conn.execute(
                    "SELECT * FROM elements_def WHERE page_id = ? AND module_name = ?", 
                    (page_id, module_filter)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM elements_def WHERE page_id = ?", (page_id,)).fetchall()
            return [dict(r) for r in rows]

    def update_element_actual(self, element_id, actual_text):
        with self.connect() as conn:
            conn.execute("UPDATE elements_def SET actual_result = ? WHERE id = ?", (actual_text, element_id))

    def reset_actual_results(self, page_id):
        with self.connect() as conn:
            conn.execute("UPDATE elements_def SET actual_result = '' WHERE page_id = ?", (page_id,))