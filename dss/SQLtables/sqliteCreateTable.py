import sqlite3
import os

os.chdir('..')

con = sqlite3.connect('site.db')
cursor = con.cursor()

try:
#create matching table
	cursor.execute("""CREATE TABLE Materials (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	                type TEXT,
	                material TEXT,
	                questionId TEXT
	                )""")

	print('Materials table created successfully')
    
except:
    print('Materials table NOT created')
con.commit()


try:
#create questions table
	cursor.execute("""CREATE TABLE Questions (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	                label TEXT,
	                questionHTML TEXT
	                )""")

	print('Questions table created successfully')
    
except:
    print('Questions table NOT created')
con.commit()


try:
#create give out waste table
	cursor.execute("""CREATE TABLE GiveOutWaste (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					materialId INTEGER NOT NULL,
					questionCode TEXT NOT NULL,
	                reportCode TEXT,
	                userId INTEGER NOT NULL,
	                description TEXT,

	                FOREIGN KEY(materialId) REFERENCES Materials(id)
	                FOREIGN KEY(userId) REFERENCES user(id)
	                )""")

	print('GiveOutWaste table created successfully')
    
except:
    print('GiveOutWaste table NOT created')
con.commit()

try:
#create take in resource table
	cursor.execute("""CREATE TABLE TakeInResource (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					materialId INTEGER NOT NULL,
					questionCode TEXT NOT NULL,
	                userId INTEGER NOT NULL,
	                description TEXT,

	                FOREIGN KEY(materialId) REFERENCES Materials(id)
	                FOREIGN KEY(userId) REFERENCES user(id)
	                )""")

	print('TakeInResource table created successfully')
    
except:
    print('TakeInResource table NOT created')
con.commit()

try:
#create material recovery supplier table
	cursor.execute("""CREATE TABLE Supplier (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					materialId INTEGER NOT NULL,
					suppliedMaterials TEXT NOT NULL,
	                userId INTEGER NOT NULL,
	                description TEXT,

	                FOREIGN KEY(materialId) REFERENCES Materials(id)
	                FOREIGN KEY(suppliedMaterials) REFERENCES Materials(id)
	                FOREIGN KEY(userId) REFERENCES user(id)
	                )""")

	print('Supplier table created successfully')
    
except:
    print('Supplier table NOT created')
con.commit()

try:
#create technology table
	cursor.execute("""CREATE TABLE Technology (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					materialId INTEGER,
					materialRequirements TEXT,
					wasteSource TEXT NOT NULL,
	                requiredTechnology TEXT NOT NULL,
	                technologySuppliers TEXT NOT NULL,
	                byProduct TEXT NOT NULL,
	                landSpace INTEGER NOT NULL,
	                estimatedCost INTEGER NOT NULL,
	                costUnits TEXT,
	                environmentalImpact INTEGER NOT NULL,
	                resourceId INTEGER,

	                FOREIGN KEY(materialId) REFERENCES Materials(id)
	                FOREIGN KEY(resourceId) REFERENCES Materials(id)
	                
	                )""")

	print('Technology table created successfully')
    
except:
    print('Technology table NOT created')
con.commit()

try:
#create technology breakdown table
	cursor.execute("""CREATE TABLE TechnologyBreakdown (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					technologyId INTEGER NOT NULL,
					carouselHTML TEXT,
					website TEXT,
					specifications TEXT,
	                description TEXT,
	                features TEXT,
	                suitableSubstrates TEXT, 
	                realisedProject TEXT,
	                

	                FOREIGN KEY(technologyId) REFERENCES Technology(id)
	                
	                )""")

	print('TechnologyBreakdown table created successfully')
    
except:
    print('TechnologyBreakdown table NOT created')
con.commit()


try:
#create TechnologyCode table
	cursor.execute("""CREATE TABLE TechnologyCode (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					technologyId INTEGER NOT NULL,
					wasteCode TEXT,
					resourceCode TEXT,


	                FOREIGN KEY(technologyId) REFERENCES Technology(id)
	                
	                )""")

	print('TechnologyCode table created successfully')
    
except:
    print('TechnologyCode table NOT created')
con.commit()


try:
#create DispatchMatchingResults table
	cursor.execute("""CREATE TABLE DispatchMatchingResults (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					producerId INTEGER NOT NULL,
					consumerId INTEGER NOT NULL,
					materialId INTEGER NOT NULL,
					price REAL NOT NULL, 
					quantity REAL NOT NULL,
					date TEXT NOT NULL,


	                FOREIGN KEY(supplyId) REFERENCES DispatchMatchingSupply(id),
	                FOREIGN KEY(demandId) REFERENCES DispatchMatchingDemand(id)
	                
	                )""")

	print('DispatchMatchingResults table created successfully')
    
except:
    print('DispatchMatchingResults table NOT created')
con.commit()


try:
#create DispatchMatchingSupply table
	cursor.execute("""CREATE TABLE DispatchMatchingSupply (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					userId INTEGER NOT NULL,
					giveOutWasteId INTEGER NOT NULL,
					quantity REAL NOT NULL,
					reservePrice REAL NOT NULL, 
					deliveryFee REAL NOT NULL,
					matchedFlag INTEGER NOT NULL,


	                FOREIGN KEY(userId) REFERENCES User(id),
	                FOREIGN KEY(giveOutWasteId) REFERENCES GiveOutWaste(id)

	                )""")

	print('DispatchMatchingSupply table created successfully')
    
except:
    print('DispatchMatchingSupply table NOT created')
con.commit()

try:
#create DispatchMatchingDemand table
	cursor.execute("""CREATE TABLE DispatchMatchingDemand (
					id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
					userId INTEGER NOT NULL,
					takeInResourceId INTEGER NOT NULL,
					quantity REAL NOT NULL,
					reservePrice REAL NOT NULL, 
					matchedFlag INTEGER NOT NULL,


	                FOREIGN KEY(userId) REFERENCES User(id),
	                FOREIGN KEY(takeInResourceId) REFERENCES TakeInResource(id)
	                
	                )""")

	print('DispatchMatchingDemand table created successfully')
    
except:
    print('DispatchMatchingDemand table NOT created')
con.commit()

try:
#create Distance table
	cursor.execute("""CREATE TABLE Distance (
					postalCode1 INTEGER NOT NULL,
					postalCode2 INTEGER NOT NULL,
					distance REAL NOT NULL,
					

	                PRIMARY KEY (postalCode1, postalCode2)
	                
	                )""")

	print('Distance table created successfully')
    
except:
    print('Distance table NOT created')
con.commit()



con.close()
