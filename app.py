from MySQLdb import MySQLError
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
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
import mysql.connector, random, string, json, os, uuid, smtplib, MySQLdb.cursors, razorpay, warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")  # change in prod
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/gov_services'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


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
    razorpay_order_id = db.Column(db.String(200), nullable=True)
    razorpay_payment_id = db.Column(db.String(200), nullable=True)
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
            INSERT INTO application (app_id, service_id, name, email, mobile, service_name, total_amount, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            app_id,
            form_data["service_id"],
            form_data["name"],
            form_data["email"],
            form_data["mobile"],
            form_data["title"],
            form_data["total_amount"],
            "Completed"
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

    return render_template(
        'application_submitted.html',
        app_id=app_id,
        submission_date=submission_date,
        service_name=service_name
    )

@app.route('/track', methods=['GET','POST'])
def track():
    app_info = None
    if request.method == 'POST':
        app_id = request.form.get('app_id')
        app_info = Application.query.filter_by(app_id=app_id).first()
        if not app_info:
            flash("Application not found", "danger")
    return render_template('track.html', app_info=app_info)


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