
import json
import os
import sqlite3


class CartDAO:
    def _init_(self, db_path='carts.db'):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Initialize the database and create tables if they do not exist."""
        if not os.path.exists(self.db_path):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE carts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        contents TEXT NOT NULL DEFAULT '[]',
                        cost REAL NOT NULL DEFAULT 0
                    )
                ''')
                conn.commit()

    def _connect(self):
        """Establish and return a database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def get_cart(self, username: str) -> dict:
        """Retrieve the cart for a given username."""
        with self._connect() as conn:
            cursor = conn.execute('SELECT contents, cost FROM carts WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return {"contents": json.loads(row['contents']), "cost": row['cost']}
            return {"contents": [], "cost": 0}

    def add_to_cart(self, username: str, product_id: int):
        """Add a product to the user's cart."""
        with self._connect() as conn:
            cursor = conn.execute('SELECT contents FROM carts WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                contents = json.loads(row['contents'])
                contents.append(product_id)
                conn.execute('UPDATE carts SET contents = ? WHERE username = ?',
                             (json.dumps(contents), username))
            else:
                conn.execute('INSERT INTO carts (username, contents, cost) VALUES (?, ?, ?)',
                             (username, json.dumps([product_id]), 0))
            conn.commit()

    def remove_from_cart(self, username: str, product_id: int):
        """Remove a product from the user's cart."""
        with self._connect() as conn:
            cursor = conn.execute('SELECT contents FROM carts WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                contents = json.loads(row['contents'])
                if product_id in contents:
                    contents.remove(product_id)
                    conn.execute('UPDATE carts SET contents = ? WHERE username = ?',
                                 (json.dumps(contents), username))
                    conn.commit()

    def delete_cart(self, username: str):
        """Delete the user's cart."""
        with self._connect() as conn:
            conn.execute('DELETE FROM carts WHERE username = ?', (username,))
            conn.commit()