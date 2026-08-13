from database.database import get_connection


def seed():

    connection = get_connection()
    cursor = connection.cursor()

    # =====================================================
    # WEBSITE PCM
    # =====================================================

    cursor.execute("""
        SELECT id
        FROM websites
        WHERE name = ?
    """, ("PCM",))

    website = cursor.fetchone()

    if website:

        website_id = website["id"]

    else:

        cursor.execute("""
            INSERT INTO websites (
                name,
                url
            )
            VALUES (?, ?)
        """, (
            "PCM",
            "https://courses.plt.pro.vn/"
        ))

        website_id = cursor.lastrowid

    # =====================================================
    # PCM PAGES
    # =====================================================

    pages = [
        (
            "Dashboard",
            "/dashboard"
        ),
        (
            "Bookings",
            "/bookings"
        ),
        (
            "Quản lý xe",
            "/cars"
        ),
        (
            "Danh mục xe",
            "/cars/catalog"
        ),
        (
            "Tài chính",
            "/finance"
        ),
        (
            "Người dùng",
            "/users"
        ),
    ]

    for name, path in pages:

        cursor.execute("""
            SELECT id
            FROM pages
            WHERE website_id = ?
              AND path = ?
        """, (
            website_id,
            path
        ))

        exists = cursor.fetchone()

        if not exists:

            cursor.execute("""
                INSERT INTO pages (
                    website_id,
                    name,
                    path
                )
                VALUES (?, ?, ?)
            """, (
                website_id,
                name,
                path
            ))

    connection.commit()
    connection.close()

    print("PCM seed data created successfully!")


if __name__ == "__main__":
    seed()