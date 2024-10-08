from flask import Flask, request, session, render_template, redirect, flash, url_for, jsonify
from pymongo import MongoClient 
from bson import ObjectId
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Length
import re

app=Flask(__name__)

app.secret_key='karan@11'

mongo_url='mongodb://localhost:27017/'

client=MongoClient(mongo_url)
db=client.Flipkart
collection=db.Signup
details=db.mobile_details
order=db.order_place


def isloggedin():
    return 'user_name' in session

def is_password_storng(Password):
    if len(Password)<10 :
        return False
    if not re.search(r"\d",Password):
        return False
 
    return True

class User:
    def __init__(self, username, password):
        self.username=username
        self.password=password
        
class signup_form(FlaskForm):
    username=StringField("username",validators=[InputRequired(), Length(min=3, max=20)])
    password=PasswordField('password',validators=[InputRequired(), Length(min=4, max=50)])
    submit=SubmitField('SIGN UP')
    
class login_form(FlaskForm):
    username=StringField("username",validators=[InputRequired(), Length(min=3, max=20)])
    password=PasswordField('password',validators=[InputRequired(), Length(min=4, max=50)])
    submit=SubmitField('LOGIN')
   
@app.route('/oder')
def oder():
    return render_template('oder.html')   

@app.route('/')
def home():
    
    return render_template('index.html')

@app.route('/mobile')
def mobile():
    
    return render_template('mobile.html')


@app.route('/add_details',methods=['POST'])
def add_details():
    if not isloggedin():
        return redirect(url_for('login'))
    if isloggedin():
        model_name=request.form['model_name']
        storage=request.form['storage_details']
        color=request.form['color']
        rate=request.form['ratings']
        price=request.form['price']
        quantity=request.form['quantity']
        username=session["user_name"]
        mobile_no=session["password"]
        
        package_charge = 99
        
        total_price=int(price) + package_charge
        
        mobile_details={'Name':username,
                        'Mobile_no':mobile_no,
                        'model_name':model_name,
                        'storage_details':storage,
                        'color':color,
                        'ratings':rate,
                        'price':total_price,
                        'quantity':quantity
                        }
        
        order.insert_one(mobile_details) 
        return jsonify({'message': 'Your oder is confirmed'})
        
@app.route('/buy',methods=['GET','POST'])
def buy():
    
    data=details.find_one()
    
    return render_template('buy.html',data=data)


@app.route('/singup', methods=['GET','POST'])
def signup():
    form=signup_form()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
         
        if not is_password_storng(password):            
            return redirect(url_for('signup'))
        old_user=collection.find_one({'username':username})
        
        if old_user:    
            return render_template('signup.html',form=form)
        
        signup_data=collection.insert_one({'username':username,'password':password})
        print(signup_data)
        
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form=login_form()
    if form.validate_on_submit():
            username=form.username.data
            password=form.password.data
            
            record=collection.find_one({'username':username,'password':password})
            
            if record:
                    user=User(username=record['username'], password=record['password'])
                    session['user_name'] = user.username
                    session['password'] = user.password
                    return redirect(url_for('home'))
            else:
                flash('invalid credential','danger')
            
    return render_template('login.html',form=form)


@app.route('/logout')
def logout():
    session.pop('user_name',None)
    return redirect(url_for('home'))

if __name__=='__main__':
    app.run(debug=True)