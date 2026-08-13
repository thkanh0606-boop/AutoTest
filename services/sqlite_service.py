import sqlite3

from database.database import DATABASE_PATH


class SQLiteService:

    # =====================================================
    # CONNECTION
    # =====================================================

    def get_connection(self):
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row

        # Bật foreign key cho SQLite
        connection.execute("PRAGMA foreign_keys = ON")

        return connection

    # =====================================================
    # WEBSITE
    # =====================================================

    def get_websites(self):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    name,
                    url
                FROM websites
                ORDER BY id ASC
                """
            )

            return cursor.fetchall()

        finally:
            connection.close()

    # =====================================================
    # GET WEBSITE
    # =====================================================

    def get_website(self, website_id):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    name,
                    url
                FROM websites
                WHERE id = ?
                """,
                (website_id,)
            )

            return cursor.fetchone()

        finally:
            connection.close()

    # =====================================================
    # ADD WEBSITE
    # =====================================================

    def add_website(self, name, url):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO websites (
                    name,
                    url
                )
                VALUES (?, ?)
                """,
                (
                    name.strip(),
                    url.strip()
                )
            )

            connection.commit()

            return cursor.lastrowid

        finally:
            connection.close()

    # =====================================================
    # UPDATE WEBSITE
    # =====================================================

    def update_website(self, website_id, name, url):
        connection = self.get_connection()

        try:
            connection.execute(
                """
                UPDATE websites
                SET
                    name = ?,
                    url = ?
                WHERE id = ?
                """,
                (
                    name.strip(),
                    url.strip(),
                    website_id
                )
            )

            connection.commit()

        finally:
            connection.close()

    # =====================================================
    # DELETE WEBSITE
    # =====================================================

    def delete_website(self, website_id):
        connection = self.get_connection()

        try:
            connection.execute(
                """
                DELETE FROM websites
                WHERE id = ?
                """,
                (website_id,)
            )

            connection.commit()

        finally:
            connection.close()

    # =====================================================
    # PAGES
    # =====================================================

    def get_pages(self, website_id):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    website_id,
                    name,
                    path
                FROM pages
                WHERE website_id = ?
                ORDER BY id ASC
                """,
                (website_id,)
            )

            return cursor.fetchall()

        finally:
            connection.close()

    # =====================================================
    # GET PAGE
    # =====================================================

    def get_page(self, page_id):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                SELECT
                    id,
                    website_id,
                    name,
                    path
                FROM pages
                WHERE id = ?
                """,
                (page_id,)
            )

            return cursor.fetchone()

        finally:
            connection.close()

    # =====================================================
    # ADD PAGE
    # =====================================================

    def add_page(self, website_id, name, path):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO pages (
                    website_id,
                    name,
                    path
                )
                VALUES (?, ?, ?)
                """,
                (
                    website_id,
                    name.strip(),
                    path.strip()
                )
            )

            connection.commit()

            return cursor.lastrowid

        finally:
            connection.close()

    # =====================================================
    # UPDATE PAGE
    # =====================================================

    def update_page(self, page_id, name, path):
        connection = self.get_connection()

        try:
            connection.execute(
                """
                UPDATE pages
                SET
                    name = ?,
                    path = ?
                WHERE id = ?
                """,
                (
                    name.strip(),
                    path.strip(),
                    page_id
                )
            )

            connection.commit()

        finally:
            connection.close()

    # =====================================================
    # DELETE PAGE
    # =====================================================

    def delete_page(self, page_id):
        connection = self.get_connection()

        try:
            connection.execute(
                """
                DELETE FROM pages
                WHERE id = ?
                """,
                (page_id,)
            )

            connection.commit()

        finally:
            connection.close()

    # =====================================================
    # COUNT PAGES
    # =====================================================

    def count_pages(self, website_id=None):
        connection = self.get_connection()

        try:
            if website_id is None:
                cursor = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM pages
                    """
                )
            else:
                cursor = connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM pages
                    WHERE website_id = ?
                    """,
                    (website_id,)
                )

            return cursor.fetchone()[0]

        finally:
            connection.close()

    # =====================================================
    # COUNT WEBSITES
    # =====================================================

    def count_websites(self):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                SELECT COUNT(*)
                FROM websites
                """
            )

            return cursor.fetchone()[0]

        finally:
            connection.close()

    # =====================================================
    # GET ALL PAGE COUNT BY WEBSITE
    # =====================================================

    def get_page_count_by_website(self):
        connection = self.get_connection()

        try:
            cursor = connection.execute(
                """
                SELECT
                    websites.id,
                    websites.name,
                    COUNT(pages.id) AS page_count
                FROM websites
                LEFT JOIN pages
                    ON pages.website_id = websites.id
                GROUP BY
                    websites.id,
                    websites.name
                ORDER BY websites.id ASC
                """
            )

            return cursor.fetchall()

        finally:
            connection.close()

    # =====================================================
    # GET DASHBOARD SUMMARY
    # =====================================================

    def get_dashboard_summary(self):
        connection = self.get_connection()

        try:
            websites = connection.execute(
                """
                SELECT COUNT(*)
                FROM websites
                """
            ).fetchone()[0]

            pages = connection.execute(
                """
                SELECT COUNT(*)
                FROM pages
                """
            ).fetchone()[0]

            return {
                "websites": websites,
                "pages": pages,
                "test_cases": 0,
                "elements": 0,
            }

        finally:
            connection.close()