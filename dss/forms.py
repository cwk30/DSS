from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField, SelectField
from wtforms.validators import Required, Length, Email, EqualTo, ValidationError
from dss.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username =  StringField("Username", validators=[Required(), Length(min=2, max=20)]) 

    email = StringField('Email', validators=[Required(), Email()]) 
    password = PasswordField('Password', validators=[Required()])

    confirm_password = PasswordField('Confirm Password', validators=[Required(), EqualTo('password')])

    submit = SubmitField('Sign Up') 

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first() 
        if user:
            raise ValidationError('That username is taken. Please choose a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() 
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username =  StringField("Username", validators=[Required(), Length(min=2, max=20)]) 

    password = PasswordField('Password', validators=[Required()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login') 

class UpdateAccountForm(FlaskForm):
    username =  StringField("Username", validators=[Required(), Length(min=2, max=20)])

    password = PasswordField('Password', validators=[Required()]) 

    remember = BooleanField('Remember Me')

    email = StringField('Email', validators=[Required(), Email()]) 

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update') 

    def validate_username(self, username):
        if username.data != current_user.username: 
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different username.')
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first() 
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[Required()])
    content = TextAreaField('Content', validators=[Required()])
    submit = SubmitField('Submit')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Email()])

    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() 
        if user is None:
            raise ValidationError('There is no account with that email. You must register first')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[Required()])

    confirm_password = PasswordField('Confirm Password', validators=[Required(), EqualTo('password')])

    submit = SubmitField('Reset Password')






#matching
class MaterialsForm(FlaskForm):
    wasteID = SelectField('Existing Waste Profile ID', choices=[])
    type = SelectField('Type', choices=[])
    material = SelectField('Material', choices=[])
    submit = SubmitField('Next')

class RSPForm(FlaskForm):
    technologyID = SelectField('Existing Technology Profile ID', choices=[])
    maincat = SelectField('Main Category', choices=[])
    subcat = SelectField('Subcategory', choices=[])
    submit = SubmitField('Next')

class BuyerForm(FlaskForm):
    submit = SubmitField('Next')


class FilterForm(FlaskForm):
    byproductType = SelectField('Filter by final output type:', choices=[])
    landSpace = SelectField('Filter by equipment land footprint:', choices=[(1000000,'Display all'), (10,'< 10 square meter/t/day'), (20,'< 20 square meter/t/day'), (30,'< 30 square meter/t/day')])
    investmentCost = SelectField('Filter by equipment cost budget:', choices=[(1000000,'Display all'), (5000,'< $ 5000/t/day'), (10000,'< $ 10000/t/day'), (15000,'< $ 15000/t/day')])
    environmentalImpact = SelectField('Filter by environmental impact:', choices=[(1000000,'Display all'), (100,'< 100 GWP/t/day'), (150,'< 150 GWP/t/day'), (200,'< 200 GWP/t/day')])
    submit = SubmitField('Match Optimisation')

class maxRowsForm(FlaskForm):
    # maxRows = SelectField('Return top', choices=[(3,'3'), (5,'5'), (10,'10')])
    order = SelectField('Order by', choices=[('landSpace','Land space'), ('estimatedCost','Estimated Cost'), ('environmentalImpact','Environmental Impact')])
    submit = SubmitField('Go')






#dispatch matching
class dispatchMatchingForm(FlaskForm):
    type = SelectField('Type', choices=[('0','Selling Waste'),('1','Purchasing Waste')])
    submit = SubmitField('Next')


class dispatchMatchingQuestionsForm(FlaskForm):
    wasteName = SelectField('Select waste to trade from what you have created:', choices=[])
    quantity = StringField('Supply Quantity: (t/month)', validators=[Required()])
    postalCode = StringField('Company Postal Code:', validators=[Required()])
    reservePrice = StringField('What is your reserve selling price? SGD', validators=[Required()])
    deliveryFee = StringField('Transportation Charge:', validators=[Required()])
    submit = SubmitField('Submit')


class dispatchMatchingResultsForm(FlaskForm):
    date = SelectField('Please select the matching results date:', choices=[])
    buySell = SelectField('View sell or purchase', choices=[(0,'All'),(1,'Selling Waste'),(2,'Purchase Resource',)])
    material = SelectField('View materials', choices=[('All','All')])
    submit = SubmitField('View Report')






class LCCForm(FlaskForm):
    technology = SelectField('Which technology to compare?', choices=[(0,'Technology A')])
    weightPerYear = StringField('Weight of waste generated per year:', validators=[Required()])
    disposalCostPerTon = StringField('Cost of disposal per tonne:', validators=[Required()])
    discountRate = StringField('Discount rate:', validators=[Required()])
    submit = SubmitField('Submit')
        

