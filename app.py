import os
from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras



app = Flask(__name__)
# Enable CORS (default all origins)
CORS(app)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL is None:
    # Bu, kodun Render'da çalışıp çalışmadığını anlamak için iyi bir log'dur.
    print("UYARI: DATABASE_URL ortam değişkeni bulunamadı. API veritabanına bağlanamayacak.")

def get_db_connection():
    """
    Veritabanına yeni bir bağlantı oluşturur.
    Bağlantı bilgisini 'DATABASE_URL' ortam değişkeninden okur.
    """
    try:
        # DATABASE_URL boşsa (None) bu satır hata verir, bu da istediğimiz bir şey.
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"DB connection error: {e}")
        return None

@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Hasta Risk API'si çalışıyor"})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/patient/<string:patient_id>", methods=["GET"])
def get_patient_risk(patient_id: str):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "database connection failed"}), 500
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """
            SELECT patient_id, visit_id, visit_no, age, gender, risk_score
            FROM clinical.patient_risk_scores
            WHERE patient_id = %s
            ORDER BY visit_no ASC
            """,
            (patient_id,),
        )
        rows = cur.fetchall()
        cur.close()
        if not rows:
            return jsonify({"error": "patient not found"}), 404
        return jsonify(rows)
    except Exception as e:
        print(e)
        return jsonify({"error": "internal server error"}), 500
    finally:
        if conn:
            conn.close()


# Alias endpoint matching the user-specified pattern (typos kept in path)
@app.route("/ap/patent/<string:patent_id>", methods=["GET"])
def get_patent_alias(patent_id: str):
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "database connection failed"}), 500
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """
            SELECT patient_id, visit_id, visit_no, age, gender, risk_score
            FROM clinical.patient_risk_scores
            WHERE patient_id = %s
            ORDER BY visit_no ASC
            """,
            (patent_id,),
        )
        rows = cur.fetchall()
        cur.close()
        if not rows:
            return jsonify({"error": "Patient not found"}), 404
        return jsonify(rows)
    except Exception as e:
        print(e)
        return jsonify({"error": "internal server error"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/api/patients/high-risk", methods=["GET"])
def get_high_risk_patients():
    limit = request.args.get("limit", default=50, type=int)
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "database connection failed"}), 500
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """
            SELECT patient_id, visit_id, visit_no, age, gender, risk_score
            FROM clinical.patient_risk_scores
            WHERE risk_score > 0.8
            ORDER BY risk_score DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows)
    except Exception as e:
        print(e)
        return jsonify({"error": "internal server error"}), 500
    finally:
        if conn:
            conn.close()


# Alias endpoint for C: GET '/ap/patents/hgh-rsk'
@app.route("/ap/patents/hgh-rsk", methods=["GET"])
def get_patents_hgh_rsk():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "database connection failed"}), 500
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            """
            SELECT patient_id, visit_id, visit_no, age, gender, risk_score
            FROM clinical.patient_risk_scores
            WHERE risk_score >= %s
            ORDER BY risk_score DESC
            LIMIT 50
            """,
            (0.8,),
        )
        rows = cur.fetchall()
        cur.close()
        return jsonify(rows)
    except Exception as e:
        print(e)
        return jsonify({"error": "internal server error"}), 500
    finally:
        if conn:
            conn.close()
