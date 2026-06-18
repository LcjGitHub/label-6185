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
    """创建表结构、升级旧库、写入种子数据。"""
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                region TEXT NOT NULL,
                mileage REAL DEFAULT 0,
                days REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                marker_type TEXT NOT NULL CHECK (marker_type IN ('水源', '休息')),
                coordinates TEXT NOT NULL,
                notes TEXT DEFAULT '',
                reliability TEXT CHECK (reliability IN ('高', '中', '低')),
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                is_required INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (route_id) REFERENCES routes(id) ON DELETE CASCADE
            );
            """
        )
        _migrate_routes_region(conn)
        _migrate_routes_mileage_days(conn)
        _migrate_markers_reliability(conn)
        _migrate_equipment_seed(conn)
        count = conn.execute("SELECT COUNT(*) FROM routes").fetchone()[0]
        if count == 0:
            _seed_data(conn)
        conn.commit()
    finally:
        conn.close()


def _migrate_routes_region(conn: sqlite3.Connection) -> None:
    """升级旧数据库：检测 routes 表是否缺少 region 字段，缺少则追加并回填默认值。"""
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(routes)").fetchall()]
    if "region" in columns:
        return
    conn.execute("ALTER TABLE routes ADD COLUMN region TEXT")
    conn.execute("UPDATE routes SET region = '未指定' WHERE region IS NULL OR region = ''")


def _migrate_routes_mileage_days(conn: sqlite3.Connection) -> None:
    """升级旧数据库：检测 routes 表是否缺少 mileage/days 字段，缺少则追加并回填种子路线数据。"""
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(routes)").fetchall()]
    added = False
    if "mileage" not in columns:
        conn.execute("ALTER TABLE routes ADD COLUMN mileage REAL DEFAULT 0")
        added = True
    if "days" not in columns:
        conn.execute("ALTER TABLE routes ADD COLUMN days REAL DEFAULT 0")
        added = True
    if added:
        conn.execute(
            "UPDATE routes SET mileage = ?, days = ? WHERE name LIKE '%雨崩冰湖%'",
            (18.5, 2.0),
        )
        conn.execute(
            "UPDATE routes SET mileage = ?, days = ? WHERE name LIKE '%格聂%'",
            (52.0, 4.0),
        )


def _migrate_markers_reliability(conn: sqlite3.Connection) -> None:
    """升级旧数据库：检测 markers 表是否缺少 reliability 字段，缺少则追加并回填种子数据。"""
    columns = [row["name"] for row in conn.execute("PRAGMA table_info(markers)").fetchall()]
    if "reliability" in columns:
        return
    conn.execute(
        "ALTER TABLE markers ADD COLUMN reliability TEXT CHECK (reliability IN ('高', '中', '低'))"
    )
    conn.execute(
        """
        UPDATE markers SET reliability = '高'
        WHERE marker_type = '水源' AND coordinates = 'N28.4123 E98.7891'
          AND route_id IN (SELECT id FROM routes WHERE name LIKE '%雨崩冰湖%')
        """
    )
    conn.execute(
        """
        UPDATE markers SET reliability = '中'
        WHERE marker_type = '水源' AND coordinates = 'N28.4189 E98.7955'
          AND route_id IN (SELECT id FROM routes WHERE name LIKE '%雨崩冰湖%')
        """
    )
    conn.execute(
        """
        UPDATE markers SET reliability = '高'
        WHERE marker_type = '水源' AND coordinates = 'N29.8234 E99.1234'
          AND route_id IN (SELECT id FROM routes WHERE name LIKE '%格聂%')
        """
    )
    conn.execute(
        """
        UPDATE markers SET reliability = '低'
        WHERE marker_type = '水源' AND coordinates = 'N29.8301 E99.1302'
          AND route_id IN (SELECT id FROM routes WHERE name LIKE '%格聂%')
        """
    )


def _migrate_equipment_seed(conn: sqlite3.Connection) -> None:
    """升级旧数据库：若装备表为空但已有路线，则按路线名称回填种子装备。"""
    eq_count = conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
    route_count = conn.execute("SELECT COUNT(*) FROM routes").fetchone()[0]
    if eq_count > 0 or route_count == 0:
        return

    equipment_map = {
        "雨崩冰湖": [("高帮登山鞋", 1), ("冲锋衣裤", 1), ("登山杖", 0)],
        "格聂": [("羽绒服", 1), ("冰爪冰镐", 1), ("头灯", 0)],
    }

    routes = conn.execute("SELECT id, name FROM routes").fetchall()
    for route in routes:
        matched = None
        for keyword, items in equipment_map.items():
            if keyword in route["name"]:
                matched = items
                break
        if matched:
            conn.executemany(
                "INSERT INTO equipment (route_id, name, is_required) VALUES (?, ?, ?)",
                [(route["id"], name, is_req) for name, is_req in matched],
            )


def _seed_data(conn: sqlite3.Connection) -> None:
    """写入 2 条路线、各 3 个标记点。"""
    routes = [
        ("雨崩冰湖线", "困难", "云南", 18.5, 2.0),
        ("格聂C线", "极难", "四川", 52.0, 4.0),
    ]
    for name, difficulty, region, mileage, days in routes:
        cur = conn.execute(
            "INSERT INTO routes (name, difficulty, region, mileage, days) VALUES (?, ?, ?, ?, ?)",
            (name, difficulty, region, mileage, days),
        )
        route_id = cur.lastrowid
        markers = [
            ("水源", "N28.4123 E98.7891", "溪流清澈，可直饮", "高"),
            ("休息", "N28.4156 E98.7920", "平坦草地，可扎营", None),
            ("水源", "N28.4189 E98.7955", "山涧泉水，需煮沸", "中"),
        ]
        if route_id == 2:
            markers = [
                ("水源", "N29.8234 E99.1234", "冰川融水，夏季充沛", "高"),
                ("休息", "N29.8267 E99.1267", "避风石滩", None),
                ("水源", "N29.8301 E99.1302", "季节性水源，旱季干涸", "低"),
            ]
        conn.executemany(
            "INSERT INTO markers (route_id, marker_type, coordinates, notes, reliability) VALUES (?, ?, ?, ?, ?)",
            [(route_id, t, c, n, r) for t, c, n, r in markers],
        )
        if route_id == 1:
            equipment_list = [
                ("高帮登山鞋", 1),
                ("冲锋衣裤", 1),
                ("登山杖", 0),
            ]
        else:
            equipment_list = [
                ("羽绒服", 1),
                ("冰爪冰镐", 1),
                ("头灯", 0),
            ]
        conn.executemany(
            "INSERT INTO equipment (route_id, name, is_required) VALUES (?, ?, ?)",
            [(route_id, name, is_req) for name, is_req in equipment_list],
        )
