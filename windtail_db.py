import sqlite3
import os

DB_PATH = "market.db"

items = []
players = []

# ======================
# ERROR CLASSES
# ======================
class PlayerNotFound(Exception):
    pass

class ItemNotFound(Exception):
    pass


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            display_name TEXT,
            image_url TEXT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            base_price INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER,
            server_id INTEGER NOT NULL,
            display_player_name TEXT,
            player_name TEXT NOT NULL COLLATE NOCASE,
            discord_handle TEXT COLLATE NOCASE,
            is_time_limited INTEGER,
            UNIQUE (server_id, player_name)
        );

        CREATE TABLE IF NOT EXISTS market_meta (
            server_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS market_price (
            item_id INTEGER,
            player_id INTEGER,
            market_item_percentage INTEGER,
            PRIMARY KEY (item_id, player_id),
            FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE
        );
                           
        CREATE TABLE IF NOT EXISTS rate_limit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            count INTEGER DEFAULT 0,
            last_reset TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_player_server
        ON player(server_id);

        CREATE INDEX IF NOT EXISTS idx_market_player
        ON market_price(player_id);

        CREATE INDEX IF NOT EXISTS idx_market_item
        ON market_price(item_id);


        """)
        cur.executemany(
            "INSERT OR IGNORE INTO item (display_name, base_price, name) VALUES (?, ?, ?)",
            items
        )

        cur.executemany(
            "INSERT OR IGNORE INTO player (display_player_name, discord_handle, server_id, player_name, is_time_limited) VALUES (?, ?, ?, ?, 0)",
            players
        )

        cur.execute(
            "INSERT OR IGNORE INTO rate_limit (name, count, last_reset) VALUES ('google_vision', 0, CURRENT_TIMESTAMP)"
        )   

        conn.commit()


def get_item_id(name):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM item WHERE name = ? COLLATE NOCASE OR display_name = ? COLLATE NOCASE",
            (name.lower(), name.lower())
        ).fetchone()
        return row["id"] if row else None


def get_player_id(server_id, name):
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id FROM player
               WHERE server_id = ?
               AND player_name = ? COLLATE NOCASE""",
            (server_id, name.lower())
        ).fetchone()
        return row["id"] if row else None
    
def fetch_player_by_discord(server_id, discord):
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id FROM player
               WHERE server_id = ?
               AND discord_handle = ? COLLATE NOCASE""",
            (server_id, discord.lower())
        ).fetchone()
        return row["id"] if row else None
    
def get_rate_limit(name):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM rate_limit WHERE name = ?",
            (name,)
        ).fetchone()
        return row

def add_player(server_id, name, discord_handle=None):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO player
               (server_id, display_player_name, player_name, discord_handle, is_time_limited)
               VALUES (?, ?, ?, ?, 0)""",
            (server_id, name, name, discord_handle)
        )
        conn.commit()

def add_many_scanned_players(server_id, names):
    with get_conn() as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO player
               (server_id, display_player_name, player_name, discord_handle, is_time_limited)
               VALUES (?, ?, ?, ?, 1)""",
            [(server_id, name, name, None) for name in names]
        )
        conn.commit()

def delete_player(server_id, name):
    player_id = get_player_id(server_id, name.lower())
    if not player_id:
        raise PlayerNotFound(name)

    with get_conn() as conn:
        conn.execute(
            "DELETE FROM player WHERE id = ?",
            (player_id,)
        )
        conn.commit()

def upsert_price(server_id, item_name, player_name, percentage):
    item_id = get_item_id(item_name)
    if not item_id:
        raise ItemNotFound(item_name)

    player_id = get_player_id(server_id, player_name.lower())
    if not player_id:
        raise PlayerNotFound(player_name)

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO market_price (item_id, player_id, market_item_percentage)
            VALUES (?, ?, ?)
            ON CONFLICT(item_id, player_id)
            DO UPDATE SET market_item_percentage = excluded.market_item_percentage
            """,
            (item_id, player_id, percentage)
        )
        conn.commit()

def upsert_many_prices(server_id, item_name, player_names, percentages, min_percentage=150):
    if len(player_names) != len(percentages):
        raise ValueError("player_names and percentages must have the same length")

    item_id = get_item_id(item_name)
    if not item_id:
        raise ItemNotFound(item_name)

    # Filter by min_percentage
    filtered = [
        (name, pct) for name, pct in zip(player_names, percentages)
        if min_percentage is None or pct >= min_percentage
    ]

    if not filtered:
        return

    rows = []
    for name, pct in filtered:
        pid = get_player_id(server_id, name.lower())
        if not pid:
            continue
        rows.append((item_id, pid, pct))

    with get_conn() as conn:
        conn.executemany(
            """
            INSERT INTO market_price (item_id, player_id, market_item_percentage)
            VALUES (?, ?, ?)
            ON CONFLICT(item_id, player_id)
            DO UPDATE SET market_item_percentage = excluded.market_item_percentage
            """,
            rows
        )
        conn.commit()

def increment_rate_limit(name):
    with get_conn() as conn:
        conn.execute(
            """
            UPDATE rate_limit
            SET count = count + 1,
                last_reset = CURRENT_TIMESTAMP
            WHERE name = ?
            """,
            (name,)
        )
        conn.commit()
def delete_price(server_id, item_name, player_name):
    item_id = get_item_id(item_name)
    player_id = get_player_id(server_id, player_name.lower())
    if not item_id:
        raise ItemNotFound(item_name)
    if not player_id:
        raise PlayerNotFound(player_name)

    with get_conn() as conn:
        conn.execute(
            "DELETE FROM market_price WHERE item_id = ? AND player_id = ?",
            (item_id, player_id)
        )
        conn.commit()

def fetch_items():
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT
                display_name AS item,
                name AS item_keyword,
                base_price AS item_price
            FROM item
            ORDER BY LOWER(display_name) ASC
        """)
        return cur.fetchall()

def fetch_players(server_id):
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT
                display_player_name AS display_player_name,
                player_name AS player_name,
                discord_handle AS discord
            FROM player
            WHERE server_id = ? AND is_time_limited = 0
            ORDER BY LOWER(display_player_name) ASC
        """, (server_id,))
        return cur.fetchall()

def fetch_prices(server_id):
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT
                item.display_name AS item,
                item.name AS item_keyword,
                item.base_price AS price,
                market_price.market_item_percentage AS percentage,
                player.display_player_name AS player,
                player.player_name AS player_name_id,
                player.discord_handle AS discord
            FROM market_price
            JOIN item ON item.id = market_price.item_id
            JOIN player ON player.id = market_price.player_id
            WHERE player.server_id = ?
            ORDER BY market_price.market_item_percentage DESC,
                    item.name COLLATE NOCASE;
        """, (server_id,))
        return cur.fetchall()

# def get_guild_meta(server_id):
#     with get_conn() as conn:
#         return conn.execute(
#             "SELECT * FROM guild_meta WHERE server_id = ?",
#             (server_id,)
#         ).fetchone()


# def set_guild_meta(server_id, thread_id, message_id):
#     with get_conn() as conn:
#         conn.execute(
#             """
#             INSERT INTO guild_meta (server_id, thread_id, message_id)
#             VALUES (?, ?, ?)
#             ON CONFLICT(server_id)
#             DO UPDATE SET thread_id = excluded.thread_id,
#                           message_id = excluded.message_id
#             """,
#             (server_id, thread_id, message_id)
#         )
#         conn.commit()

def set_market_meta(server_id, channel_id, message_id):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO market_meta (
            server_id,
            channel_id,
            message_id
        )
        VALUES (?, ?, ?)
        ON CONFLICT(server_id)
        DO UPDATE SET
            channel_id = excluded.channel_id,
            message_id = excluded.message_id
        """, (
            server_id,
            channel_id,
            message_id
        ))

def get_market_meta(server_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM market_meta WHERE server_id = ?",
            (server_id,)
        ).fetchone()

def reset_market_prices():
    with get_conn() as conn:
        conn.execute("DELETE FROM market_price;")
        conn.execute("DELETE FROM player WHERE is_time_limited = 1;")
        conn.commit()

def reset_google_rate_limits():
    with get_conn() as conn:
        conn.execute("""
        UPDATE rate_limit
        SET 
            count = 0,
            last_reset = CURRENT_TIMESTAMP
        WHERE name = 'google_vision;
        """)
        conn.commit()