from MySQLdb import MySQLError
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify, send_file, make_response
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON
from email.message import EmailMessage
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask_mail import Mail, Message
from twilio.rest import Client
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io, os, pdfkit
import mysql.connector, random, string, json, os, uuid, smtplib, MySQLdb.cursors, razorpay, warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")  # change in prod
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/gov_services'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Flask Mail Connection
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='hetvi5007@gmail.com',
    MAIL_PASSWORD='Malti@213'  # Use Google App Password
)
mail = Mail(app)


# ✅ Initialize SQLAlchemy
db = SQLAlchemy(app)

# Razorpay client (use test keys first)
razorpay_client = razorpay.Client(auth=("rzp_test_RYA0tri2cAfoE8", "FuIi5rksxQoJ294Qg9trERek"))

# ✅ Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        # replace with your MySQL username
        password="root",  # replace with your MySQL password
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
    status = db.Column(db.String(50), default="Submitted")
    #razorpay_order_id = db.Column(db.String(200), nullable=True)
    #razorpay_payment_id = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ApplicationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    selected_documents = db.Column(JSON)  # list of selected doc names
    item_amount = db.Column(db.Numeric(10,2))


# ✅ Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log')
def logout():
    return render_template('log.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    # Example: decide whether to show the login button in header
    # If user is logged in you might set session['user_id'] somewhere else after login
    show_login = 'user_id' not in session
    return render_template(
        'about.html',
        show_login=show_login,
        page_title="About Us - Krishi E-Government Services"
    )

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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            if check_password_hash(user['password'], password):
                #flash(f"✅ Login Successful! Welcome, {user['name']}.", "success")
                return redirect(url_for('logout'))
            else:
                flash("❌ Incorrect password!", "error")
        else:
            flash("❌ Email not found!", "error")
    return render_template('login.html')

# ✅ Route: forgot_password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            # Generate temporary password or reset token
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            hashed_temp_password = generate_password_hash(temp_password)
            # Update password in DB (temporary)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_temp_password, email))
            conn.commit()
            conn.close()
            # Send email to user (simplest SMTP example)
            try:
                msg = EmailMessage()
                msg.set_content(f"Your temporary password is: {temp_password}\nPlease login and change it immediately.")
                msg['Subject'] = 'Reset Your Password'
                msg['From'] = 'hetvi5007@gmail.com'
                msg['To'] = email

                # Replace SMTP settings with your email provider
                with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                    smtp.starttls()
                    smtp.login('hetvi5007@gmail.com', 'Malti@213')
                    smtp.send_message(msg)
                flash("A temporary password has been sent to your email.", "success")
            except Exception as e:
                flash(f"Failed to send email: {e}", "error")
        else:
            flash("Email not found!", "error")
    return render_template('forgot_password.html')


# ✅ Route to display all services
@app.route('/services')
def services():
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed!", "danger")
        return render_template('services.html', services=[])
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, title, short_desc, base_price, documents, image FROM service")
        services = cursor.fetchall()
        if not services:
            print("⚠️ No services found in database.")
            flash("No services available at the moment.", "warning")
            services = []
        return render_template('services.html', services=services)
    except Error as err:
        print(f"❌ MySQL error: {err}")
        flash("An error occurred while fetching services.", "danger")
        return render_template('services.html', services=[])
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("🔒 Database connection closed.")

@app.route("/service/<int:id>")
def service_detail(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM service WHERE id = %s", (id,))
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

@app.route('/send_message', methods=['POST'])
def send_message():
    # You can handle form data here (store in DB or send email)
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']
    # Example: flash message or redirect
    flash("Your message has been sent successfully!", "success")
    return redirect(url_for('home'))

# Function to generate unique Application ID
def generate_app_id():
    """Generate unique application ID like APP-4721"""
    return f"APP-{random.randint(1000, 9999)}"


@app.route("/application_form/<int:id>", methods=["GET", "POST"])
def application_form(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM service WHERE id = %s", (id,))
    service = cur.fetchone()
    cur.close()
    conn.close()

    if not service:
        return "Service not found", 404

    # Split document list
    if service.get("documents"):
        service["documents"] = [doc.strip() for doc in service["documents"].split(",") if doc.strip()]
    else:
        service["documents"] = []

    if request.method == "POST":
        # Temporarily store form details in session
        session["form_data"] = {
            "service_id": id,
            "name": request.form["name"],
            "email": request.form["email"],
            "mobile": request.form["phone"],
            "title": service["title"],
            "total_amount": service["base_price"]
            
        }
        app_id = generate_app_id()  # Generate unique ID here
        return redirect(url_for("payment", id=id))

    return render_template("application_form.html", service=service)

@app.route("/payment/<int:id>", methods=["GET", "POST"])
def payment(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM service WHERE id = %s", (id,))
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
        return redirect(url_for("my_applications"))
    # 🧭 Render payment page
    return render_template("payment.html", service=service)


@app.route("/my_applications")
def my_applications():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM application ORDER BY id DESC")
    applications = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("my_applications.html", applications=applications)

@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.get_json()
    amount = data.get("amount")  # amount in paise
    client = razorpay.Client(auth=("rzp_test_RYA0tri2cAfoE8", "FuIi5rksxQoJ294Qg9trERek"))
    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })
    return jsonify(order)

@app.route('/track', methods=['GET','POST'])
def track_application_form():
    app_info = None
    if request.method == 'POST':
        app_id = request.form.get('app_id')
        app_info = Application.query.filter_by(app_id=app_id).first()
        if not app_info:
            flash("Application not found", "danger")
    return render_template('track.html', app_info=app_info)

@app.route('/track/<string:app_id>')
def track_application(app_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT app_id, name, email, phone, service_id, status
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



# ----------------------- WhatsApp Sender ----------------------------
def send_whatsapp_receipt(application):
    # Twilio credentials (use environment variables for security)
    account_sid = "AC5b329f9457b1a375174144626bd26a1d"
    auth_token = "9c4476ce607f88bbc2a732fb1af3043a"
    whatsapp_from = "whatsapp:+12173946575"  # Twilio sandbox number

    client = Client(account_sid, auth_token)

    # Public URL where PDF is hosted (e.g., if deployed)
    pdf_link = f"https://your-domain.com/static/receipts/{application['app_id']}.pdf"

    message_body = (
        f"Hello {application['name']},\n\n"
        f"✅ Your application has been submitted successfully!\n"
        f"📄 Application ID: {application['app_id']}\n"
        f"💼 Service: {application['service_name']}\n"
        f"💰 Amount Paid: ₹{application['total_amount']}\n\n"
        f"You can download your receipt here:\n{pdf_link}\n\n"
        f"Thank you for using Krishi E-Government Services!"
    )
    user_number = str(application['mobile']).strip()
    if not user_number.startswith('+91'):
        user_number = '+91' + user_number

    client.messages.create(
        from_=whatsapp_from,
        body=message_body,
        to=f"whatsapp:+91{application['mobile']}"
    )


'''
# ----------------------- PDF Generation ----------------------------
def generate_receipt_pdf(application):
    pdf_path = f"static/receipts/{application['app_id']}.pdf"
    os.makedirs("static/receipts", exist_ok=True)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "Application Receipt")

    c.setFont("Helvetica", 12)
    c.drawString(100, 760, f"Application ID: {application['app_id']}")
    c.drawString(100, 740, f"Name: {application['name']}")
    c.drawString(100, 720, f"Email: {application['email']}")
    c.drawString(100, 700, f"Mobile: {application['mobile']}")
    c.drawString(100, 680, f"Service: {application['service_name']}")
    c.drawString(100, 660, f"Total Amount: ₹{application['total_amount']}")
    c.drawString(100, 640, f"Status: {application['status']}")
    c.save()

    return pdf_path

# ----------------------- Submit Application Route -------------------
@app.route('/submit_application', methods=['POST'])
def submit_application():
    service_id = request.form.get('service_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM service WHERE id = %s", (service_id,))
    service = cursor.fetchone()
    if not service:
        # Handle missing service safely
        return "Service not found", 404
    form_data = session.get("form_data")
    app_id = generate_app_id()
    submission_date = datetime.now().strftime("%d-%m-%Y")
    service_name = service["title"] if service else "Unknown Service"

    cursor.execute("""
            INSERT INTO application (app_id, service_id, name, email, mobile, service_name, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            app_id,
            form_data["service_id"],
            form_data["name"],
            form_data["email"],
            form_data["mobile"],
            form_data["title"],
            form_data["total_amount"],
            "Submitted"
        ))
    
    conn.commit()

    cursor.execute("SELECT * FROM application ORDER BY id DESC LIMIT 1")
    application = cursor.fetchone()

    cursor.close()
    conn.close()

     # Generate PDF and send WhatsApp
    pdf_path = generate_receipt_pdf(application)
    #send_whatsapp_receipt(application)

    return render_template(
        'application_submitted.html',
        app_id=app_id,
        submission_date=submission_date,
        service_name=service_name
    )

    '''
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


def generate_app_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM application")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return f"APP-{1000 + count + 1}"

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


# ---------- Submit Application ----------
@app.route('/submit_application', methods=['POST'])
def submit_application():
    service_id = request.form.get('service_id')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM service WHERE id = %s", (service_id,))
    service = cursor.fetchone()
    if not service:
        # Handle missing service safely
        return "Service not found", 404
    form_data = session.get("form_data")
    app_id = generate_app_id()
    submission_date = datetime.now().strftime("%d-%m-%Y")
    service_name = service["title"] if service else "Unknown Service"

    cursor.execute("""
            INSERT INTO application (app_id, service_id, name, email, mobile, service_name, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            app_id,
            form_data["service_id"],
            form_data["name"],
            form_data["email"],
            form_data["mobile"],
            form_data["title"],
            form_data["total_amount"],
            "Submitted"
        ))
    
    conn.commit()

    cursor.execute("SELECT * FROM application ORDER BY id DESC LIMIT 1")
    application = cursor.fetchone()

    cursor.close()
    conn.close()

     # Generate PDF and send WhatsApp
    pdf_path = generate_receipt_pdf(application)
    #send_whatsapp_receipt(application)

    return render_template(
        'application_submitted.html',
        app_id=app_id,
        submission_date=submission_date,
        service_name=service_name
    )

# ---------- Application Submitted ----------
@app.route('/application_submitted/<int:app_id>')
def application_submitted(app_id):
    app_id = session.get('last_app_id')
    if not app_id:
        return redirect(url_for('services'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM application WHERE app_id = %s", (app_id,))
    app_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not app_data:
        return "Application not found", 404
    return render_template('application_submitted.html', app_id=app_id)

'''
@app.route('/application_submitted')
def application_submitted():
    app_id = session.get('last_app_id')
    if not app_id:
        return redirect(url_for('services'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM application WHERE app_id = %s", (app_id,))
    app_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not app_data:
        return "Application not found", 404

    return render_template(
        'application_submitted.html',
        app_id=app_data['app_id'],
        submission_date=app_data['submission_date'],
        service_name=app_data['service_name']
    )
'''

@app.route('/payment_success', methods=['POST'])
def payment_success():
    data = request.form

    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    # Verify payment with Razorpay (optional but recommended)
    # Using your Razorpay API keys for server-side verification
    import razorpay
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
    cur.execute("SELECT title FROM service WHERE id = %s", (app_data['service_id'],))
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

    # ✅ Correct variable: use `rendered_html`, not `html_content`
    pdf = pdfkit.from_string(rendered_html, False, configuration=config)

    # ✅ Return as downloadable PDF file
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={app_id}_receipt.pdf'
    return response




if __name__ == "__main__":
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="gov_services"
        )
        cursor = conn.cursor()
        # ✅ Check if the service table already has rows
        cursor.execute("SELECT COUNT(*) FROM service")
        count = cursor.fetchone()[0]
    except mysql.connector.Error as err:
        print(f"❌ MySQL error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("🔒 Database connection closed.")
    
    app.run(debug=True)