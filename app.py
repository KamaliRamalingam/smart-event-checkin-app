"""Event Check-in Application."""

from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    session,
    send_file,
)
from functools import wraps
import os
import qrcode
from io import BytesIO

app = Flask(__name__)

# ===== CONFIG =====
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# Demo users
valid_users = {
    "admin": os.getenv("ADMIN_PASSWORD", "admin123"),
    "user": os.getenv("USER_PASSWORD", "user123"),
    "demo": os.getenv("DEMO_PASSWORD", "demo123"),
}


# ===== AUTH DECORATOR =====
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# ===== SAMPLE DATA =====
events = [
    {
        "id": "JB235005590",
        "title": "Tech Conference 2026",
        "start_date": "2026-06-15",
        "end_date": "2026-06-17",
        "type": "Conference",
        "capacity": 500,
        "registered": 342,
        "payment": "Paid",
        "status": "Active",
        "description": "Annual tech conference",
    }
]

attendees = []


# ===== ROUTES =====
@app.route("/")
@login_required
def index():
    return render_template(
        "index.html",
        username=session.get("user_id", "User"),
    )


# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("username")
        password_input = request.form.get("password")

        if user_id in valid_users and valid_users[user_id] == password_input:
            session["user_id"] = user_id
            return redirect("/")

        return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ===== LOGOUT =====
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# ===== API =====
@app.route("/api/events")
@login_required
def get_events():
    return jsonify(events)


@app.route("/api/attendees")
@login_required
def get_attendees():
    return jsonify(attendees)


@app.route("/api/checkin/<attendee_id>", methods=["POST"])
@login_required
def check_in(attendee_id):
    for a in attendees:
        if a.get("id") == attendee_id:
            a["checkedIn"] = True
            return jsonify({"success": True})

    return jsonify({"success": False, "error": "Not found"}), 404


@app.route("/api/qrcode/<attendee_id>")
@login_required
def get_qrcode(attendee_id):
    qr = qrcode.make(attendee_id)
    img_io = BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")


# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=False)
