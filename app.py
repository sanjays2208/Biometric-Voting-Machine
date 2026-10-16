import os, sqlite3, hashlib, secrets
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template, flash, abort

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("BVM_DB_PATH", ROOT/"instance"/"bvm.sqlite3"))
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-me")
CANDIDATES = ["Candidate A", "Candidate B", "Candidate C"]

def db_connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH); c.row_factory = sqlite3.Row
    return c

def init_db():
    with db_connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS voters(voter_id TEXT PRIMARY KEY, demo_pin TEXT NOT NULL, eligible INTEGER NOT NULL DEFAULT 1, has_voted INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS ballots(ballot_id TEXT PRIMARY KEY, candidate TEXT NOT NULL, created_at TEXT NOT NULL, previous_hash TEXT NOT NULL, record_hash TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, expires_at TEXT NOT NULL);
        """)
        db.execute("INSERT OR IGNORE INTO voters VALUES('DEMO001','1234',1,0)")
        db.execute("INSERT OR IGNORE INTO voters VALUES('DEMO002','5678',1,0)")

def event(kind):
    with db_connect() as db:
        db.execute("INSERT INTO events(event_type,created_at) VALUES(?,?)",(kind,datetime.now(timezone.utc).isoformat()))

def add_ballot(candidate):
    with db_connect() as db:
        prev = db.execute("SELECT record_hash FROM ballots ORDER BY rowid DESC LIMIT 1").fetchone()
        previous = prev["record_hash"] if prev else "GENESIS"
        ballot_id = secrets.token_hex(16); stamp = datetime.now(timezone.utc).isoformat()
        digest = hashlib.sha256(f"{ballot_id}|{candidate}|{stamp}|{previous}".encode()).hexdigest()
        db.execute("INSERT INTO ballots VALUES(?,?,?,?,?)",(ballot_id,candidate,stamp,previous,digest))

@app.route("/")
def home():
    init_db()
    return render_template("index.html")

@app.route("/authenticate", methods=["POST"])
def authenticate():
    init_db()
    voter_id=request.form.get("voter_id","").strip().upper()
    pin=request.form.get("pin","").strip()
    with db_connect() as db:
        voter=db.execute("SELECT * FROM voters WHERE voter_id=?",(voter_id,)).fetchone()
        if not voter or voter["demo_pin"] != pin or not voter["eligible"]:
            event("authentication_failed"); flash("Authentication failed. Try DEMO001 / 1234 or DEMO002 / 5678.")
            return redirect(url_for("home"))
        if voter["has_voted"]:
            flash("This demo voter has already cast a ballot."); return redirect(url_for("home"))
        db.execute("UPDATE voters SET has_voted=1 WHERE voter_id=?",(voter_id,))
        token=secrets.token_urlsafe(24)
        db.execute("INSERT INTO sessions VALUES(?,?)",(token,datetime.now(timezone.utc).isoformat()))
    event("authentication_success")
    return render_template("vote.html", candidates=CANDIDATES, token=token)

@app.route("/vote", methods=["POST"])
def vote():
    token=request.form.get("token",""); candidate=request.form.get("candidate","")
    if candidate not in CANDIDATES or not token: abort(400)
    with db_connect() as db:
        row=db.execute("SELECT token FROM sessions WHERE token=?",(token,)).fetchone()
        if not row: abort(403)
        db.execute("DELETE FROM sessions WHERE token=?",(token,))
    add_ballot(candidate); event("ballot_cast")
    return render_template("thanks.html")

@app.route("/dashboard")
def dashboard():
    init_db()
    with db_connect() as db:
        total=db.execute("SELECT COUNT(*) n FROM ballots").fetchone()["n"]
        events=db.execute("SELECT event_type,COUNT(*) n FROM events GROUP BY event_type").fetchall()
        results=db.execute("SELECT candidate,COUNT(*) votes FROM ballots GROUP BY candidate").fetchall()
        rows=db.execute("SELECT * FROM ballots ORDER BY rowid").fetchall()
    valid=True; previous="GENESIS"
    for r in rows:
        payload=f'{r["ballot_id"]}|{r["candidate"]}|{r["created_at"]}|{r["previous_hash"]}'
        if r["previous_hash"] != previous or hashlib.sha256(payload.encode()).hexdigest()!=r["record_hash"]: valid=False
        previous=r["record_hash"]
    return render_template("dashboard.html",total=total,events=events,results=results,chain_valid=valid)

if __name__=="__main__":
    init_db()
    app.run(host="127.0.0.1",port=int(os.environ.get("PORT","5000")),debug=False)
