import os.path

# from flask_mysqldb import MySQL
from flask import Flask, render_template, redirect, url_for, flash, request
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin
# login_user, login_required, logout_user, current_user, login_manager

import hashlib
from werkzeug.utils import secure_filename
# import io
# from models import Image
# from sqlalchemy_media import Image, Attachment
# from flask_mysqldb import MySQL

# Imports from other .py files of this project
from config import app, db, login_manager, mysql
from models import Accounts, Cars, Repair_Works, Worker, Mileage
from forms import RegistrationForm, LoginForm, CreateLotForm, CreateRepairWorkForm, CreateMileageForm


# with app.app_context():
#     db.create_all()

# @staticmethod
def get(user_id):
    return Accounts.query.get(user_id)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def greeting():
    return render_template('lobby.html')


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm()
    if request.method == 'POST':
        new_account = Accounts(login=form.username.data, password=form.password.data)
        db.session.add(new_account)
        db.session.commit()
        print(new_account.idAccounts)
        if form.isworker.data:  # Если выбран флажок, добавляем данные о работнике
            worker = Worker(
                First_Name=form.first_name.data,
                Second_Name=form.second_name.data,
                Surname=form.surname.data,
                Account_ID=new_account.idAccounts  # Ссылка на id аккаунта
            )
            print(new_account.idAccounts)

            db.session.add(worker)
            db.session.commit()
        return redirect(url_for('view'))

    return render_template('sign-up.html', form=form)


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    form = LoginForm()
    if request.method == 'POST':
        username = form.username.data
        password = form.password.data

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM accounts WHERE login = %s AND password = %s", (username, password))
        user = cur.fetchone()

        if user:
            return redirect(url_for('view'))
        else:
            flash('Invalid login or password.', 'danger')
        cur.close()
    return render_template('log-in.html', form=form)


@app.route('/view', methods=['GET', 'POST'])
def view():
    return render_template('view.html')


@app.route('/create_lot', methods=['GET', 'POST'])
def create_lot():
    form = CreateLotForm()
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        category = request.form['category']
        vin = request.form['vin']
        plates = request.form['plates']
        production_date = request.form['production_date']
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)  # Save the image to the filesystem

            new_lot = Cars(Make=make, Model=model, Plates=plates, Production_Date=production_date,
                           Vehicle_Category=category, VIN=vin, Image_name=filename, Image_path=file_path)
            db.session.add(new_lot)
            db.session.commit()

        return redirect(url_for('view'))

    return render_template('create_lot.html', form=form)


@app.route('/image/<int:image_id>')
def image(image_id):
    image = Cars.query.get_or_404(image_id)
    return redirect(url_for('static', filename=image.path))


@app.route('/create_work', methods=['GET', 'POST'])
def create_repair_work():
    form = CreateRepairWorkForm()
    if request.method == 'POST':
        car = form.car.data
        worker = form.worker.data
        garage = form.garage.data
        detail = form.detail.data
        start_date = form.start_date.data
        type = form.type.data

        new_work = Repair_Works(Car=car, Worker=worker, Garage=garage,
                                Detail=detail, Start_Date=start_date, Type=type)
        db.session.add(new_work)
        db.session.commit()

        return redirect(url_for('view'))

    return render_template('create_work.html', form=form)


@app.route('/create_mileage', methods=['GET', 'POST'])
def create_mileage():
    form = CreateMileageForm()
    if request.method == 'POST':
        car_id = form.car_id.data
        mileage = form.mileage.data
        date = form.date.data

        new_mileage = Mileage(Car_ID=car_id, Mileage=mileage, Date=date)
        db.session.add(new_mileage)
        db.session.commit()

        return redirect(url_for('view'))

    return render_template('create_mileage.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    return Accounts.get(user_id)


if __name__ == '__main__':
    app.run(debug=True)
