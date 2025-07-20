from flask import Flask, render_template, redirect, url_for, request, jsonify, flash, send_from_directory
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from hashlib import md5
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Date, Float, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from dateutil.relativedelta import relativedelta
from functools import wraps
from flask import abort
from forms import NewEducation, NewExperience, NewProject, NewCertificate, LoginForm, RegisterForm, NewTools
import smtplib
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APP_SEC_KEY")
Bootstrap5(app)
ckeditor = CKEditor(app)


# Creating and initiating Login manager for Flask login:
login_manager = LoginManager()
login_manager.init_app(app)



# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ubuntu@localhost/portfolio'
db = SQLAlchemy(model_class=Base)
db.init_app(app)




class Education(db.Model):
    __tablename__ = "education"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    institute: Mapped[str] = mapped_column(String(250), nullable=False)
    university: Mapped[str] = mapped_column(String(250), nullable=False)
    year: Mapped[str] = mapped_column(String(100), nullable=False)
    marks: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


class Experience(db.Model):
    __tablename__ = "experience"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    position: Mapped[str] = mapped_column(String(250), nullable=False)
    joining_date = mapped_column(Date, nullable=False)
    exit_date = mapped_column(Date, nullable=True)
    present = mapped_column(Boolean, default=False)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    

class Project(db.Model):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    title: Mapped[str] = mapped_column(String(250), unique= True, nullable= False)
    category: Mapped[str] = mapped_column(String(250), nullable= False)
    image: Mapped[str] = mapped_column(String(250), nullable= False)
    description: Mapped[str] = mapped_column(Text, nullable= False)



class Certificate(db.Model):
    __tablename__ = "certificate"
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    title: Mapped[str] = mapped_column(String(250), unique= True, nullable= False)
    image: Mapped[str] = mapped_column(String(250), nullable= False)


class Tools(db.Model):
    __tablename__ = "tools"
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    title: Mapped[str] = mapped_column(String(250), unique= True, nullable= False)
    image: Mapped[str] = mapped_column(String(250), nullable= False)
    

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)



@app.route("/")
def home():

    start_date = date(2018, 4, 1)  # Change to your real start date
    today = date.today()
    
    delta = relativedelta(today, start_date)
    experience_duration = f"{delta.years} Years & {delta.months} Months"

    edu_result = db.session.execute(db.select(Education).order_by(Education.id.desc()))
    all_qualification = edu_result.scalars().all()
    exp_result = db.session.execute(db.select(Experience).order_by(Experience.id.desc()))
    all_experience = exp_result.scalars().all()
    pro_result = db.session.execute(db.select(Project))
    all_project = pro_result.scalars().all()
    cert_result = db.session.execute(db.select(Certificate))
    all_certificates = cert_result.scalars().all()
    tools_result = db.session.execute(db.select(Tools))
    all_tools = tools_result.scalars().all()
    return render_template("index.html", qualifications = all_qualification, experiences = all_experience, projects = all_project, certificates = all_certificates, tools = all_tools, experience_duration=experience_duration, logged_in = current_user.is_authenticated)



# @app.route("/<int:project_id>", methods = ['GET', 'POST'])
# def project(project_id):
#     requested_project = db.get_or_404(Project, project_id)

#     return render_template("project.html", projects = requested_project, logged_in = current_user.is_authenticated)



@app.route("/project_details/<int:project_id>")
def project(project_id):
    requested_project = db.get_or_404(Project, project_id)

    # Convert project title into a valid filename (replace spaces with underscores)
    doc_filename = requested_project.title.replace(" ", "_") + ".pdf"
    doc_path = f"static/docs/{doc_filename}"

    if os.path.exists(doc_path):
        # Get absolute URL of the file
        file_url = f"{request.host_url}{doc_path}"
        return jsonify({"file_url": file_url})
    
    return jsonify({"error": "Project document not found"}), 404



@app.route("/update-education", methods = ['GET', 'POST'])
def update_education():
    new_education = NewEducation()
    
    if new_education.validate_on_submit():
        new_qualification = Education(
            exam = new_education.exam.data,
            institute = new_education.institute.data,
            university = new_education.university.data,
            year =new_education.year.data,
            marks = new_education.marks.data,
            description = new_education.description.data
        )

        db.session.add(new_qualification)
        db.session.commit()

    return render_template('update_education.html', form = new_education, logged_in = current_user.is_authenticated)



@app.route("/update-experience", methods = ['GET', 'POST'])
def update_experience():
    new_experience = NewExperience()

    if new_experience.validate_on_submit():

        if new_experience.present.data: 
            exit_date_value = None 
        else: 
            exit_date_value = new_experience.exit_date.data

        new_organization = Experience(
            company = new_experience.company.data,
            position = new_experience.position.data,
            joining_date = new_experience.starting_date.data,
            exit_date = exit_date_value,
            job_description = new_experience.job_description.data
        )

        db.session.add(new_organization)
        db.session.commit()

    return render_template('update_experience.html', form = new_experience, logged_in = current_user.is_authenticated)



@app.route("/update-portfolio", methods = ['GET', 'POST'])
def update_portfolio():

    new_portfolio = NewProject()

    if new_portfolio.validate_on_submit():
        new_project = Project(
            title = new_portfolio.title.data,
            category = new_portfolio.category.data,
            image = new_portfolio.image.data,
            description = new_portfolio.description.data
        )

        db.session.add(new_project)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template('update_portfolio.html', form = new_portfolio, logged_in = current_user.is_authenticated)



@app.route("/update-certificate", methods = ['GET', 'POST'])
def update_certificate():
    new_certificate = NewCertificate()

    if new_certificate.validate_on_submit():
        new_cert = Certificate(
            title = new_certificate.title.data,
            image = new_certificate.image.data
        )

        db.session.add(new_cert)
        db.session.commit()

    return render_template('update_certificate.html', form = new_certificate, logged_in = current_user.is_authenticated)


@app.route("/edit-certificates")
def edit_certificates():
    certificates = Certificate.query.all()
    return render_template("edit_certificates.html", certificates=certificates)


@app.route("/save-certificate-edits", methods=["POST"])
def save_certificate_edits():
    certificates = Certificate.query.all()
    for cert in certificates:
        new_title = request.form.get(f"title_{cert.id}")
        new_image = request.form.get(f"image_{cert.id}")
        if new_title and new_image:
            cert.title = new_title
            cert.image = new_image
    db.session.commit()
    return redirect(url_for("home"))




@app.route("/update-tools", methods = ['GET', 'POST'])
def update_tools():
    new_tools = NewTools()

    if new_tools.validate_on_submit():
        new_tool = Tools(
            title = new_tools.title.data,
            image = new_tools.image.data
        )

        db.session.add(new_tool)
        db.session.commit()

    return render_template('update_tools.html', form = new_tools, logged_in = current_user.is_authenticated)



@app.route("/edit-tools")
def edit_tools():
    all_tools = Tools.query.all()
    return render_template("edit_tools.html", tools=all_tools)


@app.route("/save-tool-edits", methods=["POST"])
def save_tool_edits():
    tools = Tools.query.all()
    for tool in tools:
        new_title = request.form.get(f"title_{tool.id}")
        new_image = request.form.get(f"image_{tool.id}")
        if new_title and new_image:
            tool.title = new_title
            tool.image = new_image
    db.session.commit()
    return redirect(url_for("home"))



@app.route("/edit-project/<int:project_id>", methods = ['GET', 'POST'])
def edit_project(project_id):
    project_to_edit = db.get_or_404(Project, project_id)

    edit_project_form = NewProject(
        title = project_to_edit.title,
        category = project_to_edit.category,
        image = project_to_edit.image,
        description = project_to_edit.description
    )

    if edit_project_form.validate_on_submit():
        project_to_edit.title = edit_project_form.title.data
        project_to_edit.category = edit_project_form.category.data
        project_to_edit.image = edit_project_form.image.data
        project_to_edit.description = edit_project_form.description.data

        db.session.commit()

        return redirect(url_for("project", project_id = project_id))
    
    return render_template('update_portfolio.html', form = edit_project_form, logged_in = current_user.is_authenticated)



@app.route("/edit-experience/<int:experience_id>", methods = ['GET', 'POST'])
def edit_experience(experience_id):
    experience_to_edit = db.get_or_404(Experience, experience_id)

    edit_exp_form = NewExperience(
        company = experience_to_edit.company,
        position = experience_to_edit.position,
        starting_date = experience_to_edit.joining_date,
        exit_date = experience_to_edit.exit_date,
        present = experience_to_edit.present,
        job_description = experience_to_edit.job_description
    )

    if edit_exp_form.validate_on_submit():
        experience_to_edit.company = edit_exp_form.company.data
        experience_to_edit.position = edit_exp_form.position.data
        experience_to_edit.joining_date = edit_exp_form.starting_date.data
        experience_to_edit.exit_date = edit_exp_form.exit_date.data
        experience_to_edit.present = edit_exp_form.present.data
        experience_to_edit.job_description = edit_exp_form.job_description.data


        db.session.commit()

        return redirect(url_for("home", experience_id = experience_id))
    
    return render_template('update_experience.html', form = edit_exp_form, logged_in = current_user.is_authenticated)



@app.route("/contact", methods = ["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        name = data["name"]
        user_email = data["email"]
        subject = data["subject"]
        message = data["message"]
        send_message(name, user_email, subject, message)
        flash('Message sent successfully!', 'success')
        return redirect(url_for('home') + '#contact')
        
    return render_template("index.html")
    

# Email and Password for SMTPLIB:
my_email = "cwdebojyoti@gmail.com"
password = os.environ.get("SMTP_PASS")

def send_message(name, user_email, subject, message):
    msg_content = f"Name: {name}\nemail: {user_email}\nSubject: {subject}\nMessage: {message}"
    connection = smtplib.SMTP("smtp.gmail.com", 587)
    connection.starttls()
    connection.login(user= my_email, password= password)
    connection.sendmail(from_addr= my_email, 
                            to_addrs= "debojyotichattoraj1996@gmail.com", 
                            msg= f"Subject: New User Information!\n\n {msg_content}")
    connection.close()



@app.route('/register', methods = ['GET', 'POST'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user_to_add = result.scalar()
        if user_to_add:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        else:
            new_user = User(
                name = register_form.name.data,
                email = register_form.email.data,
                password = generate_password_hash(register_form.password.data, method= 'pbkdf2:sha256', salt_length= 8)
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("home"))
        
    return render_template("register.html", form = register_form)



@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user_to_login = result.scalar()
        if not user_to_login:
            flash("This email does not exist!")
            return redirect(url_for('login'))
        elif not check_password_hash(user_to_login.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user_to_login)
            return redirect(url_for('home'))
        
    return render_template("login.html", form = login_form, logged_in = current_user.is_authenticated)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))




if __name__ == "__main__":
    app.run(debug=True, port=8001)

