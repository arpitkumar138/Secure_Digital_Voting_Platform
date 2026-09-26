from flask import Flask, render_template, request, session, redirect
import sqlite3
import os
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = "secure-voting-demo-key"


def send_sms(mobile_number):
    client = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"]
    )

    message = client.messages.create(
        body="sms_event_notifications",
        from_=os.environ["TWILIO_PHONE_NUMBER"],
        to="+91" + mobile_number
    )

    print("SMS SENT:", message.sid)


def init_db():
    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voters (
        voter_id TEXT PRIMARY KEY,
        mobile_number TEXT NOT NULL,
        has_voted INTEGER DEFAULT 0
    )
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id TEXT NOT NULL,
        party TEXT NOT NULL
    )
""")

    # Demo voter
    cursor.execute("""
    INSERT OR IGNORE INTO voters (voter_id, mobile_number, has_voted)
    VALUES ('VOTER123', '7217205430', 0)
""")
    
    cursor.execute("""
    INSERT OR IGNORE INTO voters (voter_id, mobile_number, has_voted)
    VALUES ('VOTER456', '7217205430', 0)
""")
   
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/admin-login", methods=["POST"])
def admin_login():
    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":
        session["admin"] = True
        return redirect("/results")

    return "Invalid Admin Credentials!"


@app.route("/verify", methods=["POST"])
def verify():
    voter_id = request.form["voter_id"]

    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    cursor.execute(
    "SELECT has_voted, mobile_number FROM voters WHERE voter_id = ?",
    (voter_id,)
)

    voter = cursor.fetchone()
    conn.close()

    if voter is None:
        return "Invalid Voter ID!"

    if voter[0] == 1:
        return "You have already voted!"

    session["voter_id"] = voter_id
    session["mobile_number"] = voter[1]

    return render_template("voting.html")


@app.route("/vote", methods=["POST"])
def vote():
    voter_id = session.get("voter_id")

    if not voter_id:
        return "Please verify your Voter ID first!"

    candidate = request.form["candidate"]

    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT has_voted FROM voters WHERE voter_id = ?",
        (voter_id,)
    )

    voter = cursor.fetchone()

    if voter is None:
        conn.close()
        return "Invalid Voter!"

    if voter[0] == 1:
        conn.close()
        return "You have already voted!"

    cursor.execute(
        "INSERT INTO votes (voter_id, party) VALUES (?, ?)",
        (voter_id, candidate)
    )

    cursor.execute(
        "UPDATE voters SET has_voted = 1 WHERE voter_id = ?",
        (voter_id,)
    )

    conn.commit()
    conn.close()

    try:
        send_sms(session.get("mobile_number"))
    except Exception as e:
        print("SMS ERROR:", e)

    return render_template(
        "success.html",
        candidate=candidate
)


@app.route("/results")
def results():
    
    if not session.get("admin"):
        return "Access Denied! Please login as Admin."

    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT party, COUNT(*)
    FROM votes
    GROUP BY party
""")

    results_data = cursor.fetchall()

    conn.close()

    return render_template("results.html", results=results_data)


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/admin")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

