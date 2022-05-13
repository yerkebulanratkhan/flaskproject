from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField, DateField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import *
from forms import *
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://yerkebulanratkhan:msn10911@localhost:5432/yerkebulanratkhan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:msn10911@localhost:3306/db'
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://yerkebulanratkha:msn10911@yerkebulanratkhan.mysql.pythonanywhere-services.com/yerkebulanratkha$db"
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)

@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(email=form.email.data).first()
        #user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if user.password==form.password.data:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
            else:
                flash("Password is incorrect", "error")
                return redirect(url_for('index'))
        flash("There is no account with such email", "error")
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    #print(form.email.data)
    form2=FinishRegisterPublicServant()
    form3=FinishRegisterDoctor()
    if form.validate_on_submit():
        #hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = Users(email=form.email.data, name=form.name.data,surname=form.surname.data, password=form.password.data, phone=form.phone.data, salary=form.salary.data, cname=form.cname.data)
        q=db.session.query(Users).filter_by(email=form.email.data).first()
        if q is not None:
            flash("Account with such email already exists", "error")
            return redirect(url_for('signup'))
        db.session.add(new_user)
        db.session.commit()
        user = db.session.query(Users).filter_by(email=new_user.email).first()
        login_user(user)
        return render_template('finish_signup_new.html', form2 =form2, form3=form3)
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/updatestatus',methods=['GET', 'POST'])
@login_required
def updatestatus():
    form = FinishRegisterForm()
    if form.isdoctor.data==True:
        degree=form.degree.data
        new_user = Doctor(email=current_user.email, degree=degree)
        db.session.add(new_user)
        db.session.commit()
    if form.ispublicservant.data==True:
        department=form.department.data
        new_user2 = PublicServant(email=current_user.email, department=department)
        db.session.add(new_user2)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/updatestatusps',methods=['GET', 'POST'])
@login_required
def updatestatusps():
    form = FinishRegisterPublicServant()
    dep = form.department.data
    new_user = PublicServant(email=current_user.email, department=dep)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/updatestatusd',methods=['GET', 'POST'])
@login_required
def updatestatuspd():
    form = FinishRegisterDoctor()
    degree = form.degree.data
    new_user = Doctor(email=current_user.email, degree=degree)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/updatestatusno',methods=['GET', 'POST'])
@login_required
def updatestatusno():
    return redirect(url_for('dashboard'))

@app.route('/record')
def record():
   #u=PublicServant.query.filter_by(email=current_user.email).first()
    u=db.session.query(PublicServant).filter_by(email=current_user.email).first()
    if u is not None:
        return render_template('add_record.html', form=RecordForm())
    flash("You have no access to add records", "error")
    return render_template('add_record_noaccess.html')

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    form=RecordForm()
    if form.total_deathcount.data>form.total_patients.data:
        flash("Number of patients could not be less than total deaths", "error")
        return render_template('add_record.html', form=form)
    new_user=Record(email=current_user.email,total_deaths=form.total_deathcount.data,total_patients=form.total_patients.data,cname=form.cname.data,disease_code=form.disease_code.data)
    db.session.add(new_user)
    db.session.commit()
    flash("Record successfully added", "success")
    return redirect(url_for('records'))

@app.route('/specialize')
@login_required
def specialize():
    #u = Doctor.query.filter_by(email=current_user.email).first()
    u = db.session.query(Doctor).filter_by(email=current_user.email).first()
    if u is not None:
        return render_template('specialize.html', name=current_user.name, query=db.session.query(DiseaseType).all())
    flash("Only doctors can approve their specialization", "error")
    return render_template('dashboard.html', name=current_user.name)

@app.route('/approve_specialization',methods=['GET', 'POST'])
@login_required
def approve_specialization():
    form=AddSpecializationForm()
    new_spec = Specialize(email=current_user.email, id=form.id.data)
    if form.id.data is None:
        flash("You are already specialized in all disease types!", "success")
        return redirect(url_for('profile'))
    db.session.add(new_spec)
    db.session.commit()
    flash("You added new specialization", "success")
    return redirect(url_for('profile'))

@app.route('/discovery')
@login_required
def discovery():
    #u = Doctor.query.filter_by(email=current_user.email).first()
    #i = PublicServant.query.filter_by(email=current_user.email).first()
    u = db.session.query(Doctor).filter_by(email=current_user.email).first()
    i = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    if u is not None or i is not None:
        return render_template('discovery.html', name=current_user.name, form=DiscoveryForm())
    flash("Only public servant or doctors can add discovery", "error")
    return render_template('discovery_noaccess.html')

@app.route('/add_discovery',methods=['GET', 'POST'])
@login_required
def add_discovery():
    form=DiscoveryForm()
    new_disc = Discovery(disease_code=form.disease_code.data, cname=form.cname.data, first_enc_date=form.first_enc_date.data.strftime('%Y-%m-%d'))
    db.session.add(new_disc)
    db.session.commit()
    flash("Successfully added!", "success")
    return render_template('all_discovery.html')

@app.route('/all_discovery')
def discover():
    return render_template('all_discovery.html', name=current_user.name, query=db.session.query(Discovery).all(), d=Disease)

@app.route('/diseasetypes')
def diseasetypes():
    return render_template('diseasetypes.html', name=current_user.name, query=db.session.query(DiseaseType).all())

@app.route('/diseases')
def diseases():
    return render_template('diseases.html', name=current_user.name, query=db.session.query(Disease).all(), dtype=DiseaseType)

@app.route('/records')
def records():
    query = db.session.query(Record).all()
    return render_template('all_records.html', name=current_user.name, query=query)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

@app.route('/users')
@login_required
def users():
    if current_user.email=="yerkebulan.ratkhan@nu.edu.kz":
        return render_template('users.html', name=current_user.email, query=db.session.query(Users).all())
    flash("You have no access to see all users", "error")
    return render_template('dashboard.html', name=current_user.email)

@app.route('/profile')
@login_required
def profile():
    form=RegisterForm()
    form.email.data=current_user.email
    form.cname.data=current_user.cname
    form.phone.data=current_user.phone
    form.salary.data=current_user.salary
    form.password.data=current_user.password
    form.name.data=current_user.name
    form.surname.data=current_user.surname
    #i = PublicServant.query.filter_by(email=current_user.email).first()
    #u = Doctor.query.filter_by(email=current_user.email).first()
    u = db.session.query(Doctor).filter_by(email=current_user.email).first()
    i = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    print(i is not None)
    specs=[]
    if u is not None:
        #q = Specialize.query.filter_by(email=current_user.email)
        q = db.session.query(Specialize).filter_by(email=current_user.email)
        for a in q:
            i = a.id
            #id = DiseaseType.query.filter_by(id=i).first()
            id = db.session.query(DiseaseType).filter_by(id=i).first()
            specs.append(id.description)
    return render_template('profile.html', form=form, servant=i is not None, doctor=u is not None, specs=specs, form2=AddSpecializationForm())

@app.route('/myrecords')
@login_required
def myrecords():
    #i = PublicServant.query.filter_by(email=current_user.email).first()
    i = db.session.query(PublicServant).filter_by(email=current_user.email).first()
    if i is not None:
        #q = Record.query.filter_by(email=current_user.email)
        q = db.session.query(Record).filter_by(email=current_user.email)
        if q.count() ==0:
            flash("You have no records yet", "success")
        return render_template('myrecords.html', name=current_user.email, query=q)
    flash("Only public servants have own records", "error")
    return render_template('myrecords_noaccess.html')

@app.route('/myrecords/edit/<cname>/<disease_code>', methods=['GET', 'POST'])
@login_required
def gotoeditrecord(cname, disease_code):
    #q = Record.query.filter_by(email=current_user.email, cname=cname, disease_code=disease_code).first()
    q = db.session.query(Record).filter_by(email=current_user.email, cname=cname, disease_code=disease_code).first()
    form=RecordForm()
    form.email.data = q.email
    form.disease_code.data=q.disease_code
    form.total_deathcount.data=q.total_deaths
    form.total_patients.data=q.total_patients
    form.cname.data=q.cname
    return render_template('editrecordform.html', name=current_user.email, form=form)
@app.route('/updaterecord', methods=['GET', 'POST'])
@login_required
def updaterecord():
    form=RecordForm()
    print(form.total_deathcount.data)
    #q = Record.query.filter_by(email=current_user.email, cname=form.cname.data,disease_code=form.disease_code.data)
    t=db.session.query(Record).filter_by(email=current_user.email, cname=form.cname.data,disease_code=form.disease_code.data).first()
    t.total_deaths=form.total_deathcount.data
    t.total_patients = form.total_patients.data
    #q.update({'total_deaths':form.total_deathcount.data},{'total_patients':form.total_patients.data})
    db.session.commit()
    flash("The record successfully updated", "success")
    return redirect(url_for('myrecords'))
@app.route('/myrecords/delete/<cname>/<disease_code>', methods=['GET', 'POST'])
@login_required
def deleterecord(cname, disease_code):
    t = db.session.query(Record).filter_by(email=current_user.email, cname=cname,
                                           disease_code=disease_code).first()
    db.session.delete(t)
    db.session.commit()
    flash("The record successfully deleted", "success")
    return redirect(url_for('myrecords'))
@app.route('/updateprofile', methods=['GET', 'POST'])
@login_required
def updateprofile():
    form=RegisterForm()
    #q = Record.query.filter_by(email=current_user.email, cname=form.cname.data,disease_code=form.disease_code.data)
    if current_user.email!=form.email.data:
        u = db.session.query(Users).filter_by(email=form.email.data).first()
        if u is not None:
            flash("Account with such email already exists", "error")
            return redirect(url_for('profile'))
        else:
            d = db.session.query(Doctor).filter_by(email=current_user.email).first()
            if d is not None:
                d.email = form.email.data
                db.session.commit()
            s = db.session.query(PublicServant).filter_by(email=current_user.email).first()
            if s is not None:
                s.email = form.email.data
                db.session.commit()
    t=db.session.query(Users).filter_by(email=current_user.email).first()
    t.email=form.email.data
    t.cname=form.cname.data
    t.surname = form.surname.data
    t.name = form.name.data
    t.phone = form.phone.data
    t.salary = form.salary.data
    db.session.commit()
    login_user(t)
    flash("Your profile sucessfully saved", "success")
    return redirect(url_for('profile'))

@app.route('/add_disease_type')
@login_required
def add_disease_type():
    #u = Doctor.query.filter_by(email=current_user.email).first()
    u = db.session.query(Doctor).filter_by(email=current_user.email).first()
    if u is not None:
        return render_template('add_disease_type.html', name=current_user.name, form=DiseaseTypeForm())
    flash("Only doctors can add disease type", "error")
    return render_template('add_disease_type_noaccess.html')

@app.route('/add_disease_type_save', methods=['GET', 'POST'])
@login_required
def add_disease_type_save():
    form=DiseaseTypeForm()
    dtype = DiseaseType(description=form.description.data)
    db.session.add(dtype)
    db.session.commit()
    flash("Disease type successfully added", "success")
    return redirect(url_for('diseasetypes'))

@app.route('/add_disease')
@login_required
def add_disease():
    #u = Doctor.query.filter_by(email=current_user.email).first()
    u = db.session.query(Doctor).filter_by(email=current_user.email).first()
    if u is not None:
        return render_template('add_disease.html', name=current_user.name, form=DiseaseForm())
    flash("Only doctors can add disease", "error")
    return render_template('add_disease_noaccess.html')

@app.route('/add_disease_save', methods=['GET', 'POST'])
@login_required
def add_disease_save():
    form=DiseaseForm()
    d = Disease(disease_code=form.disease_code.data, pathogen=form.pathogen.data, description=form.description.data, id=form.id.data)
    db.session.add(d)
    db.session.commit()
    flash("Disease successfully added", "success")
    return redirect(url_for('diseases'))

@app.route('/doctors')
def doctors():
    #doctors = Doctor.query.all()
    doctors = db.session.query(Doctor).all()
    list={}
    for d in doctors:
        specs = []
        #q = Specialize.query.filter_by(email=d.email)
        q = db.session.query(Specialize).filter_by(email=d.email)
        for a in q:
            i = a.id
            #id = DiseaseType.query.filter_by(id=i).first()
            id = db.session.query(DiseaseType).filter_by(id=i).first()
            specs.append(id.description)
        list[d]=specs
    return render_template('doctors.html', name=current_user.name, doctors=doctors, user=Users, Specialize=Specialize, list=list, db=db)

@app.route('/publicservants')
def publicservants():
    #servants = PublicServant.query.all()
    servants = db.session.query(PublicServant).all()
    user = Users
    return render_template('publicservants.html', name=current_user.name, servants=servants, user=user, db=db)

@app.route('/patients')
def patients():
    con = db.engine.connect()
    a=con.execute("select cname, sum(total_patients) from record group by cname order by sum(total_patients) desc")
    b=con.execute("select disease_code, sum(total_patients) from record group by disease_code order by sum(total_patients) desc")
    c=con.execute("select diseasetype.description, sum(record.total_patients) from record inner join disease on disease.disease_code=record.disease_code inner join diseasetype "
                        "on disease.id=diseasetype.id group by diseasetype.id, diseasetype.description order by sum(record.total_patients) desc")
    return render_template('patients.html', query=a, query2=b, query3=c)

@app.route('/deathcount')
def deathcount():
    con = db.engine.connect()
    a=con.execute("select cname, sum(total_deaths) from record group by cname order by sum(total_deaths) desc")
    b=con.execute("select disease_code, sum(total_deaths) from record group by disease_code order by sum(total_deaths) desc")
    c=con.execute("select diseasetype.description, sum(record.total_deaths) from record inner join disease on disease.disease_code=record.disease_code inner join diseasetype "
                        "on disease.id=diseasetype.id group by diseasetype.id, diseasetype.description order by sum(record.total_deaths) desc")
    return render_template('deathcount.html', query=a, query2=b, query3=c)

@app.route('/pssortbyrecords')
def pssortbyrecords():
    a=db.engine.execute("select count(publicservant.email), publicservant.email from record inner join publicservant"
                        " on record.email=publicservant.email group by publicservant.email order by count(publicservant.email) desc ")
    return render_template('pssortbyrecords.html', query=a)

@app.route('/pssortbycountries')
def pssortbycountries():
    a = db.engine.execute("select A.email, count(A.email) from (select record.email, record.cname from record group by record.email, record.cname) as A group by A.email order by count(A.email) desc")
    return render_template('pssortbycountry.html', query=a)

@app.route('/discoverquery')
def discoverquery():
    q = db.session.query(Discovery).filter_by().all()
    a=DiscoverQuery()
    a.cname.data="ANY"
    a.disease_code.data = "ANY"
    d = DateBetween()
    return render_template('discoverquery.html', form=a, q=q, form2=d)

@app.route('/discoverquerypost', methods=['GET', 'POST'])
def discoverquerypost():
    a = DiscoverQuery()
    form=DateBetween()
    if form.checkstart()==True and form.checkend()==True:
        if form.validate_on_submit() == False:
            flash("Start date must be earlier", "error")
            return render_template('discoverquery.html', form=a, form2=form)
    if a.cname.data != "ANY":
        if a.disease_code.data != "ANY":
            if form.checkstart() == False and form.checkend() == False:
                q = db.session.query(Discovery).filter_by(cname=a.cname.data, disease_code=a.disease_code.data).all()
            elif form.checkstart()==True and form.checkend()==False:
                q = db.session.query(Discovery).filter(Discovery.cname==a.cname.data and Discovery.disease_code==a.disease_code.data).filter(Discovery.first_enc_date > form.startdate.data).all()
            elif form.checkstart()==False and form.checkend()==True:
                q = db.session.query(Discovery).filter(Discovery.cname==a.cname.data and Discovery.disease_code==a.disease_code.data).filter(Discovery.first_enc_date < form.enddate.data).all()
            elif form.checkstart()==True and form.checkend()==True:
                q = db.session.query(Discovery).filter(Discovery.cname==a.cname.data and Discovery.disease_code==a.disease_code.data).filter(Discovery.first_enc_date < form.enddate.data).filter(Discovery.first_enc_date > form.startdate.data).all()
        else:
            if form.checkstart() == False and form.checkend() == False:
                q = db.session.query(Discovery).filter_by(cname=a.cname.data).all()
            elif form.checkstart()==True and form.checkend()==False:
                q = db.session.query(Discovery).filter_by(cname=a.cname.data).filter(Discovery.first_enc_date > form.startdate.data).all()
            elif form.checkstart()==False and form.checkend()==True:
                q = db.session.query(Discovery).filter_by(cname=a.cname.data).filter(Discovery.first_enc_date < form.enddate.data).all()
            elif form.checkstart()==True and form.checkend()==True:
                q = db.session.query(Discovery).filter_by(cname=a.cname.data).filter(Discovery.first_enc_date < form.enddate.data).filter(Discovery.first_enc_date > form.startdate.data).all()
    else:
        if a.disease_code.data != "ANY":
            if form.checkstart() == False and form.checkend() == False:
                q = db.session.query(Discovery).filter_by(disease_code=a.disease_code.data).all()
            elif form.checkstart() == True and form.checkend() == False:
                q = db.session.query(Discovery).filter_by(disease_code=a.disease_code.data).filter(
                    Discovery.first_enc_date > form.startdate.data).all()
            elif form.checkstart() == False and form.checkend() == True:
                q = db.session.query(Discovery).filter_by(disease_code=a.disease_code.data).filter(
                    Discovery.first_enc_date < form.enddate.data).all()
            elif form.checkstart() == True and form.checkend() == True:
                q = db.session.query(Discovery).filter_by(disease_code=a.disease_code.data).filter(
                    Discovery.first_enc_date < form.enddate.data).filter(
                    Discovery.first_enc_date > form.startdate.data).all()
        else:
            q = db.session.query(Discovery).filter_by().all()
            if form.checkstart() == False and form.checkend() == False:
                q = db.session.query(Discovery).filter_by().all()
            elif form.checkstart() == True and form.checkend() == False:
                q = db.session.query(Discovery).filter_by().filter(
                    Discovery.first_enc_date > form.startdate.data).all()
            elif form.checkstart() == False and form.checkend() == True:
                q = db.session.query(Discovery).filter_by().filter(
                    Discovery.first_enc_date < form.enddate.data).all()
            elif form.checkstart() == True and form.checkend() == True:
                q = db.session.query(Discovery).filter_by().filter(
                    Discovery.first_enc_date < form.enddate.data).filter(
                    Discovery.first_enc_date > form.startdate.data).all()
    return render_template('discoverquery.html', query=q, form=a, d=Disease(), form2=form)

@app.route('/deleteaccount', methods=['GET', 'POST'])
@login_required
def deleteaccount():
    u = db.session.query(Users).filter_by(email=current_user.email).first()
    db.session.delete(u)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
