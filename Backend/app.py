from flask import Flask, render_template, request, jsonify, redirect, session, make_response, send_from_directory
import os
import mysql.connector
import csv
import io
app = Flask(__name__)
app.secret_key = "queue_management_secret_key"
# ==========================================================
# DATABASE CONNECTION
# ==========================================================
db = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password="Root@1234",
    database="queue_management_db"
)
# ==========================================================
# HOME
# ==========================================================
@app.route("/")
def home():
    return render_template("index.html")
# ==========================================================
# ANALYTICS
# ==========================================================
@app.route("/analytics")
def analytics():
    return render_template("analytics.html")
# ==========================================================
# POWER BI
# ==========================================================
@app.route("/powerbi")
def powerbi():
    pbix_path = r"C:\Users\SAIKUMAR\OneDrive\New folder\Intelligent-Multi-Service-Queue-Management-System\Queue_Management_Analytics.pbix"
    if not os.path.exists(pbix_path):
        return "Power BI file not found."
    os.startfile(pbix_path)
    return redirect("/analytics")
# ==========================================================
# REGISTER
# ==========================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO users
            (full_name, email, phone, password_hash)
            VALUES (%s, %s, %s, %s)
        """, (
            full_name,
            email,
            phone,
            password
        ))
        db.commit()
        return "Registration Successful!"
    return render_template("register.html")
# ==========================================================
# LOGIN
# ==========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor = db.cursor()
        cursor.execute("""
            SELECT *
            FROM users
            WHERE email = %s
            AND password_hash = %s
        """, (
            email,
            password
        ))
        user = cursor.fetchone()
        if user:
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect("/dashboard")
        return "Invalid Email or Password"
    return render_template("login.html")
# ==========================================================
# USER DASHBOARD
# ==========================================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    cursor = db.cursor()
    # ------------------------------------------------------
    # GET USER'S LATEST BOOKING
    # ------------------------------------------------------
    cursor.execute("""
        SELECT
            a.appointment_id,
            a.org_id,
            a.token_number,
            a.status
        FROM appointments a
        WHERE a.user_id = %s
        ORDER BY a.appointment_id DESC
        LIMIT 1
    """, (user_id,))
    booking = cursor.fetchone()
    # ------------------------------------------------------
    # NO BOOKING
    # ------------------------------------------------------
    if not booking:
        return render_template(
            "dashboard.html",
            current_token="No active token",
            your_token="No booking",
            people_ahead=0,
            waiting_time=0
        )
    appointment_id = booking[0]
    org_id = booking[1]
    your_token = booking[2]
    your_status = booking[3]
    # ------------------------------------------------------
    # CURRENTLY SERVING TOKEN
    # ------------------------------------------------------
    cursor.execute("""
        SELECT MIN(token_number)
        FROM appointments
        WHERE org_id = %s
        AND status = 'In Progress'
    """, (org_id,))
    result = cursor.fetchone()
    if result and result[0] is not None:
        current_token = result[0]
    else:
        current_token = "No active token"
    # ------------------------------------------------------
    # PEOPLE AHEAD
    # ------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE org_id = %s
        AND token_number < %s
        AND status IN ('Pending', 'In Progress')
    """, (
        org_id,
        your_token
    ))
    result = cursor.fetchone()
    people_ahead = result[0] if result else 0
    # ------------------------------------------------------
    # ESTIMATED WAITING TIME
    # ------------------------------------------------------
    waiting_time = people_ahead * 15
    return render_template(
        "dashboard.html",
        current_token=current_token,
        your_token=your_token,
        people_ahead=people_ahead,
        waiting_time=waiting_time
    )
# ==========================================================
# BOOK QUEUE
# ==========================================================
@app.route("/book_queue", methods=["GET", "POST"])
def book_queue():
    if "user_id" not in session:
        return redirect("/login")
    cursor = db.cursor()
    if request.method == "POST":
        user_id = session["user_id"]
        city = request.form["city"]
        area = request.form["area"]
        category = request.form["category"]
        org_id = request.form["org_id"]
        service_id = request.form["service_id"]
        # --------------------------------------------------
        # GENERATE NEXT TOKEN FOR ORGANIZATION
        # --------------------------------------------------
        cursor.execute("""
            SELECT COALESCE(MAX(token_number), 0)
            FROM appointments
            WHERE org_id = %s
        """, (org_id,))
        token = cursor.fetchone()[0] + 1
        # --------------------------------------------------
        # INSERT NEW APPOINTMENT
        # STATUS IS EXPLICITLY SET TO PENDING
        # --------------------------------------------------
        cursor.execute("""
            INSERT INTO appointments
            (
                user_id,
                org_id,
                service_id,
                token_number,
                status
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            org_id,
            service_id,
            token,
            "Pending"
        ))
        db.commit()
        # --------------------------------------------------
        # ESTIMATED WAITING TIME
        # --------------------------------------------------
        avg_wait = (token - 1) * 15
        return f"""
        <h2>Booking Successful</h2>
        City : {city}<br>
        Area : {area}<br>
        Category : {category}<br><br>
        Token Number : {token}<br>
        Estimated Waiting Time : {avg_wait} Minutes<br>
        Status : Pending
        """
    # ------------------------------------------------------
    # GET ORGANIZATIONS
    # ------------------------------------------------------
    cursor.execute("""
        SELECT
            org_id,
            org_name
        FROM organizations
        ORDER BY org_name
    """)
    organizations = cursor.fetchall()
    # ------------------------------------------------------
    # GET SERVICES
    # ------------------------------------------------------
    cursor.execute("""
        SELECT
            service_id,
            service_name
        FROM services
        ORDER BY service_name
    """)
    services = cursor.fetchall()
    return render_template(
        "book_queue.html",
        organizations=organizations,
        services=services
    )
# ==========================================================
# GET ORGANIZATIONS
# ==========================================================
@app.route("/get_organizations", methods=["POST"])
def get_organizations():
    city = request.form["city"]
    area = request.form["area"]
    category = request.form["category"]
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            org_id,
            org_name
        FROM organizations
        WHERE city = %s
        AND area = %s
        AND category = %s
        ORDER BY org_name
    """, (
        city,
        area,
        category
    ))
    organizations = cursor.fetchall()
    return jsonify(organizations)
# ==========================================================
# GET SERVICES
# ==========================================================
@app.route("/get_services", methods=["POST"])
def get_services():
    org_id = request.form["org_id"]
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            service_id,
            service_name
        FROM services
        WHERE org_id = %s
        ORDER BY service_name
    """, (org_id,))
    services = cursor.fetchall()
    return jsonify(services)
# ==========================================================
# QUEUE STATUS
# ==========================================================
# IMPORTANT:
# Status is taken directly from appointments.status.
# This is the SAME status updated by Admin Dashboard.
# ==========================================================
@app.route("/queue_status")
def queue_status():
    if "user_id" not in session:
        return redirect("/login")
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            a.token_number,
            o.org_name,
            s.service_name,
            a.status
        FROM appointments a
        INNER JOIN organizations o
            ON a.org_id = o.org_id
        INNER JOIN services s
            ON a.service_id = s.service_id
        ORDER BY a.token_number
    """)
    queues = cursor.fetchall()
    return render_template(
        "queue_status.html",
        queues=queues
    )
# ==========================================================
# MY BOOKINGS
# ==========================================================
@app.route("/my_bookings")
def my_bookings():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            a.token_number,
            o.org_name,
            s.service_name,
            a.status,
            (
                SELECT COUNT(*)
                FROM appointments a2
                WHERE a2.org_id = a.org_id
                AND a2.token_number <= a.token_number
                AND a2.status IN ('Pending', 'In Progress')
            ) AS queue_position,
            a.org_id
        FROM appointments a
        JOIN organizations o
            ON a.org_id = o.org_id
        JOIN services s
            ON a.service_id = s.service_id
        WHERE a.user_id = %s
        ORDER BY a.token_number DESC
    """, (user_id,))
    bookings = cursor.fetchall()
    return render_template(
        "my_bookings.html",
        bookings=bookings
    )
# ==========================================================
# ADMIN DASHBOARD
# ==========================================================
@app.route("/admin_dashboard")
def admin_dashboard():
    cursor = db.cursor()
    # ======================================================
    # TOTAL BOOKINGS
    # ======================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
    """)
    total_bookings = cursor.fetchone()[0]
    # ======================================================
    # PENDING
    # ======================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status = 'Pending'
    """)
    pending_count = cursor.fetchone()[0]
    # ======================================================
    # IN PROGRESS
    # ======================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status = 'In Progress'
    """)
    in_progress_count = cursor.fetchone()[0]
    # ======================================================
    # COMPLETED
    # ======================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status = 'Completed'
    """)
    completed_count = cursor.fetchone()[0]
    # ======================================================
    # CANCELLED
    # ======================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE status = 'Cancelled'
    """)
    cancelled_count = cursor.fetchone()[0]
    # ======================================================
    # AVERAGE WAITING TIME
    #
    # Waiting time = people ahead × 15 minutes
    # ======================================================
    cursor.execute("""
        SELECT
            COALESCE(
                ROUND(
                    AVG(queue_position * 15),
                    0
                ),
                0
            )
        FROM
        (
            SELECT
                a.appointment_id,
                (
                    SELECT COUNT(*)
                    FROM appointments a2
                    WHERE a2.org_id = a.org_id
                    AND a2.token_number < a.token_number
                    AND a2.status IN ('Pending', 'In Progress')
                ) AS queue_position
            FROM appointments a
            WHERE a.status IN ('Pending', 'In Progress')
        ) AS queue_data
    """)
    average_waiting_time = cursor.fetchone()[0]
    # ======================================================
    # SEARCH
    # ======================================================
    search = request.args.get("search", "").strip()
    if search:
        search_value = "%" + search + "%"
        cursor.execute("""
            SELECT
                a.appointment_id,
                a.token_number,
                u.full_name,
                o.org_name,
                s.service_name,
                a.status
            FROM appointments a
            JOIN users u
                ON a.user_id = u.user_id
            JOIN organizations o
                ON a.org_id = o.org_id
            JOIN services s
                ON a.service_id = s.service_id
            WHERE
                u.full_name LIKE %s
                OR o.org_name LIKE %s
                OR s.service_name LIKE %s
            ORDER BY a.appointment_id DESC
        """, (
            search_value,
            search_value,
            search_value
        ))
    else:
        cursor.execute("""
            SELECT
                a.appointment_id,
                a.token_number,
                u.full_name,
                o.org_name,
                s.service_name,
                a.status
            FROM appointments a
            JOIN users u
                ON a.user_id = u.user_id
            JOIN organizations o
                ON a.org_id = o.org_id
            JOIN services s
                ON a.service_id = s.service_id
            ORDER BY a.appointment_id DESC
        """)
    bookings = cursor.fetchall()
    # ======================================================
    # SEND DATA TO ADMIN DASHBOARD
    # ======================================================
    return render_template(
        "admin_dashboard.html",
        total_bookings=total_bookings,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count,
        average_waiting_time=average_waiting_time,
        bookings=bookings
    )
# ==========================================================
# UPDATE STATUS
# ==========================================================
# Admin Dashboard buttons use this route.
#
# Pending     → In Progress
# In Progress → Completed
# Pending     → Cancelled
# In Progress → Cancelled
# ==========================================================
@app.route("/update_status/<int:appointment_id>/<status>")
def update_status(appointment_id, status):
    cursor = db.cursor()
    cursor.execute("""
        UPDATE appointments
        SET status = %s
        WHERE appointment_id = %s
    """, (
        status,
        appointment_id
    ))
    db.commit()
    return redirect("/admin_dashboard")
# ==========================================================
# CURRENT TOKEN
# ==========================================================
@app.route("/current_token")
def current_token():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    cursor = db.cursor()
    # ======================================================
    # GET USER'S LATEST BOOKING
    # ======================================================
    cursor.execute("""
        SELECT
            a.appointment_id,
            a.org_id,
            a.token_number,
            a.status
        FROM appointments a
        WHERE a.user_id = %s
        ORDER BY a.appointment_id DESC
        LIMIT 1
    """, (user_id,))
    booking = cursor.fetchone()
    # ======================================================
    # NO BOOKING
    # ======================================================
    if not booking:
        return render_template(
            "current_token.html",
            serving_token="No active token",
            your_token="No booking",
            people_ahead=0,
            waiting_time=0,
            active_count=0,
            your_status="No booking"
        )
    appointment_id = booking[0]
    org_id = booking[1]
    your_token = booking[2]
    your_status = booking[3]
    # ======================================================
    # CURRENTLY SERVING TOKEN
    # ======================================================
    cursor.execute("""
        SELECT MIN(token_number)
        FROM appointments
        WHERE org_id = %s
        AND status = 'In Progress'
    """, (org_id,))
    result = cursor.fetchone()
    if result and result[0] is not None:
        serving_token = result[0]
    else:
        serving_token = "No active token"
    # ======================================================
    # PEOPLE AHEAD
    # ======================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE org_id = %s
        AND token_number < %s
        AND status IN ('Pending', 'In Progress')
    """, (
        org_id,
        your_token
    ))
    result = cursor.fetchone()
    people_ahead = result[0] if result else 0
    # ======================================================
    # ESTIMATED WAITING TIME
    # ======================================================
    waiting_time = people_ahead * 15
    # ======================================================
    # ACTIVE CUSTOMERS
    # ======================================================
    cursor.execute("""
        SELECT COUNT(*)
        FROM appointments
        WHERE org_id = %s
        AND status IN ('Pending', 'In Progress')
    """, (org_id,))
    result = cursor.fetchone()
    active_count = result[0] if result else 0
    # ======================================================
    # SEND DATA TO CURRENT TOKEN PAGE
    # ======================================================
    return render_template(
        "current_token.html",
        serving_token=serving_token,
        your_token=your_token,
        people_ahead=people_ahead,
        waiting_time=waiting_time,
        active_count=active_count,
        your_status=your_status
    )
# ==========================================================
# OLD CURRENT TOKEN URL SUPPORT
# ==========================================================
@app.route("/current_token/<int:org_id>")
def current_token_old(org_id):
    return redirect("/current_token")
# ==========================================================
# EXPORT CSV
# ==========================================================
@app.route("/export_csv")
def export_csv():
    cursor = db.cursor()
    cursor.execute("""
        SELECT
            a.appointment_id,
            a.token_number,
            u.full_name,
            o.org_name,
            s.service_name,
            a.status
        FROM appointments a
        JOIN users u
            ON a.user_id = u.user_id
        JOIN organizations o
            ON a.org_id = o.org_id
        JOIN services s
            ON a.service_id = s.service_id
        ORDER BY a.appointment_id DESC
    """)
    bookings = cursor.fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Appointment ID",
        "Token",
        "Customer",
        "Organization",
        "Service",
        "Status"
    ])
    for row in bookings:
        writer.writerow(row)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = (
        "attachment; filename=queue_bookings.csv"
    )
    response.headers["Content-Type"] = "text/csv"
    return response
# ==========================================================
# LOGOUT
# ==========================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
# ==========================================================
# RUN APPLICATION
# ==========================================================
print(app.url_map)
if __name__ == "__main__":
    app.run(
        debug=True
    )

