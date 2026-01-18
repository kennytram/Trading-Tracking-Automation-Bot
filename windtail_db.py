import sqlite3

DB_PATH = "market.db"

items = [
    ("Ginkgo", 25, "ginkgo"),
    ("Porcelain Vase", 36, "vase"),
    ("Rice", 30, "rice"),
    ("Grapes", 60, "grapes"),
    ("Watershield", 20, "watershield"),
    ("Charcoal", 35, "charcoal"),
    ("Huai Salt", 45, "salt"),
    ("Round Fan", 30, "fan"),
    ("Storax", 70, "storax"),
    ("Xinyang Tea", 85, "tea"),
    ("Antiques", 95, "antiques"),
    ("Bamboo Curtain", 35, "bamboo"),
    ("Tixi Lacquerware", 55, "tixi"),
    ("Rice Vinegar", 35, "vinegar"),
    ("Safflower", 25, "safflower"),
    ("Pork", 45, "pork"),
    ("Horseman Lantern", 45, "lantern"),
    ("Kesi Tapestry", 60, "kesi"),
    ("Ramie", 25, "ramie"),
    ("Chrysanthemum", 25, "chrys"),
    ("Jade Disc", 95, "jade"),
]

players = [
    ("Tao", "picturing", 571241431352606721, "tao"),
    ("Macroni", "macaronilizard", 571241431352606721, "macroni"),
    ("Qiuyuae", "adexi", 571241431352606721, "qiuyuae"),
    ("Nezubi", "codo", 571241431352606721, "nezubi"),
    ("Psede", "psede", 571241431352606721, "psede"),
    ("KupoNut", "kuponaut", 571241431352606721, "kuponnut"),
    ("fishball", "ruomeimei", 571241431352606721, "fishball"),
    ("Poofie", "poofiecloud", 571241431352606721, "poofie"),
    ("Sriracha", "sriracha.", 571241431352606721, "sriracha"),
    ("Burnmore", "burnmore_", 571241431352606721, "burnmore"),
    ("Navaris", "tahlari", 571241431352606721, "navaris"),
    ("Othono", "othono", 571241431352606721, "othono"),
    ("JohnnyTu", "johnnytu", 571241431352606721, "johnnytu"),
    ("Ease", "ease", 571241431352606721, "ease"),
    ("Yihan", "hereliescaine", 571241431352606721, "yihan"),
    ("Blenjou", "blenjiman", 571241431352606721, "blenjou"),
    ("Yúnyān", ".chaoticstupid", 571241431352606721, "yúnyān"),
    ("DaiSY", "daisy9746", 571241431352606721, "daisy"),
    ("Luwucian", "okamiaaron", 571241431352606721, "luwucian"),
    ("猫", "kz1926", 571241431352606721, "猫"),
    ("Fren", "orcfren", 571241431352606721, "fren"),
    ("TrueYonko", "yourwho.", 571241431352606721, "trueyonko"),
    ("riŋ", "riririnny", 571241431352606721, "riŋ"),
    ("Sora公主", "sxftsora", 571241431352606721, "sora公主"),
    ("APTDuck", "aptduck", 571241431352606721, "aptduck"),
    ("Max", "firemax1477", 571241431352606721, "max"),
    ("SleepyMin", "sleepymin", 571241431352606721, "sleepymin"),
    ("yyy", "yyy1399", 571241431352606721, "yyy"),
    ("LiaoShun", "thelaughingimp", 571241431352606721, "liaoshun"),
    ("Sloane", "pirate.hunter", 571241431352606721, "sloane"),
    ("Aekotie", "aekotie", 571241431352606721, "aekotie"),
    ("Kōrei", "codename.lambsie", 571241431352606721, "kōrei"),
    ("土豆子", "potatoduh", 571241431352606721, "土豆子"),
    ("Ayalet", "ayaletdia", 571241431352606721, "ayalet"),
    ("光亮", "guangliang99", 571241431352606721, "光亮"),
    ("BotAwp", "bot_awp", 571241431352606721, "botawp"),
    ("critter", "nospacesallowed", 571241431352606721, "critter"),
    ("Sieann", "sieann", 571241431352606721, "sieann"),
    ("Jųnō", "estherrxx", 571241431352606721, "jųnō"),
    ("Ricci", "skysugars", 571241431352606721, "ricci"),
    ("OneHandArmy", "kush0rcake", 571241431352606721, "onehandarmy"),
    ("Sixi", "emotionalshawti", 571241431352606721, "sixi"),
    ("Utella", "sinfernio", 571241431352606721, "utella"),
    ("Tess", "xox_tess", 571241431352606721, "tess"),
    ("billmadboyxd", "billmadboyxd", 571241431352606721, "billmadboyxd"),
    ("ruleofKon", "ruleofkon", 571241431352606721, "ruleofkon"),
    ("LostLights", "hopeslayer01", 571241431352606721, "lostlights"),
    ("bittersweet", "pisster", 571241431352606721, "bittersweet"),
    ("Ciela", "ciela7905", 571241431352606721, "ciela"),
    ("yippeewee", "antherism", 571241431352606721, "yippeewee"),
    ("BlazeDarkwell", "blazerdarkwell", 571241431352606721, "blazedarkwell"),
    ("Maozidong", "baxizukesifu", 571241431352606721, "maozidong"),
    ("Tingzhu", "aquasparrow", 571241431352606721, "tingzhu"),
    ("Tekno-Voltekor", "teknolight", 571241431352606721, "tekno-voltekor"),
    ("Epialos", "entrophicdrag", 571241431352606721, "epialos"),
    ("Sunnea", "sunnea", 571241431352606721, "sunnea"),
    ("卜币", "juundaa", 571241431352606721, "卜币"),
    ("Ninety-Nine", "longjawnsilva", 571241431352606721, "ninety-nine"),
    ("Rixie", "rixei", 571241431352606721, "rixie"),
    ("水滴", "tsukiuta", 571241431352606721, "水滴"),
    ("Nectar", ".nectarios", 571241431352606721, "nectar"),
    ("alclarity", "alclarity", 571241431352606721, "alclarity"),
    ("Korryle", "korryle", 571241431352606721, "korryle"),
    ("Atuaz", "cloudtaituha", 571241431352606721, "atuaz"),
    ("Kofuku", "driedmango", 571241431352606721, "kofuku"),
    ("Hieron", "dominuzi", 571241431352606721, "hieron"),
    ("Heesoo", "tsumurf", 571241431352606721, "heesoo"),
    ("votex", "v0t3x", 571241431352606721, "votex"),
    ("DerKaiser", "derkaiser1084", 571241431352606721, "derkaiser"),
    ("x艾迪x", "eddie8321", 571241431352606721, "x艾迪x"),
    ("Aodin", "aodin", 571241431352606721, "aodin"),
    ("WhereWindsMeet", "cow_one", 571241431352606721, "wherewindsmeet"),
    ("AryelleJan", "arya355", 571241431352606721, "aryellejan"),
    ("Mrktavious", "mrktavious", 571241431352606721, "mrktavious"),
    ("Yue山", "thefourthmonth", 571241431352606721, "yue山"),
    ("Beonyan", "beobeo", 571241431352606721, "beonyan"),
    ("MuwanLi", "toannguyen", 571241431352606721, "muwanli"),
    ("Yennara", "yennari", 571241431352606721, "yennara"),
    ("LordDevil", "charlesbergoglio", 571241431352606721, "lorddevil"),
    ("霉女", "mokkimok", 571241431352606721, "霉女"),
    ("XiTang", "tbexie", 571241431352606721, "xitang"),
    ("nxppp", "weenweener", 571241431352606721, "nxppp"),
    ("Ruiyin", "raigazero", 571241431352606721, "ruiyin"),
    ("JustInSane", "justin92.", 571241431352606721, "justinsane"),
    ("MitsuMamoru", "mitsu___", 571241431352606721, "mitsumamoru"),
    ("DaR", "i7ydar", 571241431352606721, "dar"),
    ("Sleepybread", "bread0705", 571241431352606721, "sleepybread"),
    ("Moondrinker", "tducd", 571241431352606721, "moondrinker"),
    ("Aulzen", "aulzen", 571241431352606721, "aulzen"),
    ("RamzGestalt", "ramza_00", 571241431352606721, "ramzgestalt"),
    ("Jirowo", "eyeamjiro", 571241431352606721, "jirowo"),
    ("阿敏", "min_.", 571241431352606721, "阿敏"),
    ("VenusFallen", "venusfallen", 571241431352606721, "venusfallen"),
    ("Jimichu", "xjimichu", 571241431352606721, "jimichu"),

    ("Tao", "picturing", 784731196117876756, "tao"),
    ("Macroni", "macaronilizard", 784731196117876756, "macroni"),
    ("Qiuyuae", "adexi", 784731196117876756, "qiuyuae"),
    ("Nezubi", "codo", 784731196117876756, "nezubi"),
    ("Psede", "psede", 784731196117876756, "psede"),
    ("KupoNut", "kuponaut", 784731196117876756, "kuponnut"),
    ("fishball", "ruomeimei", 784731196117876756, "fishball"),
    ("Poofie", "poofiecloud", 784731196117876756, "poofie"),
    ("Sriracha", "sriracha.", 784731196117876756, "sriracha"),
    ("Burnmore", "burnmore_", 784731196117876756, "burnmore"),
    ("Navaris", "tahlari", 784731196117876756, "navaris"),
    ("Othono", "othono", 784731196117876756, "othono"),
    ("JohnnyTu", "johnnytu", 784731196117876756, "johnnytu"),
    ("Ease", "ease", 784731196117876756, "ease"),
    ("Yihan", "hereliescaine", 784731196117876756, "yihan"),
    ("Blenjou", "blenjiman", 784731196117876756, "blenjou"),
    ("Yúnyān", ".chaoticstupid", 784731196117876756, "yúnyān"),
    ("DaiSY", "daisy9746", 784731196117876756, "daisy"),
    ("Luwucian", "okamiaaron", 784731196117876756, "luwucian"),
    ("猫", "kz1926", 784731196117876756, "猫"),
    ("Fren", "orcfren", 784731196117876756, "fren"),
    ("TrueYonko", "yourwho.", 784731196117876756, "trueyonko"),
    ("riŋ", "riririnny", 784731196117876756, "riŋ"),
    ("Sora公主", "sxftsora", 784731196117876756, "sora公主"),
    ("APTDuck", "aptduck", 784731196117876756, "aptduck"),
    ("Max", "firemax1477", 784731196117876756, "max"),
    ("SleepyMin", "sleepymin", 784731196117876756, "sleepymin"),
    ("yyy", "yyy1399", 784731196117876756, "yyy"),
    ("LiaoShun", "thelaughingimp", 784731196117876756, "liaoshun"),
    ("Sloane", "pirate.hunter", 784731196117876756, "sloane"),
    ("Aekotie", "aekotie", 784731196117876756, "aekotie"),
    ("Kōrei", "codename.lambsie", 784731196117876756, "kōrei"),
    ("土豆子", "potatoduh", 784731196117876756, "土豆子"),
    ("Ayalet", "ayaletdia", 784731196117876756, "ayalet"),
    ("光亮", "guangliang99", 784731196117876756, "光亮"),
    ("BotAwp", "bot_awp", 784731196117876756, "botawp"),
    ("critter", "nospacesallowed", 784731196117876756, "critter"),
    ("Sieann", "sieann", 784731196117876756, "sieann"),
    ("Jųnō", "estherrxx", 784731196117876756, "jųnō"),
    ("Ricci", "skysugars", 784731196117876756, "ricci"),
    ("OneHandArmy", "kush0rcake", 784731196117876756, "onehandarmy"),
    ("Sixi", "emotionalshawti", 784731196117876756, "sixi"),
    ("Utella", "sinfernio", 784731196117876756, "utella"),
    ("Tess", "xox_tess", 784731196117876756, "tess"),
    ("billmadboyxd", "billmadboyxd", 784731196117876756, "billmadboyxd"),
    ("ruleofKon", "ruleofkon", 784731196117876756, "ruleofkon"),
    ("LostLights", "hopeslayer01", 784731196117876756, "lostlights"),
    ("bittersweet", "pisster", 784731196117876756, "bittersweet"),
    ("Ciela", "ciela7905", 784731196117876756, "ciela"),
    ("yippeewee", "antherism", 784731196117876756, "yippeewee"),
    ("BlazeDarkwell", "blazerdarkwell", 784731196117876756, "blazedarkwell"),
    ("Maozidong", "baxizukesifu", 784731196117876756, "maozidong"),
    ("Tingzhu", "aquasparrow", 784731196117876756, "tingzhu"),
    ("Tekno-Voltekor", "teknolight", 784731196117876756, "tekno-voltekor"),
    ("Epialos", "entrophicdrag", 784731196117876756, "epialos"),
    ("Sunnea", "sunnea", 784731196117876756, "sunnea"),
    ("卜币", "juundaa", 784731196117876756, "卜币"),
    ("Ninety-Nine", "longjawnsilva", 784731196117876756, "ninety-nine"),
    ("Rixie", "rixei", 784731196117876756, "rixie"),
    ("水滴", "tsukiuta", 784731196117876756, "水滴"),
    ("Nectar", ".nectarios", 784731196117876756, "nectar"),
    ("alclarity", "alclarity", 784731196117876756, "alclarity"),
    ("Korryle", "korryle", 784731196117876756, "korryle"),
    ("Atuaz", "cloudtaituha", 784731196117876756, "atuaz"),
    ("Kofuku", "driedmango", 784731196117876756, "kofuku"),
    ("Hieron", "dominuzi", 784731196117876756, "hieron"),
    ("Heesoo", "tsumurf", 784731196117876756, "heesoo"),
    ("votex", "v0t3x", 784731196117876756, "votex"),
    ("DerKaiser", "derkaiser1084", 784731196117876756, "derkaiser"),
    ("x艾迪x", "eddie8321", 784731196117876756, "x艾迪x"),
    ("Aodin", "aodin", 784731196117876756, "aodin"),
    ("WhereWindsMeet", "cow_one", 784731196117876756, "wherewindsmeet"),
    ("AryelleJan", "arya355", 784731196117876756, "aryellejan"),
    ("Mrktavious", "mrktavious", 784731196117876756, "mrktavious"),
    ("Yue山", "thefourthmonth", 784731196117876756, "yue山"),
    ("Beonyan", "beobeo", 784731196117876756, "beonyan"),
    ("MuwanLi", "toannguyen", 784731196117876756, "muwanli"),
    ("Yennara", "yennari", 784731196117876756, "yennara"),
    ("LordDevil", "charlesbergoglio", 784731196117876756, "lorddevil"),
    ("霉女", "mokkimok", 784731196117876756, "霉女"),
    ("XiTang", "tbexie", 784731196117876756, "xitang"),
    ("nxppp", "weenweener", 784731196117876756, "nxppp"),
    ("Ruiyin", "raigazero", 784731196117876756, "ruiyin"),
    ("JustInSane", "justin92.", 784731196117876756, "justinsane"),
    ("MitsuMamoru", "mitsu___", 784731196117876756, "mitsumamoru"),
    ("DaR", "i7ydar", 784731196117876756, "dar"),
    ("Sleepybread", "bread0705", 784731196117876756, "sleepybread"),
    ("Moondrinker", "tducd", 784731196117876756, "moondrinker"),
    ("Aulzen", "aulzen", 784731196117876756, "aulzen"),
    ("RamzGestalt", "ramza_00", 784731196117876756, "ramzgestalt"),
    ("Jirowo", "eyeamjiro", 784731196117876756, "jirowo"),
    ("阿敏", "min_.", 784731196117876756, "阿敏"),
    ("VenusFallen", "venusfallen", 784731196117876756, "venusfallen"),
    ("Jimichu", "xjimichu", 784731196117876756, "jimichu"),
]

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
            UNIQUE (server_id, player_name)
        );

        CREATE TABLE IF NOT EXISTS market_meta (
            server_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS market_prices (
            item_id INTEGER,
            player_id INTEGER,
            market_item_percentage INTEGER,
            PRIMARY KEY (item_id, player_id),
            FOREIGN KEY (item_id) REFERENCES item(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES player(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_player_server
        ON player(server_id);

        CREATE INDEX IF NOT EXISTS idx_market_player
        ON market_prices(player_id);

        CREATE INDEX IF NOT EXISTS idx_market_item
        ON market_prices(item_id);


        """)
        cur.executemany(
            "INSERT OR IGNORE INTO item (display_name, base_price, name) VALUES (?, ?, ?)",
            items
        )

        cur.executemany(
            "INSERT OR IGNORE INTO player (display_player_name, discord_handle, server_id, player_name) VALUES (?, ?, ?, ?)",
            players
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

def add_player(server_id, name, discord_handle=None):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO player
               (server_id, display_player_name, player_name, discord_handle)
               VALUES (?, ?, ?, ?)""",
            (server_id, name, name, discord_handle)
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
            INSERT INTO market_prices (item_id, player_id, market_item_percentage)
            VALUES (?, ?, ?)
            ON CONFLICT(item_id, player_id)
            DO UPDATE SET market_item_percentage = excluded.market_item_percentage
            """,
            (item_id, player_id, percentage)
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
            "DELETE FROM market_prices WHERE item_id = ? AND player_id = ?",
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
            WHERE server_id = ?
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
                market_prices.market_item_percentage AS percentage,
                player.display_player_name AS player,
                player.player_name AS player_name_id,
                player.discord_handle AS discord
            FROM market_prices
            JOIN item ON item.id = market_prices.item_id
            JOIN player ON player.id = market_prices.player_id
            WHERE player.server_id = ?
            ORDER BY market_prices.market_item_percentage DESC,
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
        conn.execute("DELETE FROM market_prices;")
        conn.commit()