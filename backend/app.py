"""冷门徒步路线水源标记 — Flask API 服务。"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from database import init_db, get_connection

app = Flask(__name__)
CORS(app)


def row_to_dict(row):
    """将 sqlite3.Row 转为普通字典。"""
    return dict(row) if row else None


VALID_RELIABILITIES = ("高", "中", "低")


def validate_reliability(reliability, marker_type):
    """校验可靠性字段：水源类型必须为高/中/低，休息类型必须为空。"""
    if marker_type == "水源":
        if reliability not in VALID_RELIABILITIES:
            return "水源类型必须指定可靠性（高/中/低）"
    else:
        if reliability is not None and reliability != "":
            return "休息类型无需指定可靠性"
    return None


@app.get("/api/stats")
def get_stats():
    """返回路线总数、标记点总数、水源数量、休息点数量。"""
    conn = get_connection()
    try:
        route_count = conn.execute("SELECT COUNT(*) FROM routes").fetchone()[0]
        marker_count = conn.execute("SELECT COUNT(*) FROM markers").fetchone()[0]
        water_count = conn.execute("SELECT COUNT(*) FROM markers WHERE marker_type = '水源'").fetchone()[0]
        rest_count = conn.execute("SELECT COUNT(*) FROM markers WHERE marker_type = '休息'").fetchone()[0]
        return jsonify({
            "routeCount": route_count,
            "markerCount": marker_count,
            "waterCount": water_count,
            "restCount": rest_count,
        })
    finally:
        conn.close()


# ── 路线 CRUD ──────────────────────────────────────────────


@app.get("/api/routes")
def list_routes():
    """获取全部路线列表，支持按名称关键词、地区和难度筛选。"""
    name = request.args.get("name", "").strip()
    region = request.args.get("region", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    conn = get_connection()
    try:
        conditions = []
        params = []
        if name:
            conditions.append("r.name LIKE ?")
            params.append(f"%{name}%")
        if region:
            conditions.append("region = ?")
            params.append(region)
        if difficulty:
            conditions.append("difficulty = ?")
            params.append(difficulty)
        where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
        rows = conn.execute(
            f"""SELECT r.id, r.name, r.difficulty, r.region, r.mileage, r.days,
                       (SELECT COUNT(*) FROM markers WHERE route_id = r.id) AS marker_count
                FROM routes r{where} ORDER BY r.id""",
            params,
        ).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.get("/api/routes/regions")
def list_regions():
    """获取所有地区列表（去重）。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT region FROM routes WHERE region IS NOT NULL AND region != '' ORDER BY region"
        ).fetchall()
        return jsonify([row["region"] for row in rows])
    finally:
        conn.close()


@app.get("/api/routes/difficulties")
def list_difficulties():
    """获取所有难度列表（去重）。"""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT DISTINCT difficulty FROM routes WHERE difficulty IS NOT NULL AND difficulty != '' ORDER BY difficulty"
        ).fetchall()
        return jsonify([row["difficulty"] for row in rows])
    finally:
        conn.close()


@app.get("/api/routes/<int:route_id>")
def get_route(route_id):
    """获取单条路线详情。"""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, name, difficulty, region, mileage, days FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if not row:
            return jsonify({"error": "路线不存在"}), 404
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.post("/api/routes")
def create_route():
    """新建路线。"""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    difficulty = (data.get("difficulty") or "").strip()
    region = (data.get("region") or "").strip()
    mileage = data.get("mileage", 0)
    days = data.get("days", 0)
    if not name or not difficulty or not region:
        return jsonify({"error": "名称、难度和地区不能为空"}), 400
    try:
        mileage = float(mileage)
        days = float(days)
    except (TypeError, ValueError):
        return jsonify({"error": "里程和天数必须为数字"}), 400
    if mileage < 0 or days < 0:
        return jsonify({"error": "里程和天数不能为负数"}), 400
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO routes (name, difficulty, region, mileage, days) VALUES (?, ?, ?, ?, ?)",
            (name, difficulty, region, mileage, days),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, name, difficulty, region, mileage, days FROM routes WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
        return jsonify(row_to_dict(row)), 201
    finally:
        conn.close()


@app.put("/api/routes/<int:route_id>")
def update_route(route_id):
    """更新路线。"""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    difficulty = (data.get("difficulty") or "").strip()
    region = (data.get("region") or "").strip()
    mileage = data.get("mileage", 0)
    days = data.get("days", 0)
    if not name or not difficulty or not region:
        return jsonify({"error": "名称、难度和地区不能为空"}), 400
    try:
        mileage = float(mileage)
        days = float(days)
    except (TypeError, ValueError):
        return jsonify({"error": "里程和天数必须为数字"}), 400
    if mileage < 0 or days < 0:
        return jsonify({"error": "里程和天数不能为负数"}), 400
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE routes SET name = ?, difficulty = ?, region = ?, mileage = ?, days = ? WHERE id = ?",
            (name, difficulty, region, mileage, days, route_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "路线不存在"}), 404
        row = conn.execute(
            "SELECT id, name, difficulty, region, mileage, days FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.delete("/api/routes/<int:route_id>")
def delete_route(route_id):
    """删除路线（级联删除标记点）。"""
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM routes WHERE id = ?", (route_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "路线不存在"}), 404
        return "", 204
    finally:
        conn.close()


@app.post("/api/routes/<int:route_id>/clone")
def clone_route(route_id):
    """克隆路线：复制名称（加「副本」后缀）、难度、地区、里程、天数、标记点和装备。"""
    conn = get_connection()
    try:
        route = conn.execute(
            "SELECT id, name, difficulty, region, mileage, days FROM routes WHERE id = ?",
            (route_id,),
        ).fetchone()
        if not route:
            return jsonify({"error": "路线不存在"}), 404

        markers = conn.execute(
            "SELECT marker_type, coordinates, notes, reliability FROM markers WHERE route_id = ? ORDER BY id",
            (route_id,),
        ).fetchall()

        equipment_list = conn.execute(
            "SELECT name, is_required FROM equipment WHERE route_id = ? ORDER BY is_required DESC, id",
            (route_id,),
        ).fetchall()

        new_name = route["name"] + "副本"

        cur = conn.execute(
            "INSERT INTO routes (name, difficulty, region, mileage, days) VALUES (?, ?, ?, ?, ?)",
            (new_name, route["difficulty"], route["region"], route["mileage"], route["days"]),
        )
        new_route_id = cur.lastrowid

        if markers:
            conn.executemany(
                "INSERT INTO markers (route_id, marker_type, coordinates, notes, reliability) VALUES (?, ?, ?, ?, ?)",
                [(new_route_id, m["marker_type"], m["coordinates"], m["notes"], m["reliability"]) for m in markers],
            )

        if equipment_list:
            conn.executemany(
                "INSERT INTO equipment (route_id, name, is_required) VALUES (?, ?, ?)",
                [(new_route_id, e["name"], e["is_required"]) for e in equipment_list],
            )

        conn.commit()

        new_route = conn.execute(
            "SELECT id, name, difficulty, region, mileage, days FROM routes WHERE id = ?",
            (new_route_id,),
        ).fetchone()
        return jsonify(row_to_dict(new_route)), 201
    finally:
        conn.close()


# ── 标记点 CRUD ────────────────────────────────────────────


@app.get("/api/routes/<int:route_id>/markers")
def list_markers(route_id):
    """获取某条路线的全部标记点。"""
    conn = get_connection()
    try:
        route = conn.execute(
            "SELECT id FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if not route:
            return jsonify({"error": "路线不存在"}), 404
        rows = conn.execute(
            """SELECT id, route_id, marker_type AS type, coordinates, notes, reliability
               FROM markers WHERE route_id = ? ORDER BY id""",
            (route_id,),
        ).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.post("/api/routes/<int:route_id>/markers")
def create_marker(route_id):
    """在某条路线下新建标记点。"""
    data = request.get_json(silent=True) or {}
    marker_type = (data.get("type") or "").strip()
    coordinates = (data.get("coordinates") or "").strip()
    notes = (data.get("notes") or "").strip()
    reliability = data.get("reliability")
    if reliability is not None:
        reliability = reliability.strip() or None
    if marker_type not in ("水源", "休息"):
        return jsonify({"error": "类型必须为「水源」或「休息」"}), 400
    if not coordinates:
        return jsonify({"error": "坐标不能为空"}), 400
    rel_err = validate_reliability(reliability, marker_type)
    if rel_err:
        return jsonify({"error": rel_err}), 400
    conn = get_connection()
    try:
        route = conn.execute(
            "SELECT id FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if not route:
            return jsonify({"error": "路线不存在"}), 404
        cur = conn.execute(
            """INSERT INTO markers (route_id, marker_type, coordinates, notes, reliability)
               VALUES (?, ?, ?, ?, ?)""",
            (route_id, marker_type, coordinates, notes, reliability),
        )
        conn.commit()
        row = conn.execute(
            """SELECT id, route_id, marker_type AS type, coordinates, notes, reliability
               FROM markers WHERE id = ?""",
            (cur.lastrowid,),
        ).fetchone()
        return jsonify(row_to_dict(row)), 201
    finally:
        conn.close()


@app.put("/api/markers/<int:marker_id>")
def update_marker(marker_id):
    """更新标记点。"""
    data = request.get_json(silent=True) or {}
    marker_type = (data.get("type") or "").strip()
    coordinates = (data.get("coordinates") or "").strip()
    notes = (data.get("notes") or "").strip()
    reliability = data.get("reliability")
    if reliability is not None:
        reliability = reliability.strip() or None
    if marker_type not in ("水源", "休息"):
        return jsonify({"error": "类型必须为「水源」或「休息」"}), 400
    if not coordinates:
        return jsonify({"error": "坐标不能为空"}), 400
    rel_err = validate_reliability(reliability, marker_type)
    if rel_err:
        return jsonify({"error": rel_err}), 400
    conn = get_connection()
    try:
        cur = conn.execute(
            """UPDATE markers SET marker_type = ?, coordinates = ?, notes = ?, reliability = ?
               WHERE id = ?""",
            (marker_type, coordinates, notes, reliability, marker_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "标记点不存在"}), 404
        row = conn.execute(
            """SELECT id, route_id, marker_type AS type, coordinates, notes, reliability
               FROM markers WHERE id = ?""",
            (marker_id,),
        ).fetchone()
        return jsonify(row_to_dict(row))
    finally:
        conn.close()


@app.delete("/api/markers/<int:marker_id>")
def delete_marker(marker_id):
    """删除标记点。"""
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM markers WHERE id = ?", (marker_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "标记点不存在"}), 404
        return "", 204
    finally:
        conn.close()


# ── 装备 CRUD ──────────────────────────────────────────────


@app.get("/api/routes/<int:route_id>/equipment")
def list_equipment(route_id):
    """获取某条路线的全部装备清单。"""
    conn = get_connection()
    try:
        route = conn.execute(
            "SELECT id FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if not route:
            return jsonify({"error": "路线不存在"}), 404
        rows = conn.execute(
            """SELECT id, route_id, name, is_required
               FROM equipment WHERE route_id = ? ORDER BY is_required DESC, id""",
            (route_id,),
        ).fetchall()
        return jsonify([row_to_dict(r) for r in rows])
    finally:
        conn.close()


@app.post("/api/routes/<int:route_id>/equipment")
def create_equipment(route_id):
    """在某条路线下新增装备。"""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    is_required = data.get("isRequired", 0)
    if not name:
        return jsonify({"error": "装备名称不能为空"}), 400
    try:
        is_required = int(is_required)
        if is_required not in (0, 1):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({"error": "是否必备必须为 0 或 1"}), 400
    conn = get_connection()
    try:
        route = conn.execute(
            "SELECT id FROM routes WHERE id = ?", (route_id,)
        ).fetchone()
        if not route:
            return jsonify({"error": "路线不存在"}), 404
        cur = conn.execute(
            """INSERT INTO equipment (route_id, name, is_required)
               VALUES (?, ?, ?)""",
            (route_id, name, is_required),
        )
        conn.commit()
        row = conn.execute(
            """SELECT id, route_id, name, is_required
               FROM equipment WHERE id = ?""",
            (cur.lastrowid,),
        ).fetchone()
        return jsonify(row_to_dict(row)), 201
    finally:
        conn.close()


@app.delete("/api/equipment/<int:equipment_id>")
def delete_equipment(equipment_id):
    """删除装备。"""
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "装备不存在"}), 404
        return "", 204
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=7000, debug=True)
