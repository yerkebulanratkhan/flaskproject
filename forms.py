from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_login import current_user
from models import *
from wtforms.validators import ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[InputRequired(), Email(message='Invalid email'), Length(min=4, max=60)])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=4, max=15)])
    remember = BooleanField('Remember me')
class RegisterForm(FlaskForm):
    email = StringField('Email:', validators=[InputRequired(), Email(message='Invalid email'), Length(max=60)])
    name = StringField('Name:', validators=[InputRequired(), Length(min=4, max=30)])
    surname = StringField('Surname:', validators=[InputRequired(), Length(min=4, max=40)])
    phone = StringField('Phone:', validators=[InputRequired(), Length(min=4, max=20)])
    salary = IntegerField('Salary:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=4, max=15)])
    cname = SelectField('Country:')
    def __init__(self):
        super(RegisterForm, self).__init__()
        self.cname.choices = [(c.cname) for c in Country.query.all()]
class FinishRegisterForm(FlaskForm):
    isdoctor = BooleanField('Are you doctor:')
    degree = StringField('Degree:', validators=[InputRequired(), Length(min=4, max=20)])
    ispublicservant = BooleanField('Are you public servant?')
    department = StringField('Department:', validators=[InputRequired(), Length(min=4, max=50)])
class FinishRegisterPublicServant(FlaskForm):
    department = StringField('Department:', validators=[InputRequired(), Length(min=4, max=50)])
class FinishRegisterDoctor(FlaskForm):
    degree = StringField('Degree:', validators=[InputRequired(), Length(min=1, max=20)])
class RecordForm(FlaskForm):
    email = StringField('Email:', validators=[InputRequired(), Email(message='Invalid email'), Length(min=4, max=60)])
    disease_code = SelectField()
    total_deathcount = IntegerField('Total deathcount:', validators=[InputRequired()])
    total_patients = IntegerField('Total patients:', validators=[InputRequired()])
    cname = SelectField()
    def __init__(self):
        super(RecordForm, self).__init__()
        self.cname.choices = [(c.cname) for c in Country.query.all()]
        self.disease_code.choices = [(c.disease_code) for c in Disease.query.all()]
class DiscoveryForm(FlaskForm):
    cname = SelectField('Country: ')
    first_enc_date = DateField('First enc date: ', validators=[InputRequired()])
    disease_code = SelectField('Disease code: ')
    def __init__(self):
        super(DiscoveryForm, self).__init__()
        self.cname.choices = [(c.cname) for c in Country.query.all()]
        self.disease_code.choices = [(c.disease_code) for c in Disease.query.all()]
class DiseaseTypeForm(FlaskForm):
    id = IntegerField('id', validators=[InputRequired()])
    description = StringField('Description:', validators=[InputRequired(), Length(min=2, max=140)])
class DiseaseForm(FlaskForm):
    disease_code = StringField('Disease code:', validators=[InputRequired(), Length(min=2, max=50)])
    pathogen = StringField('Pathogen:', validators=[InputRequired(), Length(min=2, max=20)])
    description = StringField('Description:', validators=[InputRequired(), Length(min=2, max=140)])
    id = SelectField('Disease type')
    def __init__(self):
        super(DiseaseForm, self).__init__()
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        self.id.choices = [(c.id, c.description) for c in
                           db.session.query(DiseaseType).filter(DiseaseType.id.in_(spec_id)).all()]
class AddSpecializationForm(FlaskForm):
    id = SelectField('Disease type')
    def __init__(self):
        super(AddSpecializationForm, self).__init__()
        cur_spec = db.session.query(Specialize).filter_by(email=current_user.email).all()
        spec_id = []
        for i in cur_spec:
            spec_id.append(i.id)
        self.id.choices = [(c.id, c.description) for c in
                           db.session.query(DiseaseType).filter(DiseaseType.id.not_in(spec_id)).all()]

class DiscoverQuery(FlaskForm):
    disease_code = SelectField('Disease code')
    cname = SelectField('Country')
    def __init__(self):
        super(DiscoverQuery, self).__init__()
        self.disease_code.choices=[]
        self.disease_code.choices.append("ANY")
        self.disease_code.choices += [(c.disease_code) for c in Disease.query.all()]
        self.cname.choices = []
        self.cname.choices.append("ANY")
        self.cname.choices += [(c.cname) for c in db.session.query(Country).all()]

class DateBetween(FlaskForm):
    startdate = DateField('From Date')
    enddate = DateField('To Date')

    def validate_on_submit(self):
        result = super(DateBetween, self).validate()
        if (self.startdate.data > self.enddate.data):
            return False
        else:
            return True
    def checkstart(self):
        print(self.startdate)
        if self.startdate.data is not None:
            print("true")
            return True
        else:
            print("false")
            return False

    def checkend(self):
        print(self.enddate)
        if self.enddate.data is not None:
            print("true")
            return True
        else:
            print("false")
            return False