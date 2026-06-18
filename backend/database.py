"""SQLite 数据库初始化与连接管理。"""

import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "hiking.db"


def get_connection() -> sqlite3.Connection:
    """获取 SQLite 连接，行以字典形式返回。"""
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """创建表结构并写入种子数据（仅在空库时）。"""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                difficulty TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                marker_type TEXT NOT NULL CHECK (marker_type IN ('水源', '休息')),
                coordinates TEXT NOT NULL,
                notes TEXT DEFAULT '',
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM routes").fetchone()[0]
        if count == 0:
            _seed_data(conn)
        conn.commit()
    finally:
        conn.close()


def _seed_data(conn: sqlite3.Connection) -> None:
    """写入 2 条路线、各 3 个标记点。"""
    routes = [
        ("雨崩冰湖线", "困难"),
        ("格聂C线", "极难"),
    ]
    for name, difficulty in routes:
        cur = conn.execute(
            "INSERT INTO routes (name, difficulty) VALUES (?, ?)",
            (name, difficulty),
        )
        route_id = cur.lastrowid
        markers = [
            ("水源", "N28.4123 E98.7891", "溪流清澈，可直饮"),
            ("休息", "N28.4156 E98.7920", "平坦草地，可扎营"),
            ("水源", "N28.4189 E98.7955", "山涧泉水，需煮沸"),
        ]
        if route_id == 2:
            markers = [
                ("水源", "N29.8234 E99.1234", "冰川融水，夏季充沛"),
                ("休息", "N29.8267 E99.1267", "避风石滩"),
                ("水源", "N29.8301 E99.1302", "季节性水源，旱季干涸"),
            ]
        conn.executemany(
            "INSERT INTO markers (route_id, marker_type, coordinates, notes) VALUES (?, ?, ?, ?)",
            [(route_id, t, c, n) for t, c, n in markers],
        )
