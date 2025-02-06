def save_to_db(conn, cursor, name, href, expires, description=None, requirements=None):
    """
    Save vacancy data to the database.
    Args:
        conn: SQLite connection object.
        cursor: SQLite cursor object.
        name: Vacancy name.
        href: Vacancy URL.
        expires: Expiration date of the vacancy.
        description: Full description of the vacancy.
        requirements: Specific requirements extracted from the description.
    """
    try:
        # Check if the vacancy already exists in the database
        cursor.execute(
            "SELECT * FROM vacancies WHERE name = ? AND url = ? AND expires = ?",
            (name, href, expires),
        )
        if cursor.fetchone() is None:
            # Insert the vacancy into the database
            cursor.execute(
                """
                INSERT INTO vacancies (name, url, expires, description, requirements)
                VALUES (?, ?, ?, ?, ?)
            """,
                (name, href, expires, description, requirements),
            )
            conn.commit()
            print(f"Saved: {name}, {href}, {expires}")
        else:
            print(f"Already exists in DB: {name}")
    except Exception as e:
        print(f"Error saving to database: {e}")
