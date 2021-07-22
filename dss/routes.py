import secrets
import os
from PIL import Image 
from datetime import datetime, timedelta
from flask import render_template
from flask import url_for 
from flask import flash 
from flask import redirect
from flask import request, abort
from flask import jsonify
from dss import app, db, bcrypt, mail
from dss.forms import (RegistrationForm,LoginForm, UpdateAccountForm, PostForm,RequestResetForm, ResetPasswordForm,
    MaterialsForm, FilterForm, maxRowsForm,
    dispatchMatchingForm, dispatchMatchingQuestionsForm, dispatchMatchingResultsForm,
    LCCForm) 
from dss.models import (User, Post, 
    Materials, Questions, Giveoutwaste, Technology, Takeinresource, Supplier, Technologybreakdown, Technologycode, 
    Dispatchmatchingresults, Dispatchmatchingsupply, Dispatchmatchingdemand)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import or_, and_
from flask_sqlalchemy import Pagination

from dss.wasteIdGenerator import Waste
from dss.dispatchMatchingSavingsBreakdown import CostSavings

from .PyomoSolver import PyomoModel

from .LCCTest import TechSpecifications
#bananas test

@app.route("/") 
def landing():
    if current_user.is_authenticated:
        return render_template('home.html')
    else:
        return render_template('index.html')

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/home") 
def home():
    return render_template('home.html') 

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
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,listings=0,transacted=0)
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
            return redirect(url_for("matching_filter_waste", giveoutwasteId=form.wasteID.data))
        #creates new Waste ID
        else:
            return redirect(url_for("matching_questions",materialId=form.material.data))
    return render_template('matching.html', title="Matching", form=form)
    

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


@app.route("/matching/questions/<materialId>", methods=['GET', 'POST'])
def matching_questions(materialId):
    form = []
    material = Materials.query.filter_by(id=materialId).first()
    if material.type == '1. Selling Waste':
        giveOutWaste = True
    else:
        giveOutWaste = False

    #get questions
    questionId = material.questionId.split(',')
    questions = []
    for id in questionId:
        questions.append(Questions.query.filter_by(id=id).first())
    
    if request.method == 'POST':

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
            wasteObj = Waste(materialId, request)
            questionCode = wasteObj.getId()
        except:
            flash(f'Please ensure that the form is filled in correctly first before submitting','danger')
            return redirect(url_for("matching_questions", materialId=materialId))

        flash(f'Waste ID: {questionCode}', 'success')

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
            return redirect(url_for("matching"))

        elif material.type == '3. Recycling Service Provider':
            for interest in questionCode:
                supplier = Supplier(materialId=int(materialId), userId=int(current_user.id), suppliedMaterials=interest, description=request.form['description'] or None)
                db.session.add(supplier)
            db.session.commit()
            flash('Your response has been recorded!','success')
            return redirect(url_for("matching"))

        else:
            resource = Takeinresource(materialId=int(materialId), questionCode=questionCode, userId=int(current_user.id), description=request.form['description'] or None, date=datetime.now())
            db.session.add(resource)
            db.session.commit()

            #get resourceId:
            takeinresourceId = Takeinresource.query.order_by(Takeinresource.id.desc()).first().id
            return redirect(url_for("matching_filter_resource", takeinresourceId=takeinresourceId))

    return render_template('matching_questions.html', title="Matching Questions", form=form, questions=questions, material=material, giveOutWaste=giveOutWaste)


@app.route("/matching/filter_waste/<giveoutwasteId>", methods=['GET','POST'])
def matching_filter_waste(giveoutwasteId):
    form = FilterForm()
    materialId = Giveoutwaste.query.filter_by(id=giveoutwasteId).first().materialId

    #get possible by-products
    form.byproductType.choices = [(technology.byProduct, technology.byProduct) for technology in Technology.query.filter_by(materialId=materialId).group_by(Technology.byProduct)]
    form.byproductType.choices.insert(0,('All','Display all'))

    if request.method == 'POST':
        return redirect(url_for("matching_results_waste", giveoutwasteId=giveoutwasteId, byProduct=form.byproductType.data, landSpace=form.landSpace.data, cost=form.investmentCost.data, env=form.environmentalImpact.data))
    return render_template('matching_filter_waste.html', title="Matching Filter", form=form)


@app.route("/matching/results_waste/<giveoutwasteId>/<byProduct>/<landSpace>/<cost>/<env>", methods=['GET','POST'])
def matching_results_waste(giveoutwasteId,byProduct,landSpace,cost,env):
    form = maxRowsForm()
    page = request.args.get('page', 1, type=int)
    order = request.args.get('order','id',type=str)
    orderName = 'None' if order == 'id' else order

    #get material info
    material = Giveoutwaste.query.filter_by(id=giveoutwasteId).first()
    materialId = material.materialId
    materialCode = material.questionCode
    materialType = Materials.query.filter_by(id=materialId).first().material

    #technology matching
    techCode = Technologycode.query.all() #if can add the filter here will be more efficient
    feasibleTech = []
    for tech in techCode:
        #checks if feasibility set matches
        feasible = Giveoutwaste.query.filter(Giveoutwaste.id==giveoutwasteId , Giveoutwaste.questionCode.like(tech.wasteCode)).all()
        if feasible != []:
            technology = Technology.query.filter_by(id=tech.technologyId).first()
            #filter based on landspace/cost/env
            if byProduct == 'All':
                if technology.landSpace <= int(landSpace) and technology.estimatedCost <= int(cost) and technology.environmentalImpact <= int(env):
                    feasibleTech.append(technology)
            else:
                if technology.byProduct == byProduct and technology.landSpace <= int(landSpace) and technology.estimatedCost <= int(cost) and technology.environmentalImpact <= int(env):
                    feasibleTech.append(technology)

    #sort results
    if order != 'id':
        feasibleTech.sort(key=lambda x: getattr(x,order) )

    #convert to pagination object  
    per_page = 3
    feasibleTech = Pagination(query=feasibleTech, page=page, per_page=per_page, total=len(feasibleTech), items=feasibleTech[per_page*(page-1):(per_page*page)]) #items is results to show in current page

    if request.method == 'POST':
        return redirect(url_for('matching_results_waste', giveoutwasteId=giveoutwasteId,byProduct=byProduct,landSpace=landSpace,cost=cost,env=env,page=page,order=form.order.data))
    return render_template('matching_results_waste.html', title="Matching Results", results=feasibleTech, materialType=materialType, form=form, order=order, orderName=orderName, giveoutwasteId=giveoutwasteId,byProduct=byProduct,landSpace=landSpace,cost=cost,env=env)   

@app.route("/matching/filter_resource/<takeinresourceId>", methods=['GET','POST'])
def matching_filter_resource(takeinresourceId):
    form = FilterForm()
    resourceId = Takeinresource.query.filter_by(id=takeinresourceId).first().materialId

    #get possible by-products
    form.byproductType.choices = [(technology.byProduct, technology.byProduct) for technology in Technology.query.filter_by(resourceId=resourceId).group_by(Technology.byProduct)]
    form.byproductType.choices.insert(0,('All','Display all'))

    if request.method == 'POST':
        return redirect(url_for("matching_results_resource", takeinresourceId=takeinresourceId, byProduct=form.byproductType.data, landSpace=form.landSpace.data, cost=form.investmentCost.data, env=form.environmentalImpact.data))
    return render_template('matching_filter_resource.html', title="Matching Filter", form=form)

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


@app.route("/dispatch_matching/questions_resource", methods=['GET','POST'])
def dispatch_matching_questions_resource():
    form = dispatchMatchingQuestionsForm()
    prevEntries = [(waste.id, waste.questionCode + ': ' + waste.description + ' - ' + waste.date.strftime("%d/%m/%Y")) for waste in Takeinresource.query.filter_by(userId=int(current_user.id)).all()]
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
    userId = 113


    form.date.choices = [(Dispatchmatchingresult.date, Dispatchmatchingresult.date) for Dispatchmatchingresult in Dispatchmatchingresults.query.group_by(Dispatchmatchingresults.date)]

    # soln = PyomoModel.runModel()
    # soln = soln.to_html(classes=["table","table-hover"])

    if request.method == 'POST':
        sell = []
        supplierSurplus = None
        buy = []
        demandSurplus = None
        #get matched buyers
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