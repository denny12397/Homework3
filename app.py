import re
import sqlite3
import requests
from tkinter import Tk, Label, Entry, Button, scrolledtext, messagebox, N, S, E, W

DATABASE_NAME = "contacts.db"

def setup_database():
    """建立 SQLite 資料表"""
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            iid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    connection.commit()
    connection.close()

def save_to_database(contacts):
    """將聯絡資訊存入資料庫"""
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
    for contact in contacts:
        try:
            cursor.execute("""
                INSERT INTO contacts (name, title, email)
                VALUES (?, ?, ?)
            """, (contact['name'], contact['title'], contact['email']))
        except sqlite3.IntegrityError as error:
            messagebox.showerror("異常警報",f"有一個異常警報 ： {error}")

    connection.commit()
    connection.close()

def scrape_contacts(url):
    """
    爬取聯絡資訊
    :param url: 目標網頁的 URL
    :return: 聯絡資訊列表
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        messagebox.showerror("錯誤警報", f"無法連接到網頁：{e}")
        return []

    html_content = response.text

    # 調整的正則表達式，匹配 HTML 結構
    pattern = re.compile(
        r'<div class="member_name">.*?<a[^>]*>(?P<name>.*?)</a>.*?'
        r'<div class="member_info_content">(?P<title>.*?)</div>.*?'
        r'<a href="mailto:[^"]*">(?P<email>[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})</a>',
        re.DOTALL
    )
    matches = pattern.findall(html_content)

    contacts = []
    for match in matches:
        name, title, email = match
        contacts.append({
            'name': name.strip(),
            'title': title.strip(),
            'email': email.strip()
        })
    return contacts

def display_contacts(contacts):
    """在 Tkinter 界面中顯示聯絡資訊"""
    global scrolled_text
    scrolled_text.delete("1.0", "end")
    scrolled_text.insert("end",f"{'姓名':{chr(12288)}<10}{'職稱':{chr(12288)}<20}{'E-mail':{chr(12288)}<80}\n")
    scrolled_text.insert("end", "-" * 100 + "\n")
    if contacts:
        for contact in contacts:
            scrolled_text.insert("end", f"{contact['name']:{chr(12288)}<10}")
            scrolled_text.insert("end", f"{contact['title']:{chr(12288)}<20}")
            scrolled_text.insert("end", f"{contact['email']:{chr(12288)}<80}\n")
    else:
        scrolled_text.insert("end", "未抓取到任何聯絡資訊。\n")

def main():
    """主函式"""
    global scrolled_text

    setup_database()

    root = Tk()
    root.title("聯絡資訊爬蟲")
    root.geometry("640x480")
    root.columnconfigure(1, weight=1)
    root.rowconfigure(1, weight=1)

    Label(root, text="URL:").grid(row=0, column=0, padx=5, pady=5, sticky=E)
    url_entry = Entry(root, width=50)
    url_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(E, W))
    url_entry.insert(0, "https://csie.ncut.edu.tw/content.php?key=86OP82WJQO")

    def fetch_data():
        url = url_entry.get()
        contacts = scrape_contacts(url)
        if contacts:
            save_to_database(contacts)
            display_contacts(contacts)

    Button(root, text="抓取聯絡資訊", command=fetch_data).grid(row=0, column=2, padx=5, pady=5)
    scrolled_text = scrolledtext.ScrolledText(root, wrap="word", width=70, height=20)
    scrolled_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=(N, S, E, W))
    root.mainloop()

if __name__ == "__main__":
    main()
