from dss import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from onemapsg import OneMap


email = "e0175262@u.nus.edu"
passw = "Password1"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True) 
    username = db.Column(db.String(20), unique=True, nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    website = db.Column(db.String(100))
    listings = db.Column(db.Integer,nullable=False)
    transacted = db.Column(db.Integer,nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    totalposts=db.Column(db.Integer,nullable=False)
    totalsuccess=db.Column(db.Integer,nullable=False)
    totalwaste=db.Column(db.Integer,nullable=False)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod 
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


    def __repr__(self): 
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self): 
        return f"Post('{self.title}', '{self.date_posted}')"

class TechnologyDB(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    userId = db.Column(db.Integer, nullable=False)
    materialId = db.Column(db.Integer)
    CRatiomin = db.Column(db.Integer)
    CRatiomax = db.Column(db.Integer)
    NRatiomin = db.Column(db.Integer)
    NRatiomax = db.Column(db.Integer)
    Moisturemin = db.Column(db.Integer)
    Moisturemax = db.Column(db.Integer)
    pHmin = db.Column(db.Integer)
    pHmax = db.Column(db.Integer)
    cellulosicmin = db.Column(db.Integer)
    cellulosicmax = db.Column(db.Integer)
    particleSizemin = db.Column(db.Integer)
    particleSizemax = db.Column(db.Integer)
    unacceptableshells = db.Column(db.Integer)
    unacceptableshellspercent = db.Column(db.Integer)
    unacceptablebones = db.Column(db.Integer)
    unacceptablebonespercent = db.Column(db.Integer)
    unacceptablebamboo = db.Column(db.Integer)
    unacceptablebamboopercent = db.Column(db.Integer)
    unacceptablebanana = db.Column(db.Integer)
    unacceptablebananapercent = db.Column(db.Integer)
    unacceptableothers = db.Column(db.Integer)
    unacceptableotherspercent = db.Column(db.Integer)
    contaminantCRatiomin = db.Column(db.Integer)
    contaminantCRatiomax = db.Column(db.Integer)
    contaminantNRatiomin = db.Column(db.Integer)
    contaminantNRatiomax = db.Column(db.Integer)
    contaminantMoisturemin = db.Column(db.Integer)
    contaminantMoisturemax = db.Column(db.Integer)
    contaminantpHmin = db.Column(db.Integer)
    contaminantpHmax = db.Column(db.Integer)
    contaminantCellulosicmin = db.Column(db.Integer)
    contaminantCellulosicmax = db.Column(db.Integer)
    contaminantparticleSizemin = db.Column(db.Integer)
    contaminantparticleSizemax = db.Column(db.Integer)
    byproductBiogas = db.Column(db.Integer)
    byproductBiogasEfficiency = db.Column(db.Integer)
    byproductBiogasCHFour = db.Column(db.Integer)
    byproductBiogasCOTwo = db.Column(db.Integer)
    ByproductChemical = db.Column(db.Integer)
    ByproductMetal = db.Column(db.Integer)
    ByproductBiochar = db.Column(db.Integer)
    ByproductDigestate = db.Column(db.Integer)
    ByproductOil = db.Column(db.Integer)
    ByproductOthers = db.Column(db.Integer)
    ByproductChemicalEfficiency = db.Column(db.Integer)
    ByproductMetalEfficiency = db.Column(db.Integer)
    ByproductBiocharEfficency = db.Column(db.Integer)
    ByproductDigestateEfficiency = db.Column(db.Integer)
    ByproductOilEfficiency = db.Column(db.Integer)
    ByproductOthersEfficiency = db.Column(db.Integer)
    TechnologyName = db.Column(db.String(100))
    AdditionalInformation = db.Column(db.String(100))
    date = db.Column(db.String(100))
    description = db.Column(db.String(100))
    cost = db.Column(db.Integer)
    capacity = db.Column(db.Integer)
    url = db.Column(db.String(100))
    forsale = db.Column(db.Integer)
    scaling = db.Column(db.Integer)
    size = db.Column(db.Integer)
    sizecost = db.Column(db.Integer)

class Materials(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    type = db.Column(db.String(100), nullable=False)
    material = db.Column(db.String(100), nullable=False)
    questionId = db.Column(db.String(100), nullable=False)

class RSP(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    maincat = db.Column(db.String(100), nullable=False)
    subcat = db.Column(db.String(100), nullable=False)
    questionId = db.Column(db.String(100), nullable=False)   

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    label = db.Column(db.String(500), nullable=False)
    questionHTML = db.Column(db.String(10000), nullable=False)

class Sample(db.Model):
    FoodItem = db.Column(db.String(100), primary_key = True)
    C = db.Column(db.Integer)
    H = db.Column(db.Integer)
    N = db.Column(db.Integer)
    Moisture = db.Column(db.Integer)
    pH = db.Column(db.Integer)

class Giveoutwaste(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    materialId = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    questionCode = db.Column(db.String(100), nullable=False)
    reportCode = db.Column(db.String(100), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime)

class Processwaste(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    materialId = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    questionCode = db.Column(db.String(100), nullable=False)
    reportCode = db.Column(db.String(100), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    technologyName = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime)    

class Takeinresource(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    materialId = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    questionCode = db.Column(db.String(100), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.DateTime)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    materialId = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    suppliedMaterials = db.Column(db.String(100), db.ForeignKey('materials.id'), nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(1000), nullable=False)

class Technology(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    materialId = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)
    materialRequirements = db.Column(db.String(100), nullable=True)
    wasteSource = db.Column(db.String(500), nullable=False)
    requiredTechnology = db.Column(db.String(500), nullable=False)
    technologySuppliers = db.Column(db.String(500), nullable=False)
    byProduct = db.Column(db.String(500), nullable=False)
    landSpace = db.Column(db.Integer, nullable=False)
    estimatedCost = db.Column(db.Integer, nullable=False)
    costUnits = db.Column(db.String(100), nullable=False)
    environmentalImpact = db.Column(db.Integer, nullable=False)
    resourceId = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False)

    def technologySuppliersHTML(self,technologySuppliers,id):
        if technologySuppliers == 'N.A.':
            return technologySuppliers
        else:
            HTML = f'<a href="/matching/technology/{id}" target="_blank" >{technologySuppliers}</a>'
            return HTML

    def potentialSellers(self,materialId):
        userId = [user.userId for user in Giveoutwaste.query.filter_by(materialId=materialId).group_by(Giveoutwaste.userId).all()]
        username = [User.query.filter_by(id=userId).first().username for userId in userId]
        usernameStr = ', '.join(username)
        return usernameStr

    def potentialSellersSupplier(self,materialId):
        userId = [user.userId for user in Supplier.query.filter_by(suppliedMaterials=materialId).group_by(Supplier.userId).all()]
        username = [User.query.filter_by(id=userId).first().username for userId in userId]
        usernameStr = ', '.join(username)
        return usernameStr  

    def potentialBuyers(self,resourceId):
        userId = [user.userId for user in Takeinresource.query.filter_by(materialId=resourceId).group_by(Takeinresource.userId).all()]
        username = [User.query.filter_by(id=userId).first().username for userId in userId]
        usernameStr = ', '.join(username)
        return usernameStr

    def potentialBuyersSupplier(self,resourceId):
        userId = [user.userId for user in Supplier.query.filter_by(suppliedMaterials=resourceId).group_by(Supplier.userId).all()]
        username = [User.query.filter_by(id=userId).first().username for userId in userId]
        usernameStr = ', '.join(username)
        return usernameStr


class Technologybreakdown(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    technologyId = db.Column(db.Integer, db.ForeignKey('Technology.id'), nullable=False)
    carouselHTML = db.Column(db.String(500))
    website = db.Column(db.String(500))
    specifications = db.Column(db.String(500))
    description = db.Column(db.Integer, nullable=False)
    features = db.Column(db.String(100))
    suitableSubstrates = db.Column(db.String(500))
    realisedProject = db.Column(db.String(500))

    def specificationsName(self, specifications):
        try:
            name = specifications.split('_')[0]
            return name
        except:
            return ''

    def specificationsPower(self, specifications):
        try:
            power = specifications.split('_')[1]
            return power
        except:
            return ''

    def featuresHTML(self, features):
        try:
            list = features.split('_')
            feature = [feature for feature in list]
            return feature
        except:
            return []

    def substratesHTML(self, substrates):
        try:
            list = substrates.split('_')
            substrate = [substrate for substrate in list]
            return substrate
        except:
            return []

class Technologycode(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    technologyId = db.Column(db.Integer, db.ForeignKey('Technology.id'), nullable=False)
    wasteCode = db.Column(db.String(500))
    resourceCode = db.Column(db.String(500))

class Dispatchmatchingresults(db.Model):
    no = None
    id = db.Column(db.Integer, primary_key = True)
    supplyId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    demandId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    materialId = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(500))
    quantity = db.Column(db.Float(500))
    date = db.Column(db.String(500))      

    def usernameSupply(self):
        userId = Dispatchmatchingsupply.query.filter_by(id=self.supplyId).first().userId
        user = User.query.filter_by(id=userId).first()
        if user.website:
            name = f'<a href={user.website} target="_blank">{user.username}</a>'
        else:
            name = user.username
        return name

    def usernameDemand(self):
        userId = Dispatchmatchingdemand.query.filter_by(id=self.demandId).first().userId
        user = User.query.filter_by(id=userId).first()
        if user.website:
            name = f'<a href={user.website} target="_blank">{user.username}</a>'
        else:
            name = user.username
        return name

    def postalCodeSupply(self):
        supply = Dispatchmatchingsupply.query.filter_by(id=self.supplyId).first()
        return supply.postalCode

    def postalCodeDemand(self):
        demand = Dispatchmatchingdemand.query.filter_by(id=self.demandId).first()
        return demand.postalCode   

    def priceDisplay(self):
        price = self.price
        return "{:.2f}".format(price) 

    def quantityDisplay(self):
        quantity = round(float(self.quantity),1)
        return quantity

    def transportationCost(self):
        supply = Dispatchmatchingsupply.query.filter_by(id=self.supplyId).first()
        return "{:.2f}".format(supply.deliveryFee )        

    def transportDist(self):


        postalCode1 = self.postalCodeSupply()
        postalCode2 = self.postalCodeDemand()

        postalCode1,postalCode2 = sorted([postalCode1,postalCode2])

        dist = Distance.query.filter_by(postalCode1=postalCode1, postalCode2=postalCode2).first()

        if dist == None:
            onemap = OneMap(email,passw)
            loc1 = onemap.search(postalCode1).results[0]
            loc2 = onemap.search(postalCode2).results[0]

            loc1_latlong = ','.join(loc1.lat_long)
            loc2_latlong = ','.join(loc2.lat_long)

            route = onemap.route(loc1_latlong, loc2_latlong, 'drive')
            dist = route.route_summary['total_distance']/1000

            data = Distance(postalCode1=postalCode1, postalCode2=postalCode2, distance=dist)
            db.session.add(data)
            db.session.commit()
        
        else:
            dist = dist.distance

        return dist

    def supplierReserve(self):
        reserve = Dispatchmatchingsupply.query.filter_by(id=self.supplyId).first().reservePrice
        return "{:.2f}".format(reserve) 

    def supplierSurplus(self):
        supply = Dispatchmatchingsupply.query.filter_by(id=self.supplyId).first()
        surplus = (float(self.price) - float(supply.reservePrice)) * float(self.quantity) 
        return "{:.2f}".format(surplus)

    def demandReserve(self):
        reserve = Dispatchmatchingdemand.query.filter_by(id=self.demandId).first().reservePrice
        return "{:.2f}".format(reserve) 

    def demandSurplus(self):
        demand = Dispatchmatchingdemand.query.filter_by(id=self.demandId).first()
        surplus = (float(demand.reservePrice)-float(self.price))*float(self.quantity) - float(self.transportDist())*float(self.transportationCost())*float(self.quantity)
        return "{:.2f}".format(surplus)

    def materialSupplyName(self):
        supply = Dispatchmatchingsupply.query.filter_by(id=self.supplyId).first()
        waste = Giveoutwaste.query.filter_by(id=supply.giveOutWasteId).first()
        return waste.description

class Dispatchmatchinginvestment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    material = db.Column(db.String(500))
    reservePrice = db.Column(db.String(500))
    cost = db.Column(db.String(500))
    capacity = db.Column(db.String(500))

class Dispatchmatchingsupply(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    giveOutWasteId = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float(500), nullable=False)
    reservePrice = db.Column(db.Float(500), nullable=False)
    deliveryFee = db.Column(db.Float(500), nullable=False)
    matchedFlag = db.Column(db.Integer, nullable=False)
    postalCode = db.Column(db.String(500))


class Dispatchmatchingdemand(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    takeInResourceId = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float(500), nullable=False)
    reservePrice = db.Column(db.Float(500), nullable=False)
    matchedFlag = db.Column(db.Integer, nullable=False)
    postalCode = db.Column(db.String(500))


class Distance(db.Model):
    postalCode1 = db.Column(db.Integer, primary_key = True)
    postalCode2 = db.Column(db.Integer, primary_key = True)
    distance = db.Column(db.Float(500), nullable=False)