from MySQLdb import MySQLError
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify, send_file, make_response, send_from_directory
from mysql.connector import Error
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON
from email.message import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from flask_mail import Mail, Message
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from functools import wraps
from werkzeug.utils import secure_filename
from flask import session
import io, os, pdfkit, bcrypt
import mysql.connector, random, string, json, os, uuid, smtplib, ssl, MySQLdb.cursors, razorpay, warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")  # change in prod
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/gov_services'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "uploads"

# ✅ Flask Mail Connection
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hetvi5007@gmail.com'
app.config['MAIL_PASSWORD'] = 'jyoibgqmyckxewuz'  # Use an App Password, not your real Gmail password
mail = Mail(app)

# ✅ Flask Twilio Connection
ACCOUNT_SID = "AC5b329f9457b1a375174144626bd26a1d"
AUTH_TOKEN = "84606e7abd243d1fda07fb5859e91733"
TWILIO_PHONE = "+12173946575"  
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ✅ Initialize SQLAlchemy
db = SQLAlchemy(app)

# Razorpay client (use test keys first)
razorpay_client = razorpay.Client(auth=("rzp_test_Rcq1OkhS35AWp9", "ldq5ru7Am3Q19qxjUHhF5w7x"))

# ✅ Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="",
        database="gov_services"
    )

with app.app_context():
    db.create_all()

# ✅ Load JSON file safely
json_path = r"C:\Users\Hetvi\OneDrive\Desktop\Final Year Project\E-Gov\data.json"  # update your path
if not os.path.exists(json_path):
    print(f"❌ JSON file not found: {json_path}")
    exit()
try:
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        if not data:
            print("❌ JSON file is empty or invalid.")
            exit()
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON format: {e}")
    exit()
print("✅ JSON loaded successfully.")

# ✅ Define models
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    image = db.Column(db.String(255))
    short_desc = db.Column(db.Text)
    long_desc = db.Column(db.Text)
    base_price = db.Column(db.Float)
    documents = db.Column(db.Text)  # ✅ list of {"name": "Aadhaar", "price": 20.0}

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_id = db.Column(db.String(50), unique=True, index=True)  # e.g., APP-0001
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    mobile = db.Column(db.String(50))
    total_amount = db.Column(db.Numeric(10,2))
    status = db.Column(db.String(50))
    #razorpay_order_id = db.Column(db.String(200), nullable=True)
    #razorpay_payment_id = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Admin Dashboard Route
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):   # protect admin section
        return redirect(url_for("login"))
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM application ORDER BY id DESC")
    applications = cur.fetchall()
    conn.close()
    return render_template("admin_dashboard.html", applications=applications)

@app.route("/reject_application/<app_id>", methods=["POST"])
def reject_application(app_id):
    reason = request.form.get("reason")

    print("Received reason:", reason)
    print("App ID:", app_id)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM application WHERE app_id=%s", (app_id,))
    app_data = cursor.fetchone()

    if not app_data:
        flash("Application not found!", "error")
        return redirect("/admin/dashboard")

    cursor.execute("""
        UPDATE application SET status='Rejected', reject_reason=%s WHERE app_id=%s """, (reason, app_id)
    )
    conn.commit()

    # Send email
    try:
        msg = Message(
            subject="Application Rejected",
            sender="hetvi5007@gmail.com",
            recipients=[app_data["email"]]
        )

        msg.body = (
            f"Hello {app_data['name']},\n\n"
            f"Your application ID {app_id} for {app_data['service_name']} has been rejected.\n\n"
            f"Reason:\n{reason}\n\n"
            f"You may correct the issue and re-apply the application.\n\n"
            "Regards,\nAdmin Team"
        )
        mail.send(msg)
        print("Rejection email sent")
    except Exception as e:
        print("Email error:", e)

    flash("Application rejected & email sent!", "success")
    return redirect("/admin/dashboard")


@app.route("/update_status/<app_id>/<new_status>")
def update_status(app_id, new_status):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE application SET status=%s WHERE app_id=%s", (new_status, app_id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/complete_application/<app_id>", methods=["POST"])
def complete_application(app_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch application
    cursor.execute("SELECT * FROM application WHERE app_id=%s", (app_id,))
    application = cursor.fetchone()

    if not application:
        cursor.close()
        conn.close()
        return "Application not found", 404

    # Ensure document exists
    document_path = application["document_path"]
    if not document_path:
        cursor.close()
        conn.close()
        return "Document not generated yet.", 400

    # Update status to Completed
    cursor.execute(
        "UPDATE application SET status='Completed' WHERE app_id=%s", (app_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()

    # Send document email
    send_document_email(application["email"], document_path)
    return render_template("application_form_completed.html")

# Admin Analytics Route
@app.route("/admin/analytics")
def admin_analytics():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ===== KPI METRICS =====
    cur.execute("SELECT COUNT(*) AS total FROM application")
    total = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) AS rejected FROM application WHERE status='Rejected'")
    rejected = cur.fetchone()['rejected']

    cur.execute("SELECT COUNT(*) AS received FROM application WHERE status='Received'")
    received = cur.fetchone()['received']

    cur.execute("SELECT COUNT(*) AS verified FROM application WHERE status='Verified'")
    verified = cur.fetchone()['verified']

    cur.execute("SELECT COUNT(*) AS processing FROM application WHERE status='Processing'")
    processing = cur.fetchone()['processing']

    cur.execute("SELECT COUNT(*) AS completed FROM application WHERE status='Completed'")
    completed = cur.fetchone()['completed']

    cur.execute("SELECT SUM(total_amount) AS revenue FROM application WHERE payment_status='Paid'")
    revenue = cur.fetchone()['revenue'] or 0

    # ===== APPLICATION TREND =====
    cur.execute("""
        SELECT DATE(created_at) AS date, COUNT(*) AS count FROM application
        GROUP BY DATE(created_at) ORDER BY DATE(created_at)
    """)
    trend = cur.fetchall()

    # ===== SERVICE-WISE APPLICATION COUNT =====
    cur.execute("""
        SELECT service_name, COUNT(*) AS count FROM application GROUP BY service_name
    """)
    service_data = cur.fetchall()

    # ===== SERVICE-WISE MONTHLY REVENUE =====
    cur.execute("""
        SELECT service_name, DATE_FORMAT(created_at, '%b-%y') AS month, SUM(total_amount) AS monthly_revenue
        FROM application WHERE payment_status='Paid'
        GROUP BY service_name, DATE_FORMAT(created_at, '%b-%y') ORDER BY month, service_name
    """)
    monthly_summary = cur.fetchall()

    # ===== TOTAL REVENUE PER MONTH =====
    cur.execute("""
        SELECT DATE_FORMAT(created_at, '%b-%y') AS month, SUM(total_amount) AS total_month_revenue
        FROM application WHERE payment_status='Paid'
        GROUP BY DATE_FORMAT(created_at, '%b-%y') ORDER BY month
    """)
    month_totals = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "analytics.html",
        total=total,
        rejected=rejected,
        received=received,
        verified=verified,
        processing=processing,
        completed=completed,
        revenue=revenue,
        trend=trend,
        service_data=service_data,
        monthly_summary=monthly_summary,
        month_totals=month_totals
    )

@app.route("/admin/analytics/pdf")
def analytics_pdf():

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # --- Fetch Monthly Revenue Summary ---
    cur.execute("""
        SELECT DATE_FORMAT(created_at, '%b-%y') AS month, service_name, SUM(total_amount) AS monthly_revenue
        FROM application WHERE payment_status='Paid' GROUP BY month, service_name ORDER BY month DESC
    """)
    monthly_summary = cur.fetchall()

    # --- Fetch Total Revenue Per Month ---
    cur.execute("""
        SELECT DATE_FORMAT(created_at, '%b-%y') AS month, SUM(total_amount) AS total_month_revenue
        FROM application WHERE payment_status='Paid' GROUP BY month ORDER BY month DESC
    """)
    month_totals = cur.fetchall()

    cur.close()
    conn.close()

    # --- Create PDF in Memory ---
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("<b>Monthly Revenue Report (Service-wise)</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    # ===== TABLE 1: Monthly Revenue Summary (Service-wise) =====
    data1 = [["Month", "Service Name", "Revenue (Rs.)"]]

    for row in monthly_summary:
        data1.append([
            row['month'],
            row['service_name'],
            f"Rs. {row['monthly_revenue']}"
        ])

    table1 = Table(data1, colWidths=[100, 200, 100])
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (2,1), (2,-1), 'RIGHT')
    ]))

    elements.append(table1)
    elements.append(Spacer(1, 20))

    # ===== TABLE 2: Total Revenue Per Month =====
    elements.append(Paragraph("<b>Total Revenue Per Month</b>", styles['Heading2']))
    elements.append(Spacer(1, 8))

    data2 = [["Month", "Total Revenue (Rs.)"]]

    for row in month_totals:
        data2.append([
            row['month'],
            f"Rs. {row['total_month_revenue']}"
        ])

    table2 = Table(data2, colWidths=[150, 150])
    table2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,1), (1,-1), 'RIGHT')
    ]))

    elements.append(table2)
    pdf.title = f"Revenue_Report.pdf"

    # Build PDF
    pdf.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Analytics_Report.pdf",
        mimetype="application/pdf"
    )

@app.route("/admin/settings", methods=["GET", "POST"])
def admin_settings():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch admin details (example)
    cur.execute("SELECT * FROM users WHERE user_id = 2")
    admin = cur.fetchone()

    cur.execute("SELECT * FROM service")
    services = cur.fetchall()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        cur.execute("UPDATE users SET name=%s, email=%s WHERE user_id=2",
                    (name, email))
        conn.commit()
        flash("Updated!", "success")

    conn.close()
    return render_template("admin_settings.html", admin=admin, services=services)

@app.route("/admin/settings/update_profile", methods=["POST"])
def update_profile():
    name = request.form.get("name")
    email = request.form.get("email")
    user_id = 2

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Check if email is used by another admin
    cur.execute("SELECT user_id FROM users WHERE email = %s", (email,))
    existing = cur.fetchone()
    if existing and existing['user_id'] != user_id:
        flash("Email already in use by another account.", "danger")
        conn.close()
        return redirect("/admin/settings")

    # Perform update
    cur.execute("UPDATE users SET name=%s, email=%s WHERE user_id=%s",
                (name, email, 2))
    conn.commit()
    conn.close()

    flash("Profile updated successfully!", "success")
    return redirect("/admin/settings")

@app.route("/admin/settings/change_password", methods=["POST"])
def change_password():
    old_pw = request.form.get("old_password")
    new_pw = request.form.get("new_password")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT password FROM users WHERE user_id=2")
    admin = cur.fetchone()

    # Check old password
    if not check_password_hash(admin["password"], old_pw):
        flash("Old password is incorrect.", "danger")
        return redirect("/admin/settings")

    # Save new password
    hashed = generate_password_hash(new_pw)
    cur.execute("UPDATE users SET password=%s WHERE user_id=2", (hashed,))
    conn.commit()
    conn.close()

    flash("Password updated!", "success")
    return redirect("/admin/settings")

# ✅ UPDATE SERVICE FEE
@app.route("/admin/settings/update_fee/<int:id>", methods=["POST"])
def update_fee(id):
    fee = request.form.get("fee")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE service SET base_price=%s WHERE service_id=%s", (fee, id))
    conn.commit()
    conn.close()

    flash("Service fee updated!", "success")
    return redirect("/admin/settings")

# ✅ TOGGLE SERVICE ACTIVE/INACTIVE
@app.route("/admin/settings/toggle_service/<int:id>", methods=["POST"])
def toggle_service(id):
    status = request.form.get("status")  # "on" or None

    new_status = 1 if status == "on" else 0

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE service SET is_active=%s WHERE service_id=%s",
                (new_status, id))
    conn.commit()
    conn.close()

    flash("Service status updated!", "success")
    return redirect("/admin/settings")

# ✅ Session timeout: auto logout after 30 minutes
app.permanent_session_lifetime = timedelta(minutes=30)

# Functions
def allowed_file(filename):
    allowed_extensions = {"pdf", "jpg", "jpeg", "png"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

def send_document_email(to_email, document_path):
    sender = "hetvi5007@gmail.com"
    password = "jyoibgqmyckxewuz"

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = "Your Completed Document"

    msg.attach(MIMEText("Your application has been completed. Please find the attached document."))

    # Attach document
    with open(document_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={document_path.split('/')[-1]}",
    )

    msg.attach(part)

    # Send email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, to_email, msg.as_string())
    server.quit()
    
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def send_reset_otp(email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Password Reset OTP"
    msg["From"] = "hetvi5007@gmail.com"
    msg["To"] = email
    msg.set_content(f"Your OTP for password reset is: {otp}")

    # Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("hetvi5007@gmail.com", "cbedkaqjtytrihfw")
        smtp.send_message(msg)

def generate_receipt_pdf(application):
    # HTML receipt rendering
    rendered_html = render_template(
        "pdf_receipt.html",
        app_id=application["app_id"],
        submission_date=application["submission_date"],
        service_name=application["service_name"]
    )
    # Path to wkhtmltopdf
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdf_path = f"static/receipts/{application['app_id']}_receipt.pdf"
    pdfkit.from_string(rendered_html, pdf_path, configuration=config)
    return pdf_path

def send_receipt_email(receiver_email, app_id, pdf_path, service_name):
    sender_email = "hetvi5007@gmail.com"
    sender_password = "cbedkaqjtytrihfw"  # NOT your Gmail password!

    subject = f"Receipt for Your Application ({app_id})"
    body = f"""
    Dear User,

    Thank you for submitting your application for {service_name}.
    Please find attached your official receipt.

    Application ID: {app_id}
    Status: Application
    Service: {service_name}

    Regards,
    Krishi E-Government Services
    """
    # Create MIME message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    with open(pdf_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(pdf_path)}')
    msg.attach(part)

    # Send email via SMTP (Gmail)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# USER GUIDES
guide_details = {
    "how-to-register-service": {
        "title": "How to Create an Account",
        "steps": [
            "Go to the homepage and click on Register.",
            "Enter your personal details such as name, email, phone, and password.",
            "Click Create Account to register.",
            "After successful registration, log in using your new credentials."
        ]
    },
    "how-to-upload-documents": {
        "title": "How to Apply for a Service",
        "steps": [
            "Log in to your dashboard.",
            "Go to the Services page.",
            "Select the service you want to apply for.",
            "Fill in the application form.",
            "Upload all required documents.",
            "Click Submit to complete the application."
        ]
    },
    "how-to-track-application": {
        "title": "How to Track Your Application",
        "steps": [
            "Log in to your account.",
            "Go to Track Page.",
            "View the real-time status of your request: Pending → Processing → Completed."
        ]
    },
    "how-to-download-documents": {
        "title": "How to Download Completed Documents",
        "steps": [
            "Open your dashboard.",
            "Go to My Applications.",
            "Click the Download button for any completed service.",
            "A copy is also sent to your email address."
        ]
    },
    "contact-support": {
        "title": "How to Contact Support",
        "steps": [
            "Go to the Contact page.",
            "Fill out the support form with your issue.",
            "Alternatively, you can email support@krishiservices.in.",
            "Our team will respond within 24–48 hours."
        ]
    },
}

# ADMIN GUIDES
admin_guides = {
    "admin-how-to-login": {
        "title": "How to Access Admin Panel",
        "steps": [
            "Open the Admin Login URL.",
            "Enter admin email & password.",
            "Click Login to access dashboard."
        ]
    },
    "admin-how-to-manage-services": {
        "title": "How Admins Enable / Disable Services",
        "steps": [
            "Open Admin Panel.",
            "Go to Services Management.",
            "Toggle Enable/Disable for each service.",
            "Changes reflect instantly for users."
        ]
    },
    "admin-how-to-verify-applications": {
        "title": "How Admins Verify Applications",
        "steps": [
            "Go to Applications section.",
            "Select a Pending application.",
            "Review submitted data & documents.",
            "Click Verify → Status becomes Processing."
        ]
    },
    "admin-how-to-complete-applications": {
        "title": "How Admins Mark Applications Completed",
        "steps": [
            "Open an application with status Processing.",
            "Upload final verified documents.",
            "Click Mark Completed.",
            "User gets email + download option."
        ]
    },
    "admin-how-to-manage-users": {
        "title": "How Admins Manage Users",
        "steps": [
            "Go to Users section in admin panel.",
            "View all registered users.",
            "Edit or block a user if needed."
        ]
    }
}

# ✅ Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log')
def logout():
    session.clear()
    return render_template('log.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/terms')
@login_required
def terms():
    return render_template('terms.html')

@app.route('/privacy')
@login_required
def privacy():
    return render_template('privacy.html')

@app.route('/faq')
@login_required
def faq():
    return render_template('faq.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        admin_email = "hetvi5007@gmail.com"  # admin email

        # Construct email content
        msg = MIMEText(f"""You have received a query from the Contact Form:

Name: {name} \n
Email: {email} \n
Subject: {subject} \n
Message: {message} \n
        """)

        msg['Subject'] = f"Contact Form query : {subject}"
        msg['From'] = email
        msg['To'] = admin_email

        # Send using SMTP (Gmail example)
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.starttls()
        smtp_server.login("hetvi5007@gmail.com", "jyoibgqmyckxewuz")
        smtp_server.sendmail(email, admin_email, msg.as_string())
        smtp_server.quit()
        flash("Your message has been sent successfully!", "success")
    except Exception as e:
        print("Email error:", e)
        flash("Failed to send your message. Please try again.", "error")

    return redirect(url_for('contact'))

@app.route('/about')
@login_required
def about():
    # Example: decide whether to show the login button in header
    # If user is logged in you might set session['user_id'] somewhere else after login
    show_login = 'user_id' not in session
    return render_template(
        'about.html',
        show_login=show_login,
        page_title="About Us - Krishi E-Government Services"
    )

@app.route("/guides")
def tutorials():
    return render_template("guide.html")

@app.route("/tutorials/<slug>")
def tutorial_detail(slug):
    guide = guide_details.get(slug)
    if not guide:
        return "Guide not found", 404
    return render_template("guides_detail.html", tutorial=guide)

@app.route("/guides/admin")
def admin_guides_page():
    return render_template("admin_guides.html", guides=admin_guides)

@app.route("/guides/admin/<slug>")
def admin_guide_detail(slug):
    guide = admin_guides.get(slug)
    if not guide:
        return "Guide not found", 404
    return render_template("admin_guide.html", guide=guide)

@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")

@app.route("/chatbot/ask", methods=["POST"])
def chatbot_ask():
    data = request.get_json()
    question = data.get("question", "").lower()

    # Simple rule-based responses (can upgrade later)
    responses = {
        "register": "To register, go to the Register page and fill all fields correctly.",
        "apply": "To apply for a service, open Services → Select service → Fill form → Submit.",
        "forget password":"To reset the password go the Login page and click on 'forget password' button",
        "forget the password":"To reset the password go the Login page and click on 'forget password' button",
        "documents": "Upload clear documents in PDF/JPG only. Max size 2MB.",
        "track": "Go to My Applications to track your status or manually track through Track page.",
        "payment": "Payments are securely processed using Razorpay.",
        "hello": "Hello! How can I help you today?",
        "hi": "Hi! Ask me anything.",
    }
    for key in responses:
        if key in question:
            return jsonify({"answer": responses[key]})

    # Default fallback
    return jsonify({"answer": "I’m not sure about that. Please rephrase your question."})

# ✅ Route: register_user
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    confirm_password = request.form['confirm-password']
    if password != confirm_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for('register'))
    hashed_password = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (name, email, phone, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    except Error as e:
        # print("MySQL Error:", e)
        flash(f"An error occurred: {e}", "Enter unique e-mail id")
        return redirect(url_for('register'))

# ✅ Route: login_user
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # ✅ Admin Login (hard-coded for now)
        if email == "admin@gmail.com" and password == "admin":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))

        # ✅ Normal User Login
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            if check_password_hash(user['password'], password):
                session.permanent = True   # ✅ Enable session timeout
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                return render_template('log.html')
            else:
                flash("❌ Incorrect password!", "error")
        else:
            flash("❌ Email not found!", "error")

    return render_template('login.html')

# ✅ Route: forgot_password
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        user_input = request.form.get("identifier")

        # ✅ Step 1: Validate input
        if not user_input or user_input.strip() == "":
            flash("Please enter your email or phone number.", "error")
            return redirect("/forgot_password")

        user_input = user_input.strip()

        # ✅ Step 2: Generate OTP
        otp = str(random.randint(100000, 999999))
        session["reset_otp"] = otp

        # ✅ Step 3: Check if it's email or phone safely
        if "@" in user_input:
            # ----- Email OTP -----
            session["reset_email"] = user_input
            session.pop("reset_phone", None)
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
                    smtp.starttls()
                    smtp.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                    subject = "Your OTP for Password Reset"
                    body = f"Your OTP for resetting password is {otp}"
                    msg = f"Subject: {subject}\n\n{body}"
                    smtp.sendmail(app.config['MAIL_USERNAME'], user_input, msg)
                flash("OTP sent to your email.", "info")
            except Exception as e:
                flash("Failed to send OTP via email: " + str(e), "error")
        else:
            # ----- SMS OTP -----
            if not user_input.startswith("+"):
                user_input = "+91" + user_input 
            session["reset_phone"] = user_input
            session.pop("reset_email", None)
            try:
                client.messages.create(
                    body=f"Your OTP for password reset is {otp}.",
                    from_=TWILIO_PHONE,
                    to=user_input
                )
                flash("OTP sent via SMS.", "info")
            except Exception as e:
                flash("Failed to send OTP via SMS: " + str(e), "error")
        return redirect("/verify_otp")

    return render_template("forgot_password.html")

@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form.get("otp")
        saved_otp = session.get("reset_otp")

        # ✅ Step 1: Check if session exists
        if not saved_otp:
            flash("Session expired! Please request a new OTP.", "error")
            return redirect("/forgot_password")

        # ✅ Step 2: Compare safely (as strings)
        if entered_otp and entered_otp.strip() == str(saved_otp).strip():
            flash("✅ OTP verified successfully! You can now reset your password.", "success")
            return redirect("/reset_password")
        else:
            flash("❌ Invalid OTP! Please try again.", "error")
            return redirect("/verify_otp")

    return render_template("verify_otp.html")

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        password = request.form.get("password")

        if not password or password.strip() == "":
            flash("Password cannot be empty!", "error")
            return redirect("/reset_password")

        hashed_password = generate_password_hash(password)
        email = session.get("reset_email")
        phone = session.get("reset_phone")

        if not email and not phone:
            flash("Session expired! Please request OTP again.", "error")
            return redirect("/forgot_password")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if email:
                cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_password, email))
            elif phone:
                # Normalize phone (optional)
                if phone.startswith("+91"):
                    phone = phone[3:]
                cursor.execute("UPDATE users SET password=%s WHERE phone=%s", (hashed_password, phone))

            conn.commit()
            print("Updated rows:", cursor.rowcount)
            cursor.close()
            conn.close()
            session.pop("reset_email", None)
            session.pop("reset_phone", None)
            session.pop("reset_otp", None)

            if cursor.rowcount > 0:
                flash("Password reset successfully! You can now log in.", "success")
            else:
                flash("No account found for that number or email!", "error")
            return redirect("/login")

        except Exception as e:
            flash("Database error: " + str(e), "error")
            return redirect("/reset_password")

    return render_template("reset_password.html")

# ✅ Route to display all services
@app.route('/services')
@login_required
def services():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM service WHERE is_active = 1")
    services = cur.fetchall()

    if conn is None:
        flash("Database connection failed!", "danger")
        return render_template('services.html', services=[])
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT service_id, title, short_desc, base_price, documents, image FROM service")
        services = cursor.fetchall()
        if not services:
            print("⚠️ No services found in database.")
            flash("No services available at the moment.", "warning")
            services = []
        return render_template('services.html', services=services)
    except Error as err:
        flash("An error occurred while fetching services.", "danger")
        return render_template('services.html', services=[])
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route("/service/<int:id>")
def service_detail(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM service WHERE service_id = %s", (id,))
        service = cursor.fetchone()
        if not service:
            return "Service not found", 404

        # ✅ Convert comma-separated document names into a list
        if service.get("documents"):
            service["documents"] = [doc.strip() for doc in service["documents"].split(",") if doc.strip()]
        else:
            service["documents"] = []
        return render_template("service_detail.html", service=service)
    
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "danger")
        return redirect(url_for("services"))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

UPLOAD_FOLDER = "uploads"   # temporary upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/application_form/<int:id>", methods=["GET", "POST"])
def application_form(id):

    # Fetch the service
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM service WHERE service_id = %s", (id,))
    service = cursor.fetchone()
    #print("RAW DOCUMENT STRING:", repr(service["documents"]))
    cursor.close()
    conn.close()

    if not service:
        return "Service not found", 404

    # Convert "Aadhaar, PAN" → ["Aadhaar", "PAN"]
    if service.get("documents"):
        service["documents"] = [doc.strip() for doc in service["documents"].split(",")]
    else:
        service["documents"] = []

    # --------------- POST HANDLING ----------------
    if request.method == "POST":
        MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
        uploaded_files = {}

        # Loop through each document
        for doc_name in service["documents"]:

            # Checkbox value (on/off)
            checkbox_val = request.form.get(f"{doc_name}_checked")

            # File input
            file = request.files.get(doc_name)

            # Text Box input
            text_value = request.form.get(f"text_{doc_name}", "").strip()

            # CASE A → Checkbox checked → file must be uploaded
            if checkbox_val == "on":
                if not file or file.filename == "":
                    flash(f"Please upload required document: {doc_name}", "danger")
                    return redirect(request.url)

                file_bytes = file.read()
                if len(file_bytes) > MAX_FILE_SIZE:
                    flash(f"{doc_name} must be less than 2MB", "danger")
                    return redirect(request.url)
                file.seek(0)
                filename = secure_filename(f"{doc_name}_{file.filename}")
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                file_saved = filename
                uploaded_files[doc_name] = {
                "text": text_value if text_value else None,
                "file": file_saved
            }
                
            # CASE B → Checkbox not checked → File is optional
            else:
                if file and file.filename != "":
                    file_bytes = file.read()
                    if len(file_bytes) > MAX_FILE_SIZE:
                        flash(f"{doc_name} must be less than 2MB", "danger")
                        return redirect(request.url)
                    file.seek(0)
                    filename = secure_filename(f"{doc_name}_{file.filename}")
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    uploaded_files[doc_name] = filename

        # Save into session
        session["form_data"] = {
            "service_id": id,
            "name": request.form["name"],
            "email": request.form["email"],
            "mobile": request.form["phone"],
            "title": service["title"],
            "amount": service["base_price"],
            "uploaded_files": uploaded_files,
        }
        return redirect(url_for("payment", id=id))

    return render_template("application_form.html", service=service)

@app.route("/payment/<int:id>", methods=["GET", "POST"])
def payment(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM service WHERE service_id = %s", (id,))
    service = cur.fetchone()
    cur.close()
    conn.close()
    if not service:
        return "Service not found", 404
    # Get form data from session
    form_data = session.get("form_data")
    # ✅ If someone visits this page directly without submitting form first
    if not form_data:
        flash("Please fill out the application form first.", "warning")
        return redirect(url_for("application_form", id=id))

    # 🧾 When submit button is clicked (after payment done)
    if request.method == "POST":
        conn = get_db_connection()
        cur = conn.cursor()
        
        conn.commit()
        cur.close()
        conn.close()
        # Remove data from session
        session.pop("form_data", None)
        flash("✅ Application submitted successfully!", "success")
        return redirect(url_for("submit_application"))
    # 🧭 Render payment page
    return render_template("payment.html", service=service)

@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.get_json()
    amount = data.get("amount")  # amount in paise
    client = razorpay.Client(auth=("rzp_test_Rcq1OkhS35AWp9", "ldq5ru7Am3Q19qxjUHhF5w7x"))
    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })
    return jsonify(order)

@app.route('/generate_pdf/<app_id>')
def generate_pdf(app_id):
    # Fetch application data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM application WHERE app_id = %s", (app_id,))
    app_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not app_data:
        return "Application not found", 404

    # Get service name
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT title FROM service WHERE service_id = %s", (app_data['service_id'],))
    service = cur.fetchone()
    cur.close()
    conn.close()

    service_name = service['title'] if service else "Unknown Service"
    submission_date = app_data['created_at']
    
    # ✅ Render the receipt HTML
    rendered_html = render_template(
        'pdf_receipt.html',
        app_id=app_data['app_id'],
        submission_date=submission_date,
        service_name=service_name
    )
    # ✅ Path to wkhtmltopdf (update this to your system path)
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    pdf = pdfkit.from_string(rendered_html, False, configuration=config)

    # ✅ Return as downloadable PDF file
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={app_id}_receipt.pdf'
    return response

@app.route('/submit_application', methods=['GET', 'POST'])
def submit_application():
    form_data = session.get("form_data")
    if not form_data:
        flash("No application data found. Please start again.", "warning")
        return redirect(url_for("services"))

    # generate application ID
    app_id = f"APP-{random.randint(1000, 9999)}"

    # Handle uploaded documents
    temp_folder = "uploads"
    final_folder = "uploads_final"
    os.makedirs(final_folder, exist_ok=True)

    uploaded_files = form_data.get("uploaded_files", {})
    final_files = []
    for doc_name, filename in uploaded_files.items():
        temp_path = os.path.join(temp_folder, filename)

        # new name: APP-3535_Aadhaar_doc.pdf
        new_filename = f"{app_id}_{filename}"
        final_path = os.path.join(final_folder, new_filename)

        if os.path.exists(temp_path):
            os.rename(temp_path, final_path)

        final_files.append(new_filename)

    files_string = " , ".join(final_files)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM service WHERE service_id = %s", (form_data["service_id"],))
    service = cursor.fetchone()

    submission_date = datetime.now().strftime("%d-%m-%Y")
    cursor.execute("""
        INSERT INTO application 
        (app_id, service_id, name, email, mobile, service_name, total_amount, uploaded_files, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", (
        app_id,
        form_data["service_id"],
        form_data["name"],
        form_data["email"],
        form_data["mobile"],
        service["title"],
        service["base_price"],
        files_string,   # store final renamed files
        "Received"
    ))
     # Prepare email content
    msg = Message(
        subject="Application Submitted Successfully – Krishi E-Government Services",
        sender=app.config['MAIL_USERNAME'],
        recipients=[form_data["email"]]
    )
    msg.html = render_template('email_receipt.html', 
                               app_id=app_id, 
                               date=submission_date, 
                               service=service["title"])

    mail.send(msg)
    conn.commit()
    cursor.close()
    conn.close()

    # clear session
    session.pop("form_data", None)

    return render_template(
        'application_submitted.html',
        app_id=app_id,
        submission_date=submission_date,
        service_name=service["title"]
    )

@app.route("/my_applications")
def my_applications():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM application ORDER BY app_id DESC")
    applications = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("my_applications.html", applications=applications)

@app.route('/download/<path:filename>')
def download_document(filename):
    base_dir = os.path.join(app.root_path, 'uploads')
    file_path = os.path.join(base_dir, filename)
    print("Looking for file:", file_path)  # debug
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(base_dir, filename, as_attachment=True)

@app.route('/track', methods=['GET', 'POST'])
def track_application_form():
    application = None
    searched = False

    if request.method == 'POST':
        searched = True
        app_id = request.form.get('app_id')
        application = Application.query.filter_by(app_id=app_id).first()
        if not application:
            flash("Application not found", "danger")
    return render_template('track.html', application=application, searched=searched)

@app.route('/track/<string:app_id>')
def track_application(app_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT app_id, name, email, mobile, service_id, status
            FROM application
            WHERE app_id = %s
            LIMIT 1
        """, (app_id,))
        application = cursor.fetchone()
        cursor.close()
        conn.close()

        if not application:
            flash("No application found with this Application ID.", "warning")
            return redirect(url_for('my_applications'))
        
        return render_template('tracking.html', application=application)

    except Error as e:
        print("Database error:", e)
        flash("An error occurred while fetching application status.", "danger")
        return redirect(url_for('my_applications'))

@app.route('/payment_success', methods=['POST'])
def payment_success():
    data = request.form
    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    # Verify payment with Razorpay (optional but recommended)
    # Using your Razorpay API keys for server-side verification
    client = razorpay.Client(auth=(" rzp_test_RYA0tri2cAfoE8", "FuIi5rksxQoJ294Qg9trERek"))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        return "Payment verification failed", 400

    # ✅ Payment verified successfully, now update database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        UPDATE application 
        SET payment_status = %s, razorpay_payment_id = %s, status = %s 
        WHERE razorpay_order_id = %s
    """, ('Paid', razorpay_payment_id, 'Submitted', razorpay_order_id))

    conn.commit()
    cursor.close()
    conn.close()

    # Generate receipt PDF
    pdf_path = generate_receipt_pdf(application)

    # ✅ Send receipt to user's email
    send_receipt_email(
        receiver_email=application['email'],
        app_id=application['app_id'],
        pdf_path=pdf_path,
        service_name=application['service_name']
    )

    # ✅ Fetch the updated application record
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM application WHERE razorpay_order_id = %s", (razorpay_order_id,))
    application = cursor.fetchone()
    cursor.close()
    conn.close()

    # Store app_id in session and redirect to submission page
    session['last_app_id'] = application['app_id']

    # Redirect user to success/receipt page
    return redirect(url_for('application_submitted'))

if __name__ == "__main__":
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gov_services"
        )
        cursor = con.cursor()
        # ✅ Check if the service table already has rows
        cursor.execute("SELECT COUNT(*) FROM service")
        count = cursor.fetchone()[0]
    except mysql.connector.Error as err:
        print(f"❌ MySQL error: {err}")
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
            print("🔒 Database connection closed.")
    
    app.run(debug=True)