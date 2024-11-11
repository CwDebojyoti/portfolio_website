from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, DateField, validators, BooleanField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


class NewEducation(FlaskForm):
    exam = StringField('Qualification', validators= [DataRequired()])
    institute = StringField('Name of the Institution', validators= [DataRequired()])
    university = StringField('Board/University', validators=[DataRequired()])
    year = StringField('Starting and Passing Year', validators=[DataRequired()])
    marks = StringField('Marks Obtained', validators=[DataRequired()])
    description = CKEditorField('Description',validators=[DataRequired()])
    submit = SubmitField('Save')


class NewExperience(FlaskForm):
    company = StringField('Name of the Organization', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    starting_date = DateField('Joining Date', validators=[DataRequired()])
    exit_date = DateField('Exit Date', validators=[validators.Optional()])
    present = BooleanField('Currently Present')
    job_description = CKEditorField('Job Description',validators=[DataRequired()])
    submit = SubmitField('Save')


class NewProject(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    category = SelectField('Subject', choices=['Data_Analytics', 'Data_Science', 'Web_Development', 'Python_Development'], validators=[DataRequired()])
    image = StringField("Thumbnail URL", validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])
    submit = SubmitField('Save')


class NewCertificate(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    image = StringField("Image of the Certificate", validators=[DataRequired()])
    submit = SubmitField('Save')


class RegisterForm(FlaskForm):
    name = StringField('User Name', validators=[DataRequired()])
    email = StringField('Enter Email', validators=[DataRequired()])
    password = PasswordField('Choose Password:', validators=[DataRequired()])
    submit = SubmitField('Register')



class LoginForm(FlaskForm):
    email = StringField('Enter Email', validators=[DataRequired()])
    password = PasswordField('Enter Password:', validators=[DataRequired()])
    submit = SubmitField('LogIn')