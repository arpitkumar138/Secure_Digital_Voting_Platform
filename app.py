from flask import Flask, render_template, request, session, redirect
import sqlite3
import os
import secrets
import time
from twilio.rest import Client

app = Flask(__name__)

# Demo secret key
app.secret_key = "secure-voting-demo-key"


# ==============================
# SEND OTP SMS
# ==============================

def send_otp_sms(mobile_number):
    client = Client(
        os.environ["TWILIO_ACCOUNT_SID"],
        os.environ["TWILIO_AUTH_TOKEN"]
    )

    verification = client.verify.v2.services(
        os.environ["TWILIO_VERIFY_SERVICE_SID"]
    ).verifications.create(
        to="+91" + mobile_number,
        channel="sms"
    )

    print("VERIFY OTP STATUS:", verification.status)


# ==============================
# DATABASE INITIALIZATION
# ==============================

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

    # Demo voters
    cursor.execute("""
    INSERT OR IGNORE INTO voters
    (voter_id, mobile_number, has_voted)
    VALUES ('VOTER123', '7217205430', 0)
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anonymous_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vote_token TEXT UNIQUE NOT NULL,
    party TEXT NOT NULL)
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO voters
    (voter_id, mobile_number, has_voted)
    VALUES ('VOTER456', '7217205430', 0)
    """)

    conn.commit()
    conn.close()


# ==============================
# HOME
# ==============================

@app.route("/")
def home():

    return render_template("index.html")


# ==============================
# ADMIN PAGE
# ==============================

@app.route("/admin")
def admin():

    return render_template("admin.html")


# ==============================
# ADMIN LOGIN
# ==============================

@app.route("/admin-login", methods=["POST"])
def admin_login():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":

        session["admin"] = True

        return redirect("/results")

    return "Invalid Admin Credentials!"


# ==============================
# VOTER VERIFICATION
# ==============================

@app.route("/verify", methods=["POST"])
def verify():

    voter_id = request.form["voter_id"].strip()

    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT has_voted, mobile_number
        FROM voters
        WHERE voter_id = ?
        """,
        (voter_id,)
    )

    voter = cursor.fetchone()

    conn.close()

    # Voter does not exist
    if voter is None:

        return "Invalid Voter ID!"


    # Voter already voted
    if voter[0] == 1:

        return "You have already voted!"


    # Generate 6-digit OTP
    otp = str(secrets.randbelow(900000) + 100000)
    print("DEMO OTP:", otp)

    # Store voter information
    session["voter_id"] = voter_id
    session["mobile_number"] = voter[1]
    session["otp_verified"] = False

# Send OTP through Twilio Verify
    try:
        send_otp_sms(voter[1])
        print("OTP SMS SENT")
    except Exception as e:
        print("SMS ERROR:", e)
        return "Unable to send OTP. Please try again."


    return render_template("otp.html")


# ==============================
# OTP VERIFICATION
# ==============================

@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    entered_otp = request.form["otp"].strip()

    mobile_number = session.get("mobile_number")

    if not mobile_number:
        return "OTP session expired. Please start again."

    try:

        client = Client(
            os.environ["TWILIO_ACCOUNT_SID"],
            os.environ["TWILIO_AUTH_TOKEN"]
        )

        verification_check = client.verify.v2.services(
            os.environ["TWILIO_VERIFY_SERVICE_SID"]
        ).verification_checks.create(
            to="+91" + mobile_number,
            code=entered_otp
        )

        if verification_check.status == "approved":

            session["otp_verified"] = True

            return render_template("voting.html")

        else:

            return "Invalid OTP. Please try again."

    except Exception as e:

        print("VERIFY ERROR:", e)

        return "OTP verification failed. Please try again."


# ==============================
# VOTE
# ==============================

@app.route("/vote", methods=["POST"])
def vote():

    voter_id = session.get("voter_id")

    otp_verified = session.get("otp_verified")


    # Voter verification required
    if not voter_id:

        return "Please verify your Voter ID first!"


    # OTP verification required
    if not otp_verified:

        return "Please complete OTP verification first."


    candidate = request.form["candidate"]


    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()


    # Check voter
    cursor.execute(
        """
        SELECT has_voted
        FROM voters
        WHERE voter_id = ?
        """,
        (voter_id,)
    )

    voter = cursor.fetchone()


    if voter is None:

        conn.close()

        return "Invalid Voter!"


    # Prevent duplicate voting
    if voter[0] == 1:

        conn.close()

        return "You have already voted!"


    # Create anonymous vote token
    vote_token = secrets.token_hex(16)

   # Store vote without voter ID
    cursor.execute(
            """
           INSERT INTO anonymous_votes
           (vote_token, party)
            VALUES (?, ?)
           """,
            (vote_token, candidate)
)


    # Mark voter as voted
    cursor.execute(
        """
        UPDATE voters
        SET has_voted = 1
        WHERE voter_id = ?
        """,
        (voter_id,)
    )


    conn.commit()
    conn.close()


    # Clear voting session
    session.pop("voter_id", None)
    session.pop("mobile_number", None)
    session.pop("otp_verified", None)


    return render_template(
        "success.html",
        candidate=candidate
    )


# ==============================
# RESULTS
# ==============================

@app.route("/results")
def results():

    if not session.get("admin"):

        return "Access Denied! Please login as Admin."


    conn = sqlite3.connect("voting.db")
    cursor = conn.cursor()


    cursor.execute("SELECT party, COUNT(*) FROM anonymous_votes GROUP BY party")

    results_data = cursor.fetchall()

    conn.close()


    return render_template(
        "results.html",
        results=results_data
    )


# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/admin")


# ==============================
# RUN APPLICATION
# ==============================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)
