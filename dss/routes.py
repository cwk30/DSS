import traceback
import secrets
import requests as r
import xlsxwriter
from onemapsg import OneMap
import json
from collections import defaultdict
from sqlalchemy.inspection import inspect
import os
from PIL import Image 
from datetime import datetime, timedelta
import pandas as pd
from flask import render_template
from flask import url_for 
from flask import flash 
from flask import redirect
from flask import request, abort
from flask import jsonify
from dss import app, db, bcrypt, mail
from dss.forms import (RegistrationForm,LoginForm, UpdateAccountForm, PostForm,RequestResetForm, ResetPasswordForm,
    MaterialsForm, FilterForm, maxRowsForm, BuyingForm,
    dispatchMatchingForm, dispatchMatchingQuestionsForm, dispatchMatchingResultsForm,
    LCCForm, RSPForm) 
from dss.models import (User, Post, RSP, Materials, Questions, Giveoutwaste, Processwaste, Technology, Takeinresource, Supplier, Technologybreakdown, Technologycode, 
    Dispatchmatchingresults, Dispatchmatchingsupply, Dispatchmatchingdemand, Sample, TechnologyDB)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import or_, and_
from sqlalchemy import create_engine
from flask_sqlalchemy import Pagination

from dss.wasteIdGenerator import Waste
from dss.dispatchMatchingSavingsBreakdown import CostSavings

from .PyomoSolver import PyomoModel

from .LCCTest import TechSpecifications
#bananas test

def distance(start,end):
    email = "e0175262@u.nus.edu"
    passw = "Password1"

    locSupply = start
    locDemand = end


    # print(sorted([locSupply,locDemand]))
    #loc1, loc2 = [locSupply,locDemand].sort()


    onemap = OneMap(email,passw)
    loc1 = onemap.search(locSupply).results[0]
    loc2 = onemap.search(locDemand).results[0]

    loc1_latlong = ','.join(loc1.lat_long)
    loc2_latlong = ','.join(loc2.lat_long)

    route = onemap.route(loc1_latlong, loc2_latlong, 'drive')
    return route.route_summary['total_distance']

def feasibility_check(techid,wasteid):
    rset = Giveoutwaste.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    waste_df = pd.DataFrame(result)

    rset = TechnologyDB.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    RSP_df = pd.DataFrame(result)

    rset = Materials.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    materials_df = pd.DataFrame(result)

    # try:
    waste_material_id=waste_df.loc[waste_df['id'] == int(wasteid), 'materialId'].iloc[0]
    waste_questioncode=waste_df.loc[waste_df['id']==int(wasteid),'questionCode'].iloc[0]
    tech_material_id=RSP_df.loc[RSP_df['id'] == int(techid), 'materialId'].iloc[0]
    RSP_df.set_index('id',inplace=True)
    tech_material=(materials_df.loc[materials_df['id'] == int(tech_material_id), 'material'].iloc[0])
    waste_material=(materials_df.loc[materials_df['id'] == int(waste_material_id), 'material'].iloc[0])
    # print(tech_material)
    # print(waste_material)
    if tech_material!=waste_material:
        
        return 0
    else:
        
        homogeneity=waste_questioncode[1]
        wCHNType=waste_questioncode[2]
        wCRatio=waste_questioncode[3:5]
        wHRatio=waste_questioncode[5:7]
        wNRatio=waste_questioncode[7:9]
        wproteinType=waste_questioncode[9]
        wproteinRatio=waste_questioncode[10:12]
        wcellulosic=waste_questioncode[12]
        wshellAndBones=waste_questioncode[13:15]
        wmoistureType=waste_questioncode[15]
        wmoistureContent=waste_questioncode[16:18]
        wsaltType=waste_questioncode[18]
        wsaltContent=waste_questioncode[19:21]
        wpHType=waste_questioncode[21]
        wphValue=waste_questioncode[22:24]
        wparticleSize=waste_questioncode[24]

        attrib=['materialId',
                'CRatiomin',
                'CRatiomax',
                'NRatiomin',
                'NRatiomax',
                'Moisturemin',
                'Moisturemax',
                'pHmin',
                'pHmax',
                'cellulosicmin',
                'cellulosicmax',
                'particleSizemin',
                'particleSizemax',
                'unacceptableshells',
                'unacceptableshells',
                'unacceptableshellspercent',
                'unacceptablebones',
                'unacceptablebonespercent',
                'unacceptablebamboo',
                'unacceptablebamboopercent',
                'unacceptablebanana',
                'unacceptablebananapercent',
                'unacceptableothers',
                'unacceptableotherspercent',
                'TechnologyName',
                'byproductBiogas',
                'byproductBiogasEfficiency',
                'byproductBiogasCHFour',
                'byproductBiogasCOTwo',
                'ByproductChemical',
                'ByproductChemicalEfficiency',
                'ByproductMetal',
                'ByproductMetalEfficiency',
                'ByproductBiochar',
                'ByproductBiocharEfficency',
                'ByproductDigestate',
                'ByproductDigestateEfficiency',
                'ByproductOil',
                'ByproductOilEfficiency',
                'ByproductOthers',
                'ByproductOthersEfficiency',
                'TechnologyName',
                'AdditionalInformation']
        techID = {}
        #print(df.loc[i,'description'])
        #print(techID)
        for at in attrib:
            techID[at]=RSP_df.loc[techid,at]
        # print('Buyer:'+str(techid))
        # print('Seller:'+str(wasteid))
        # print('Waste CRatio:'+wCRatio)
        # print('Waste NRatio:'+wNRatio)
        # print('Waste pH:'+wphValue)
        # print('RSP pH Range '+techID['pHmin']+' '+techID['pHmax'])
        # print('RSP CRatio'+techID['CRatiomin']+' '+techID['CRatiomax'])
        # print('RSP NRatio'+techID['NRatiomin']+' '+techID['NRatiomax'])
        
        if (wCRatio=='__' or (int(wCRatio)>=int(techID['CRatiomin']) and int(wCRatio)<=int(techID['CRatiomax']))) and ((wNRatio)=='__' or (int(wNRatio)>=int(techID['NRatiomin']) and int(wNRatio)<=int(techID['NRatiomax']))) and ((wphValue)=='__' or (int(wphValue)>=int(techID['pHmin']) and int(wphValue)<=int(techID['pHmax']))):
            return 1
        else:
            return 0
    # except:
    #     return 0




    


@app.route("/") 
def landing():
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    else:
        return render_template('index.html')

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/dashboard")
@login_required
def dashboard():
    #posts=db.execute("SELECT * FROM post order by id")
    return render_template('dashboard.html')

@app.route("/home") 
@login_required
def home():
    return render_template('dashboard.html') 

@app.route("/about")
def about():
    return render_template('about.html', title='About') 

@app.route("/posts_home")
def posts_home():
    page = request.args.get('page', 1, type=int) 
    posts = Post.query.paginate(page=page, per_page=2) 
    return render_template('posts_home.html', title="Posts Home", posts=posts)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,listings=0,transacted=0,totalposts=0,totalsuccess=0,totalwaste=0)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", 'success') 
        return redirect(url_for('login'))
    return render_template('register.html', title="Register", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename) 
    picture_fn = random_hex + f_ext 
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn) 
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required 
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account info has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file) 
    return render_template('account.html', title="Account", image_file=image_file, form=form)

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id) 
    return render_template('Post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', 
                            form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>") 
def user_posts(username):
    page = request.args.get('page', 1, type=int) 
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=2) 

    return render_template('user_posts.html', posts=posts, user=user) 

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)} 

If you did not make this request, simply ignore this email and no change will be made to your account.
'''
    mail.send(msg)

@app.route("/reset_request", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None: 
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    
    form =  ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated! You are now able to log in", 'success') 
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)




#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


@app.route("/matching", methods=['GET', 'POST'])
def matching():
    if current_user.is_authenticated:
        pass
    else: 
        flash(f'Please log in first','danger')
        return redirect(url_for("login"))
    return render_template('matching.html')

@app.route("/matching/sellingwaste", methods=['GET', 'POST'])
def selling_waste():
    if current_user.is_authenticated:
        pass
    else: 
        flash(f'Please log in first','danger')
        return redirect(url_for("login"))

    form = MaterialsForm()
    form.type.choices = [(material.type, material.type) for material in Materials.query.group_by(Materials.type)]
    form.material.choices = [(material.id, material.material) for material in Materials.query.filter_by(type=Materials.query.first().type).all()]
    #get past waste ID
    prevEntries = [(waste.id, waste.questionCode + ': ' + waste.description + ' - ' + waste.date.strftime("%d/%m/%Y")) for waste in Giveoutwaste.query.filter_by(userId=int(current_user.id)).all()]
    prevEntries.insert(0,(None,None))
    form.wasteID.choices = prevEntries
    # flash(prevEntries, 'success')

    if request.method == 'POST':
        #user selects past Waste ID
        if form.wasteID.data != None:
            print(form.wasteID.data)
            return redirect(url_for("matching_filter_waste", giveoutwasteId=form.wasteID.data))
        #creates new Waste ID
        else:
            return redirect(url_for("matching_questions",materialId=form.material.data))
    return render_template('sellingwaste.html', title="Matching", form=form)

@app.route("/matching/recycling_service_provider", methods=['GET', 'POST'])
def recycling_service_provider():
    if current_user.is_authenticated:
        pass
    else: 
        flash(f'Please log in first','danger')
        return redirect(url_for("login"))

    form = RSPForm()
    form.maincat.choices = [(rsp.maincat, rsp.maincat) for rsp in RSP.query.group_by(RSP.maincat)]
    form.subcat.choices = [(rsp.id, rsp.subcat) for rsp in RSP.query.filter_by(maincat=RSP.query.first().maincat).all()]
    #get past technology ID
    prevEntries = [(waste.id, waste.description + ': ' + waste.TechnologyName + ' - ' + waste.date) for waste in TechnologyDB.query.filter_by(userId=int(current_user.id)).all()]
    prevEntries.insert(0,(None,None))
    form.technologyID.choices = prevEntries
    # flash(prevEntries, 'success')

    if request.method == 'POST':
        #user selects past Tech ID
        if form.technologyID.data != None:
            print(form.technologyID.data)
            return redirect(url_for("matching_filter_recycling", processwasteId=form.technologyID.data))
        #creates new Tech ID
        else:
            return redirect(url_for("matching_questions",materialId=form.subcat.data))
    return render_template('recycling_service_provider.html', title="Matching", form=form)    

@app.route("/matching/buying_resources", methods=['GET', 'POST'])
def buying_resources_selection():
    if current_user.is_authenticated:
        pass
    else: 
        flash(f'Please log in first','danger')
        return redirect(url_for("login"))
    return render_template('buying_resource.html', title="Matching")  

@app.route("/matching/buying_resources/processed", methods=['GET', 'POST'])
def buying_resources():
    if current_user.is_authenticated:
        pass
    else: 
        flash(f'Please log in first','danger')
        return redirect(url_for("login"))

    form = BuyingForm()
    form.dropdown.choices = ['Biogas','Chemical','Metal','Biochar','Digestate','Oil','Others']
    

    if request.method == 'POST':
        if form.dropdown.data == None:
            return redirect(url_for("buying_resources"))
        else:
            return redirect(url_for("matching_filter_resource",byproduct=form.dropdown.data))
    return render_template('buying_resources.html', title="Matching", form=form)

@app.route("/matching/filter_resource/waste", methods=['GET', 'POST'])
def buying_waste():

    rset = Giveoutwaste.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    df = pd.DataFrame(result)

    
    counter=0
    result=[]
    attrib=['materialId',
                    'CRatiomin',
                    'CRatiomax',
                    'NRatiomin',
                    'NRatiomax',
                    'Moisturemin',
                    'Moisturemax',
                    'pHmin',
                    'pHmax',
                    'cellulosicmin',
                    'cellulosicmax',
                    'particleSizemin',
                    'particleSizemax',
                    'unacceptableshells',
                    'unacceptableshells',
                    'unacceptableshellspercent',
                    'unacceptablebones',
                    'unacceptablebonespercent',
                    'unacceptablebamboo',
                    'unacceptablebamboopercent',
                    'unacceptablebanana',
                    'unacceptablebananapercent',
                    'unacceptableothers',
                    'unacceptableotherspercent',
                    'TechnologyName',
                    'byproductBiogas',
                    'byproductBiogasEfficiency',
                    'byproductBiogasCHFour',
                    'byproductBiogasCOTwo',
                    'ByproductChemical',
                    'ByproductChemicalEfficiency',
                    'ByproductMetal',
                    'ByproductMetalEfficiency',
                    'ByproductBiochar',
                    'ByproductBiocharEfficency',
                    'ByproductDigestate',
                    'ByproductDigestateEfficiency',
                    'ByproductOil',
                    'ByproductOilEfficiency',
                    'ByproductOthers',
                    'ByproductOthersEfficiency',
                    'TechnologyName',
                    'AdditionalInformation']

        
    #print(techmaterialID)
    for i in range(len(df)):
        wastematerialID=int(df.loc[i,'materialId'])
        #print(techmaterialID)
        print(wastematerialID)      
        
        wasteID = (df.loc[i,'questionCode'])
        print(wasteID)
        # homogeneity=wasteID[1]
        # wCHNType=wasteID[2]
        # wCRatio=wasteID[3:5]
        # wHRatio=wasteID[5:7]
        # wNRatio=wasteID[7:9]
        # wproteinType=wasteID[9]
        # wproteinRatio=wasteID[10:12]
        # wcellulosic=wasteID[12]
        # wshellAndBones=wasteID[13:15]
        # wmoistureType=wasteID[15]
        # wmoistureContent=wasteID[16:18]
        # wsaltType=wasteID[18]
        # wsaltContent=wasteID[19:21]
        # wpHType=wasteID[21]
        # wphValue=wasteID[22:24]
        # wparticleSize=wasteID[24]
        counter+=1
        index=(counter)
        desc=(df.loc[i,'description'])
        supplier=(User.query.filter_by(id=int(df.loc[i,'userId'])).first().username)
        #print(supplier)
        rawdate=str(df.loc[i,'date'])
        rawdate=rawdate[:10]
        result.append([index,desc,supplier,rawdate])
    return render_template('matching_results_recycling.html', result=result )

   

@app.route("/materials/<Type>")
def materials(Type):
    materials = Materials.query.order_by(Materials.id.asc()).filter_by(type=Type).all()

    materialArray = []
    for material in materials:
        materialObj = {}
        materialObj['id'] = material.id
        materialObj['material'] = material.material
        materialArray.append(materialObj)
    return jsonify({'materials' : materialArray})

@app.route("/rsp/<maincat>")
def rsp(maincat):
    rsp = RSP.query.order_by(RSP.id.asc()).filter_by(maincat=maincat).all()

    subcatArray = []
    for subcat in rsp:
        subcatObj = {}
        subcatObj['id'] = subcat.id
        subcatObj['subcat'] = subcat.subcat
        subcatArray.append(subcatObj)
    return jsonify({'subcats' : subcatArray})

@app.route("/matching/questions/<materialId>", methods=['GET', 'POST'])
@login_required
def matching_questions(materialId):
    form = []
    material = Materials.query.filter_by(id=materialId).first()
    samples = Sample.query.all()
    result = defaultdict(list)
    for obj in samples:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    df = pd.DataFrame(result)
    samplefood=df['FoodItem'].tolist()
    #print(df)
    #print(samplefood)
    if material.type == '1. Selling Waste':
        giveOutWaste = True
        buyWaste = False
        processWaste = False
    elif material.type=='2. Purchase Resources':
        giveOutWaste = False
        buyWaste = True
        processWaste = False
    else:
        giveOutWaste = False
        buyWaste = False
        processWaste = True
    #get questions
    questionId = material.questionId.split(',')
    questions = []
    for id in questionId:
        questions.append(Questions.query.filter_by(id=id).first())
    
    if request.method == 'POST':
        
        print(request.data)
        print(request.form)
        #print(request.form.getlist('Q51_Chemical'))

        #save file
        if giveOutWaste and request.files["file"]:
            file = request.files["file"] 
            file.save(os.path.join(app.config['UPLOAD'],file.filename))
           
            #process file
            reportCode = 1
        else: 
            reportCode = 0
        
        #convert output to a code    
        try:
            if giveOutWaste:
                wasteObj = Waste(materialId, request)
                questionCode = wasteObj.getId()
                if questionCode[0:5] == "Error":
                    flash(questionCode,'danger')
                    return redirect(url_for("matching_questions", materialId=materialId))
            if processWaste:
                description = str(request.form['description'])
                userId = int(current_user.id)
                materialId = int(materialId)
                CRatiomin = int(request.form['Q45_min_C'])
                CRatiomax = int(request.form['Q45_max_C'])
                NRatiomin = int(request.form['Q45_min_N'])
                NRatiomax = int(request.form['Q45_max_N'])
                if len(request.form.getlist('Q46_moisture'))==2:
                    Moisturemin = int(request.form['Q46_min_moisture'])
                    Moisturemax = int(request.form['Q46_max_moisture'])
                else:
                    Moisturemin = 0
                    Moisturemax = 100
                if len(request.form.getlist('Q46_pH'))==2:
                    pHmin = int(request.form['Q46_min_ph'])
                    pHmax = int(request.form['Q46_max_ph'])
                else:
                    pHmin = 1
                    pHmax = 14
                if len(request.form.getlist('Q46_cellulosic'))==2:
                    cellulosicmin = int(request.form['Q46_min_Cellulosic'])
                    cellulosicmax = int(request.form['Q46_max_Cellulosic'])
                else:
                    cellulosicmin = 0
                    cellulosicmax = 100
                if len(request.form.getlist('Q46_size'))==2:
                    particleSizemin = int(request.form['Q46_min_Size'])
                    particleSizemax = int(request.form['Q46_max_Size'])
                else:
                    particleSizemin = 0
                    particleSizemax = 100
                
                
                if len(request.form.getlist('Q47_1'))==2:
                    unacceptableshells = 1
                    unacceptableshellspercent = int(request.form['Q47_1_value'])
                else:
                    unacceptableshells = 0
                    unacceptableshellspercent = 0
                if len(request.form.getlist('Q47_2'))==2:
                    unacceptablebones = 1
                    unacceptablebonespercent = int(request.form['Q47_2_value'])
                else:
                    unacceptablebones = 0
                    unacceptablebonespercent = 0
                if len(request.form.getlist('Q47_3'))==2:
                    unacceptablebamboo = 1
                    unacceptablebamboopercent = int(request.form['Q47_3_value'])
                else:
                    unacceptablebamboo = 0
                    unacceptablebamboopercent = 0
                if len(request.form.getlist('Q47_4'))==2:
                    unacceptablebanana = 1
                    unacceptablebananapercent = int(request.form['Q47_4_value'])
                else:
                    unacceptablebanana = 0
                    unacceptablebananapercent = 0
                        
                if len(request.form.getlist('Q47_5'))==2:
                    unacceptableothers = 1
                    unacceptableotherspercent = int(request.form['Q47_5_value'])
                else:
                    unacceptableothers = 0
                    unacceptableotherspercent = 0
                
                if len(request.form.getlist('Q51_Biogas'))==2:
                    byproductBiogas = 1
                    byproductBiogasEfficiency = int(request.form['Q51_Biogas_efficiency'])
                    byproductBiogasCHFour = int(request.form['Q51_Biogas_ch4'])
                    byproductBiogasCOTwo = int(request.form['Q51_Biogas_co2'])

                else:
                    byproductBiogas = 0
                    byproductBiogasEfficiency = 0
                    byproductBiogasCHFour = 0
                    byproductBiogasCOTwo = 0

                if len(request.form.getlist('Q51_Chemical'))==2:
                    ByproductChemical = 1
                    ByproductChemicalEfficiency = int(request.form['Q51_Chemical_efficiency'])
                else:
                    ByproductChemical = 0
                    ByproductChemicalEfficiency = 0

                if len(request.form.getlist('Q51_Metal'))==2:
                    ByproductMetal = 1
                    ByproductMetalEfficiency = int(request.form['Q51_Metal_efficiency'])
                else:
                    ByproductMetal = 0
                    ByproductMetalEfficiency = 0

                if len(request.form.getlist('Q51_Biochar'))==2:
                    ByproductBiochar = 1
                    ByproductBiocharEfficency = int(request.form['Q51_Biochar_efficiency'])
                else:
                    ByproductBiochar = 0
                    ByproductBiocharEfficency = 0

                if len(request.form.getlist('Q51_Digestate'))==2:
                    ByproductDigestate = 1
                    ByproductDigestateEfficiency = int(request.form['Q51_Digestate_efficiency'])
                else:
                    ByproductDigestate = 0
                    ByproductDigestateEfficiency = 0

                if len(request.form.getlist('Q51_Oil'))==2:
                    ByproductOil = 1
                    ByproductOilEfficiency = int(request.form['Q51_Oil_efficiency'])
                else:
                    ByproductOil = 0
                    ByproductOilEfficiency = 0

                if len(request.form.getlist('Q51_Others'))==2:
                    ByproductOthers = 1
                    ByproductOthersEfficiency = int(request.form['Q51_Others_efficiency'])
                else:
                    ByproductOthers = 0
                    ByproductOthersEfficiency = 0

                TechnologyName = str(request.form['Q50_tech'])
                AdditionalInformation = str(request.form['Q53'])
                questionCode = "Submitted!"




            
            
        except Exception:
            traceback.print_exc()
            flash(f'Please ensure that the form is filled in correctly first before submitting','danger')
            return redirect(url_for("matching_questions", materialId=materialId))

        flash(f'ID: {questionCode}', 'success')

        #if logged in (bring outside in the future)
        if current_user.is_authenticated:
            pass
        else: 
            flash(f'Please log in first','danger')
            return redirect(url_for("login"))

        if giveOutWaste:
            # insert into database
            waste = Giveoutwaste(materialId=int(materialId), questionCode=questionCode, reportCode=str(reportCode), userId=int(current_user.id), description=request.form['description'] or None, date=datetime.now())
            db.session.add(waste)
            db.session.commit()
            
            #get wasteId:
            flash('Your response has been recorded!','success')
            return redirect(url_for("selling_waste"))

        elif processWaste:
            techID = TechnologyDB(userId=userId,
            materialId=materialId,
            CRatiomin=CRatiomin,
            CRatiomax=CRatiomax,
            NRatiomin=NRatiomin,
            NRatiomax=NRatiomax,
            Moisturemin=Moisturemin,
            Moisturemax=Moisturemax,
            pHmin=pHmin,
            pHmax=pHmax,
            cellulosicmin=cellulosicmin,
            cellulosicmax=cellulosicmax,
            particleSizemin=particleSizemin,
            particleSizemax=particleSizemax,
            unacceptableshells=unacceptableshells,
            unacceptableshellspercent=unacceptableshellspercent,
            unacceptablebones=unacceptablebones,
            unacceptablebonespercent=unacceptablebonespercent,
            unacceptablebamboo=unacceptablebamboo,
            unacceptablebamboopercent=unacceptablebamboopercent,
            unacceptablebanana=unacceptablebanana,
            unacceptablebananapercent=unacceptablebananapercent,
            unacceptableothers=unacceptableothers,
            unacceptableotherspercent=unacceptableotherspercent,
            TechnologyName=TechnologyName,
            byproductBiogas=byproductBiogas,
            byproductBiogasEfficiency=byproductBiogasEfficiency,
            byproductBiogasCHFour=byproductBiogasCHFour,
            byproductBiogasCOTwo=byproductBiogasCOTwo,
            ByproductChemical=ByproductChemical,
            ByproductChemicalEfficiency=ByproductChemicalEfficiency,
            ByproductMetal=ByproductMetal,
            ByproductMetalEfficiency=ByproductMetalEfficiency,
            ByproductBiochar=ByproductBiochar,
            ByproductBiocharEfficency=ByproductBiocharEfficency,
            ByproductDigestate=ByproductDigestate,
            ByproductDigestateEfficiency=ByproductDigestateEfficiency,
            ByproductOil=ByproductOil,
            ByproductOilEfficiency=ByproductOilEfficiency,
            ByproductOthers=ByproductOthers,
            ByproductOthersEfficiency=ByproductOthersEfficiency,
            AdditionalInformation=AdditionalInformation,
            date=str(datetime.now())[0:19],
            description=description)
            db.session.add(techID)
            db.session.commit()
            flash('Your response has been recorded!','success')
            return redirect(url_for("recycling_service_provider"))

        else:
            resource = Takeinresource(materialId=int(materialId), questionCode=questionCode, userId=int(current_user.id), description=request.form['description'] or None, date=datetime.now())
            db.session.add(resource)
            db.session.commit()
            #get resourceId:
            takeinresourceId = Takeinresource.query.order_by(Takeinresource.id.desc()).first().id
            return redirect(url_for("matching_filter_resource", takeinresourceId=takeinresourceId))

    return render_template('matching_questions.html', title="Matching Questions", form=form, questions=questions, material=material, giveOutWaste=giveOutWaste, samplefood=samplefood, samplefoodlen=len(samplefood), materialId=materialId)

@app.route("/matching/filter_waste/<giveoutwasteId>", methods=['GET','POST'])
def matching_filter_waste(giveoutwasteId):
    # form = FilterForm()
    # materialId = Giveoutwaste.query.filter_by(id=giveoutwasteId).first().materialId

    # #get possible by-products
    # form.byproductType.choices = [(technology.byProduct, technology.byProduct) for technology in Technology.query.filter_by(materialId=materialId).group_by(Technology.byProduct)]
    # form.byproductType.choices.insert(0,('All','Display all'))

    # if request.method == 'POST':
    #     return redirect(url_for("matching_results_waste", giveoutwasteId=giveoutwasteId, byProduct=form.byproductType.data, landSpace=form.landSpace.data, cost=form.investmentCost.data, env=form.environmentalImpact.data))
    # return render_template('matching_filter_waste.html', title="Matching Filter", form=form)
    wasteID = Giveoutwaste.query.filter_by(id=giveoutwasteId).first().questionCode
    wastematerialID = Giveoutwaste.query.filter_by(id=giveoutwasteId).first().materialId
    rset = TechnologyDB.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    df = pd.DataFrame(result)
    #print(df)
    counter=0
    result=[]
    homogeneity=wasteID[1]
    wCHNType=wasteID[2]
    wCRatio=wasteID[3:5]
    wHRatio=wasteID[5:7]
    wNRatio=wasteID[7:9]
    wproteinType=wasteID[9]
    wproteinRatio=wasteID[10:12]
    wcellulosic=wasteID[12]
    wshellAndBones=wasteID[13:15]
    wmoistureType=wasteID[15]
    wmoistureContent=wasteID[16:18]
    wsaltType=wasteID[18]
    wsaltContent=wasteID[19:21]
    wpHType=wasteID[21]
    wphValue=wasteID[22:24]
    wparticleSize=wasteID[24]

    #print(wastematerialID)
    for i in range(len(df)):
        techmaterialID=int(df.loc[i,'materialId'])      
        if wastematerialID==1 and techmaterialID==14:
            attrib=['materialId',
                    'CRatiomin',
                    'CRatiomax',
                    'NRatiomin',
                    'NRatiomax',
                    'Moisturemin',
                    'Moisturemax',
                    'pHmin',
                    'pHmax',
                    'cellulosicmin',
                    'cellulosicmax',
                    'particleSizemin',
                    'particleSizemax',
                    'unacceptableshells',
                    'unacceptableshells',
                    'unacceptableshellspercent',
                    'unacceptablebones',
                    'unacceptablebonespercent',
                    'unacceptablebamboo',
                    'unacceptablebamboopercent',
                    'unacceptablebanana',
                    'unacceptablebananapercent',
                    'unacceptableothers',
                    'unacceptableotherspercent',
                    'TechnologyName',
                    'byproductBiogas',
                    'byproductBiogasEfficiency',
                    'byproductBiogasCHFour',
                    'byproductBiogasCOTwo',
                    'ByproductChemical',
                    'ByproductChemicalEfficiency',
                    'ByproductMetal',
                    'ByproductMetalEfficiency',
                    'ByproductBiochar',
                    'ByproductBiocharEfficency',
                    'ByproductDigestate',
                    'ByproductDigestateEfficiency',
                    'ByproductOil',
                    'ByproductOilEfficiency',
                    'ByproductOthers',
                    'ByproductOthersEfficiency',
                    'TechnologyName',
                    'AdditionalInformation']
            techID = {}
            #print(df.loc[i,'description'])
            #print(techID)
            for at in attrib:
                techID[at]=df.loc[i,at]
            #print('Waste CRatio:'+wCRatio)
            #print('Waste NRatio:'+wNRatio)
            #print('Waste pH:'+wphValue)
            #print('RSP pH Range '+techID['pHmin']+' '+techID['pHmax'])
            #print('RSP CRatio'+techID['CRatiomin']+' '+techID['CRatiomax'])
            #print('RSP NRatio'+techID['NRatiomin']+' '+techID['NRatiomax'])
            
            if (wCRatio=='__' or (int(wCRatio)>=int(techID['CRatiomin']) and int(wCRatio)<=int(techID['CRatiomax']))) and ((wNRatio)=='__' or (int(wNRatio)>=int(techID['NRatiomin']) and int(wNRatio)<=int(techID['NRatiomax']))) and ((wphValue)=='__' or (int(wphValue)>=int(techID['pHmin']) and int(wphValue)<=int(techID['pHmax']))):
                counter+=1
                index=(counter)
                desc=(df.loc[i,'description'])
                supplier=(User.query.filter_by(id=int(df.loc[i,'userId'])).first().username)
                #print(supplier)
                rawdate=str(df.loc[i,'date'])
                rawdate=rawdate[:10]
                result.append([index,desc,supplier,rawdate])
    return render_template('matching_results_waste.html', result=result )

@app.route("/matching/filter_recycling/<processwasteId>", methods=['GET','POST'])
def matching_filter_recycling(processwasteId):
    techstuff=TechnologyDB.query.filter_by(id=processwasteId).first()
    
    techmaterialID = TechnologyDB.query.filter_by(id=processwasteId).first().materialId
    rset = Giveoutwaste.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    df = pd.DataFrame(result)

    results = defaultdict(list)
    instance = inspect(techstuff)
    for key, x in instance.attrs.items():
        results[key].append(x.value)    
    #techdf = pd.DataFrame(result)
    #print(results)
    #print(df)
    counter=0
    result=[]
    #TechnologyDB.query.filter_by(id=processwasteId).first()
    attrib=['materialId',
                    'CRatiomin',
                    'CRatiomax',
                    'NRatiomin',
                    'NRatiomax',
                    'Moisturemin',
                    'Moisturemax',
                    'pHmin',
                    'pHmax',
                    'cellulosicmin',
                    'cellulosicmax',
                    'particleSizemin',
                    'particleSizemax',
                    'unacceptableshells',
                    'unacceptableshells',
                    'unacceptableshellspercent',
                    'unacceptablebones',
                    'unacceptablebonespercent',
                    'unacceptablebamboo',
                    'unacceptablebamboopercent',
                    'unacceptablebanana',
                    'unacceptablebananapercent',
                    'unacceptableothers',
                    'unacceptableotherspercent',
                    'TechnologyName',
                    'byproductBiogas',
                    'byproductBiogasEfficiency',
                    'byproductBiogasCHFour',
                    'byproductBiogasCOTwo',
                    'ByproductChemical',
                    'ByproductChemicalEfficiency',
                    'ByproductMetal',
                    'ByproductMetalEfficiency',
                    'ByproductBiochar',
                    'ByproductBiocharEfficency',
                    'ByproductDigestate',
                    'ByproductDigestateEfficiency',
                    'ByproductOil',
                    'ByproductOilEfficiency',
                    'ByproductOthers',
                    'ByproductOthersEfficiency',
                    'TechnologyName',
                    'AdditionalInformation']
    techID = {}
    for at in attrib:
        #print(results[at][0])
        techID[at]=results[at][0]
        
    #print(techmaterialID)
    for i in range(len(df)):
        wastematerialID=int(df.loc[i,'materialId'])
        #print(techmaterialID)
        #print(wastematerialID)      
        if int(techmaterialID)==14 and int(wastematerialID)==1:
            #print("Triggered")
            wasteID = (df.loc[i,'questionCode'])
            #print(wasteID)
            homogeneity=wasteID[1]
            wCHNType=wasteID[2]
            wCRatio=wasteID[3:5]
            wHRatio=wasteID[5:7]
            wNRatio=wasteID[7:9]
            wproteinType=wasteID[9]
            wproteinRatio=wasteID[10:12]
            wcellulosic=wasteID[12]
            wshellAndBones=wasteID[13:15]
            wmoistureType=wasteID[15]
            wmoistureContent=wasteID[16:18]
            wsaltType=wasteID[18]
            wsaltContent=wasteID[19:21]
            wpHType=wasteID[21]
            wphValue=wasteID[22:24]
            wparticleSize=wasteID[24]
            #print(wCRatio)
            #print(wNRatio)
            #print(wphValue)
            #print(techID['pHmin'])        
            if (wCRatio=='__' or (int(wCRatio)>=int(techID['CRatiomin']) and int(wCRatio)<=int(techID['CRatiomax']))) and ((wNRatio)=='__' or (int(wNRatio)>=int(techID['NRatiomin']) and int(wNRatio)<=int(techID['NRatiomax']))) and ((wphValue)=='__' or (int(wphValue)>=int(techID['pHmin']) and int(wphValue)<=int(techID['pHmax']))):
                counter+=1
                index=(counter)
                desc=(df.loc[i,'description'])
                supplier=(User.query.filter_by(id=int(df.loc[i,'userId'])).first().username)
                #print(supplier)
                rawdate=str(df.loc[i,'date'])
                rawdate=rawdate[:10]
                result.append([index,desc,supplier,rawdate])
    return render_template('matching_results_recycling.html', result=result )

@app.route("/matching/filter_resource/<byproduct>", methods=['GET','POST'])
def matching_filter_resource(byproduct):
    rset = Processwaste.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    df = pd.DataFrame(result)
    counter=0
    result=[]
    byproducts = ['Biogas','Chemical','Metal','Biochar','Digestate','Oil','Others']
    j=41
    for k in range(len(byproducts)):
        if byproducts[k]==byproduct:
            print(byproduct)
            for i in range(len(df)):
                techID=(df.loc[i,'questionCode'])      
                byproductID=techID[j+k]
                if byproductID=="1":
                    counter+=1
                    index=(counter)
                    desc=(df.loc[i,'description'])
                    supplier=(User.query.filter_by(id=int(df.loc[i,'userId'])).first().username)
                    #print(supplier)
                    rawdate=str(df.loc[i,'date'])
                    rawdate=rawdate[:10]
                    result.append([index,desc,supplier,rawdate])


    return render_template('matching_results_buyer.html', result=result,byproduct=byproduct)


# @app.route("/matching/results_waste/<giveoutwasteId>/<byProduct>/<landSpace>/<cost>/<env>", methods=['GET','POST'])
# def matching_results_waste(giveoutwasteId,byProduct,landSpace,cost,env):
#     form = maxRowsForm()
#     page = request.args.get('page', 1, type=int)
#     order = request.args.get('order','id',type=str)
#     orderName = 'None' if order == 'id' else order

#     #get material info
#     material = Giveoutwaste.query.filter_by(id=giveoutwasteId).first()
#     materialId = material.materialId
#     materialCode = material.questionCode
#     materialType = Materials.query.filter_by(id=materialId).first().material

#     #technology matching
#     techCode = Technologycode.query.all() #if can add the filter here will be more efficient
#     feasibleTech = []
#     for tech in techCode:
#         #checks if feasibility set matches
#         feasible = Giveoutwaste.query.filter(Giveoutwaste.id==giveoutwasteId , Giveoutwaste.questionCode.like(tech.wasteCode)).all()
#         if feasible != []:
#             technology = Technology.query.filter_by(id=tech.technologyId).first()
#             #filter based on landspace/cost/env
#             if byProduct == 'All':
#                 if technology.landSpace <= int(landSpace) and technology.estimatedCost <= int(cost) and technology.environmentalImpact <= int(env):
#                     feasibleTech.append(technology)
#             else:
#                 if technology.byProduct == byProduct and technology.landSpace <= int(landSpace) and technology.estimatedCost <= int(cost) and technology.environmentalImpact <= int(env):
#                     feasibleTech.append(technology)

#     #sort results
#     if order != 'id':
#         feasibleTech.sort(key=lambda x: getattr(x,order) )

#     #convert to pagination object  
#     per_page = 3
#     feasibleTech = Pagination(query=feasibleTech, page=page, per_page=per_page, total=len(feasibleTech), items=feasibleTech[per_page*(page-1):(per_page*page)]) #items is results to show in current page

#     if request.method == 'POST':
#         return redirect(url_for('matching_results_waste', giveoutwasteId=giveoutwasteId,byProduct=byProduct,landSpace=landSpace,cost=cost,env=env,page=page,order=form.order.data))
#     return render_template('matching_results_waste.html', title="Matching Results", results=feasibleTech, materialType=materialType, form=form, order=order, orderName=orderName, giveoutwasteId=giveoutwasteId,byProduct=byProduct,landSpace=landSpace,cost=cost,env=env)   

# @app.route("/matching/filter_resource/<takeinresourceId>", methods=['GET','POST'])
# def matching_filter_resource(takeinresourceId):
#     form = FilterForm()
#     resourceId = Takeinresource.query.filter_by(id=takeinresourceId).first().materialId

#     #get possible by-products
#     form.byproductType.choices = [(technology.byProduct, technology.byProduct) for technology in Technology.query.filter_by(resourceId=resourceId).group_by(Technology.byProduct)]
#     form.byproductType.choices.insert(0,('All','Display all'))

#     if request.method == 'POST':
#         return redirect(url_for("matching_results_resource", takeinresourceId=takeinresourceId, byProduct=form.byproductType.data, landSpace=form.landSpace.data, cost=form.investmentCost.data, env=form.environmentalImpact.data))
#     return render_template('matching_filter_resource.html', title="Matching Filter", form=form)

@app.route("/matching/results_resource/<takeinresourceId>/<byProduct>/<landSpace>/<cost>/<env>", methods=['GET','POST'])
def matching_results_resource(takeinresourceId,byProduct,landSpace,cost,env):
    form = maxRowsForm()
    page = request.args.get('page', 1, type=int)
    order = request.args.get('order','id',type=str)
    orderName = 'None' if order == 'id' else order

    #get material info
    materialId = Takeinresource.query.filter_by(id=takeinresourceId).first().materialId
    materialType = Materials.query.filter_by(id=materialId).first().material
        
    if byProduct == 'All':
        results = Technology.query.\
            filter(Technology.resourceId==materialId, Technology.landSpace<=landSpace, Technology.estimatedCost<=cost, Technology.environmentalImpact<=env)\
            .order_by( getattr(Technology,order) .asc()).paginate(page=page, per_page=5) 
    else:
        results = Technology.query.\
            filter(Technology.resourceId==materialId, Technology.byProduct==byProduct, Technology.landSpace<=landSpace, Technology.estimatedCost<=cost, Technology.environmentalImpact<=env)\
            .order_by( getattr(Technology,order) .asc()).paginate(page=page, per_page=5) 

    if request.method == 'POST':
        return redirect(url_for('matching_results_resource', takeinresourceId=takeinresourceId,byProduct=byProduct,landSpace=landSpace,cost=cost,env=env,page=page,order=form.order.data))
    return render_template('matching_results_resource.html', title="Matching Results", results=results, materialType=materialType, form=form, order=order, orderName=orderName, takeinresourceId=takeinresourceId,byProduct=byProduct,landSpace=landSpace,cost=cost,env=env)


@app.route("/matching/technology/<technologyId>", methods=['GET','POST'])
def matching_technology(technologyId):
    technology = Technology.query.filter(Technology.id==technologyId).first()
    technologyBreakdown = Technologybreakdown.query.filter(Technologybreakdown.technologyId==int(technologyId)).first()

    #carousel pictures & HTML
    navHTML = []
    if technologyBreakdown and technologyBreakdown.carouselHTML:
        for i in range(len(technologyBreakdown.carouselHTML.split('<div class="carousel-item"'))):
            if technologyBreakdown.carouselHTML != None:
                navHTML.append(f'<li data-target="#technologyPictures" data-slide-to="{i}"></li>')


    return render_template('matching_technology.html', title="Matching Technology", technology=technology, technologyBreakdown=technologyBreakdown, navHTML=navHTML)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route("/dispatch_matching", methods=['GET','POST'])
def dispatch_matching():
    form = dispatchMatchingForm()
    if request.method == 'POST':
        if form.type.data == '0':
            return redirect(url_for('dispatch_matching_questions_waste'))
        else:
            return redirect(url_for('dispatch_matching_questions_resource'))
    return render_template('dispatch_matching.html', title="Dispatch Matching", form=form)


@app.route("/dispatch_matching/questions_waste", methods=['GET','POST'])
def dispatch_matching_questions_waste():
    form = dispatchMatchingQuestionsForm()
    #get past waste ID
    prevEntries = [(waste.id, waste.questionCode + ': ' + waste.description + ' - ' + waste.date.strftime("%d/%m/%Y")) for waste in Giveoutwaste.query.filter_by(userId=int(current_user.id)).all()]
    prevEntries.insert(0,(None,None))
    form.wasteName.choices = prevEntries

    recommendedReservePrice = 640

    if request.method == 'POST':
        supply = Dispatchmatchingsupply(userId=current_user.id,giveOutWasteId=form.wasteName.data,quantity=form.quantity.data,postalCode=form.postalCode.data,reservePrice=form.reservePrice.data,deliveryFee=form.deliveryFee.data,matchedFlag=0)
        if form.wasteName.data!='None' and form.postalCode.data.isnumeric() and len(form.postalCode.data)==6:
            db.session.add(supply)
            db.session.commit()
            flash('Your response has been recorded!','success')
            return redirect(url_for('dispatch_matching'))
        else:
            flash(f'Please check your inputs','danger')
    return render_template('dispatch_matching_questions_waste.html', title="Dispatch Matching Questions", form=form, recommendedReservePrice=recommendedReservePrice)

@app.route("/dispatch_matching/match", methods=['GET','POST'])
def dispatch_matching_match():
    rset = Dispatchmatchingdemand.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    raw_demand = pd.DataFrame(result)
    rset = Dispatchmatchingsupply.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    raw_supply = pd.DataFrame(result)
    rset = Materials.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    raw_materials = pd.DataFrame(result)
    rset = User.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    raw_user = pd.DataFrame(result)
    rset = Giveoutwaste.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    raw_waste = pd.DataFrame(result)
    rset = TechnologyDB.query.all()
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            result[key].append(x.value)    
    raw_technology = pd.DataFrame(result)
    
    material_list=[]
    entity_list=[]
    company_list=[]
    postal_list=[]
    long_list=[]
    lat_list=[]
    BS_list=[]
    industry_supply_df=pd.DataFrame(columns=['entity','material','quantity','reserve_price','delivery_fee'])
    industry_demand_df=pd.DataFrame(columns=['entity','material','quantity','reserve_price'])
    for i in raw_demand.itertuples():
        company_list.append(raw_user.loc[raw_user['id'] == int(i.userId), 'username'].iloc[0])
        entity_list.append(i.takeInResourceId)
        postal_list.append(i.postalCode)
        BS_list.append('B')
        response = r.get('http://developers.onemap.sg/commonapi/search?searchVal='+i.postalCode+'&returnGeom=Y&getAddrDetails=Y&pageNum={1}')
        response_dict = json.loads(response.text)
        if response_dict['found']!=0:
            results = response_dict['results'][0]
            long_list.append(results['LONGITUDE'])
            lat_list.append(results['LATITUDE'])
        else:
            long_list.append(None)
            lat_list.append(None)
        material_id=raw_technology.loc[raw_technology['id'] == int(i.takeInResourceId), 'materialId'].iloc[0]
        material_entry=raw_materials.loc[raw_materials['id']== int(material_id),'material'].iloc[0]
        industry_demand_df = industry_demand_df.append({'entity' : i.takeInResourceId, 'material': material_entry, 'quantity': i.quantity, 'reserve_price': i.reservePrice}, ignore_index = True)
        if material_entry not in material_list:
            material_list.append(material_entry)
    for i in raw_supply.itertuples():
        company_list.append(raw_user.loc[raw_user['id'] == int(i.userId), 'username'].iloc[0])
        entity_list.append(i.giveOutWasteId)
        postal_list.append(i.postalCode)
        BS_list.append('S')
        response = r.get('http://developers.onemap.sg/commonapi/search?searchVal='+i.postalCode+'&returnGeom=Y&getAddrDetails=Y&pageNum={1}')
        response_dict = json.loads(response.text)
        if response_dict['found']!=0:
            results = response_dict['results'][0]
            long_list.append(results['LONGITUDE'])
            lat_list.append(results['LATITUDE'])
        else:
            long_list.append(None)
            lat_list.append(None)
        material_id=raw_waste.loc[raw_waste['id'] == int(i.giveOutWasteId), 'materialId'].iloc[0]
        material_entry=raw_materials.loc[raw_materials['id']==int(material_id),'material'].iloc[0]
        industry_supply_df = industry_supply_df.append({'entity' : i.giveOutWasteId, 'material': material_entry, 'quantity': i.quantity, 'reserve_price': i.reservePrice, 'delivery_fee': i.deliveryFee}, ignore_index = True)
        if material_entry not in material_list:
            material_list.append(material_entry)
    
    material_df=pd.DataFrame({'material': material_list})
    entity_df=pd.DataFrame({'entity': entity_list})
    industry_df=pd.DataFrame({'entity': entity_list, 'company': company_list, 'postal_code': postal_list, 'lat': lat_list, 'lon': long_list, 'BS': BS_list})
    distance_df= pd.DataFrame(index=range(len(entity_list)),columns=['entity']+list(range(len(entity_list))))
    distance_df=distance_df.assign(entity=entity_list)
    distance_df=distance_df.set_index('entity')
    feasible_df = distance_df.copy()
    for i in industry_df.itertuples():
        counter=0
        for j in industry_df.itertuples():
            if i.BS != j.BS:
                # if (i.BS=='B' and (industry_demand_df.loc[industry_demand_df['entity'] == int(i.entity), 'material'].iloc[0]==industry_supply_df.loc[industry_supply_df['entity'] == int(j.entity), 'material'].iloc[0])):
                #     if feasibility_check(i.entity,j.entity)==1:
                #         feasible_df.loc[i.entity,j.entity]=0
                #         distance_df.loc[i.entity,j.entity]=distance(i.postal_code,j.postal_code)/1000.0
                        
                if (i.BS=='S' and (industry_supply_df.loc[industry_supply_df['entity'] == int(i.entity), 'material'].iloc[0]==industry_demand_df.loc[industry_demand_df['entity'] == int(j.entity), 'material'].iloc[0])):
                    if feasibility_check(j.entity,i.entity)==1:
                        feasible_df.loc[i.entity,counter]=0
                        distance_df.loc[i.entity,counter]=distance(i.postal_code,j.postal_code)/1000.0
            counter+=1
    print(feasible_df)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    report_path = 'dss/PyomoSolver/'
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    writer = pd.ExcelWriter(os.path.join(report_path + 'case_data.xlsx'), engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    material_df.to_excel(writer, sheet_name='material',index=False)
    entity_df.to_excel(writer, sheet_name='entity',index=False)
    industry_df.to_excel(writer, sheet_name='industry',index=False)
    industry_supply_df.to_excel(writer, sheet_name='industry_supply',index=False)
    industry_demand_df.to_excel(writer, sheet_name='industry_demand',index=False)
    feasible_df.to_excel(writer, sheet_name='feasible',index=True)
    distance_df.to_excel(writer, sheet_name='distance',index=True)
    

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    solution=PyomoModel.runModel()
    writer = pd.ExcelWriter(os.path.join(report_path + 'solution.xlsx'), engine='xlsxwriter')
    solution.to_excel(writer, sheet_name='soln',index=True)
    writer.save()

    solution.reset_index(inplace=True)
    for i in solution.itertuples():
        result = Dispatchmatchingresults(supplyId=int(i.producer_id)-len(raw_demand)+1,demandId=int(i.consumer_id)+1,materialId=i.material_id,price=i.price,quantity=i.quantity,date=str(datetime.now())[0:11])
        db.session.add(result)
        db.session.commit()
    

    return redirect(url_for('dispatch_matching'))
    

@app.route("/dispatch_matching/questions_resource", methods=['GET','POST'])
def dispatch_matching_questions_resource():
    form = dispatchMatchingQuestionsForm()
    prevEntries = [(waste.id, waste.TechnologyName + ': ' + waste.description + ' - ' + waste.date[:10]) for waste in TechnologyDB.query.filter_by(userId=int(current_user.id)).all()]
    prevEntries.insert(0,(None,None))
    form.wasteName.choices = prevEntries

    recommendedReservePrice = 21

    if request.method == 'POST':
        demand = Dispatchmatchingdemand(userId=current_user.id,takeInResourceId=form.wasteName.data,quantity=form.quantity.data,postalCode=form.postalCode.data,reservePrice=form.reservePrice.data,matchedFlag=0)
        if form.wasteName.data!='None' and form.postalCode.data.isnumeric() and len(form.postalCode.data) == 6:
            db.session.add(demand)
            db.session.commit()
            flash('Your response has been recorded!','success')
            return redirect(url_for('dispatch_matching'))
        else:
            flash(f'Please check your inputs','danger')
    return render_template('dispatch_matching_questions_resource.html', title="Dispatch Matching Questions", form=form, recommendedReservePrice=recommendedReservePrice)


@app.route("/dispatch_matching/results", methods=['GET','POST'])
def dispatch_matching_results():
    form = dispatchMatchingResultsForm()

    #user change to current user id in the future
    # userId = 113
    userId = current_user.id


    form.date.choices = [(Dispatchmatchingresult.date, Dispatchmatchingresult.date) for Dispatchmatchingresult in Dispatchmatchingresults.query.group_by(Dispatchmatchingresults.date)]

    # soln = PyomoModel.runModel()
    # soln = soln.to_html(classes=["table","table-hover"])

    if request.method == 'POST':
        sell = []
        supplierSurplus = None
        buy = []
        demandSurplus = None
        #get matched buyers
        print(userId)
        print(form.buySell.data)
        if form.buySell.data != '2':
            supplyIds = Dispatchmatchingsupply.query.filter_by(userId=userId).all()
            
            for supplyId in supplyIds:
                sell.extend(Dispatchmatchingresults.query.filter_by(supplyId=supplyId.id, date=form.date.data).all())
                
            #set running number and surplus
            supplierSurplus = 0
            for i in range(len(sell)):
                sell[i].no = str(i+1)+'.'
                supplierSurplus += float(sell[i].supplierSurplus())
            supplierSurplus = "{:.2f}".format(supplierSurplus)

        if form.buySell.data != '1':
        #get matched sellers
            demandIds = Dispatchmatchingdemand.query.filter_by(userId=userId).all()
            for demandId in demandIds:    
                buy.extend(Dispatchmatchingresults.query.filter_by(demandId=demandId.id, date=form.date.data).all())
            
            #set running number and surplus
            demandSurplus = 0
            for i in range(len(buy)):
                buy[i].no = str(i+1)+'.'
                demandSurplus += float(buy[i].demandSurplus())
            demandSurplus = "{:.2f}".format(demandSurplus) 
                        
        return render_template('dispatch_matching_results.html', title="Dispatch Matching Results", form=form, match=True, sell=sell, buy=buy, date=form.date.data, supplierSurplus=supplierSurplus, demandSurplus=demandSurplus)

    return render_template('dispatch_matching_results.html', title="Dispatch Matching Results", form=form)

@app.route("/dispatch_matching/results/savings/<date>/<buySell>", methods=['GET','POST'])
def dispatch_matching_results_savings(date, buySell):

    userId = 113

    buyBreakdown,sellBreakdown,supplierSurplus,demandSurplus = 0,0,0,0
    

    
    if buySell == '0':
        sellBreakdown = []
        supplyIds = Dispatchmatchingsupply.query.filter_by(userId=userId).all()
        #get relevant matches    
        for supplyId in supplyIds:
            sellBreakdown.extend(Dispatchmatchingresults.query.filter_by(supplyId=supplyId.id, date=date).all() ) 
        for i in range(len(sellBreakdown)):
            sellBreakdown[i] = CostSavings(sell=sellBreakdown[i])

        #calculate surplus
        supplierSurplus = 0
        for i in range(len(sellBreakdown)):
            supplierSurplus += float(sellBreakdown[i].surplus)
        supplierSurplus = "{:.2f}".format(supplierSurplus) 

    if buySell == '1':
        buyBreakdown = []
        demandIds = Dispatchmatchingdemand.query.filter_by(userId=userId).all()
        #get relevant matches
        for demandId in demandIds:    
            buyBreakdown.extend(Dispatchmatchingresults.query.filter_by(demandId=demandId.id, date=date).all())
        for i in range(len(buyBreakdown)):
            buyBreakdown[i] = CostSavings(buy=buyBreakdown[i])
        
        #calculate surplus
        demandSurplus = 0
        for i in range(len(buyBreakdown)):
            demandSurplus += float(buyBreakdown[i].surplus)
        demandSurplus = "{:.2f}".format(demandSurplus) 



    return render_template('dispatch_matching_results_savings.html', title="Dispatch Matching Cost Breakdown", sellBreakdown=sellBreakdown, supplierSurplus=supplierSurplus, buyBreakdown=buyBreakdown, demandSurplus=demandSurplus)





@app.route("/dispatch_matching/results/contact", methods=['GET','POST'])
def dispatch_matching_results_contact():
    return render_template('dispatch_matching_results_contact.html', title="Dispatch Matching Contact")



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.route("/LCC", methods=['GET','POST'])
def LCC():
    form = LCCForm()
    if request.method == 'POST':
        return redirect(url_for('LCC_results', technologyId=form.technology.data, weightPerYear=form.weightPerYear.data, disposalCostPerTon=form.disposalCostPerTon.data, discountRate=form.discountRate.data ))
    return render_template('LCC.html', title="LCC Analysis", form=form)

@app.route("/LCC/results/<technologyId>/<weightPerYear>/<disposalCostPerTon>/<discountRate>", methods=['GET','POST'])
def LCC_results(technologyId,weightPerYear,disposalCostPerTon,discountRate):

    #tech specifications (stored in database)
    noOfYears = 10      #machine lifespan?
    capitalCost = 50000

    rawMaterialCost = 3017.13
    utilitiesCost = 49.91
    maintenanceCost = 5000
    maintenanceFrequency = [3,7]     #list of years that machine requires maintenance
    salvageValue = 25000

    #tech output 
    #figure out how to store this in database
    byproductName = ['Gold', 'Silver', 'Palladium']
    percentageExtraction = [0.97, 0.98, 0.93]
    percentageComposition = [0.00025, 0.0001, 0.001]

    #see if can extract from Quandl
    price = [58141868.4, 620966.57, 65073624.0]

    #process material data
    byproductSpecifications = []
    for i in range(len(byproductName)):
        row = []
        row.append(byproductName[i])
        row.append(round(percentageExtraction[i]*percentageComposition[i]*price[i],2))
        row.append(percentageExtraction[i])
        row.append(percentageComposition[i])
        row.append(price[i])

        byproductSpecifications.append(row)
    # flash(byproductSpecifications,'success')

    
    #create technology object
    tech = TechSpecifications(noOfYears, capitalCost, rawMaterialCost, utilitiesCost, maintenanceCost, 
        maintenanceFrequency, salvageValue, byproductName, percentageExtraction, percentageComposition)

    return render_template('LCC_results.html', title="LCC Results", tech=tech, byproductSpecifications=byproductSpecifications, weightPerYear=float(weightPerYear), disposalCostPerTon=float(disposalCostPerTon), discountRate=float(discountRate), price=price)