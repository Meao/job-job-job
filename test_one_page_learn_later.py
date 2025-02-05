

def open_page(webBrowser, url):
    webBrowser.get(url)




def test_cv_ee_pagination(webBrowser):
    open_page(webBrowser, URL)
    try:
        conn = sqlite3.connect('cv_ee.db')
        cursor = conn.cursor()
        total_results = get_total_results(webBrowser)
        if total_results:
            handle_pagination(conn, cursor, webBrowser)
        conn.close()
        print("Saved to DB")
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")