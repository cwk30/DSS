import sqlite3
import pandas as pd

con = sqlite3.connect('site.db')
cursor = con.cursor()

# try:
#populate materials table
# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Give out Waste', 'Food', '1,2,3')")
# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Give out Waste', 'Plastic', '1,2,3,4,5')")
# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Give out Waste', 'E-Waste', '1,2,3,4')")
# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Give out Waste', 'Animal Manure', '1,2,4')")

# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Take in Resource', 'Plastic', '1,2,3,4')")
# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Take in Resource', 'Chemical', '1,2,3,4')")
# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Take in Resource', 'Metal', '1,2,3,4')")
# cursor.execute("INSERT INTO materials(`type`,`material`,`questionId`) VALUES('Take in Resource', 'Oil', '1,2,3,4')")


# print('Materials table data inserted successfully')
    
# except:
#     print('Materials table data NOT inserted')



# try:
# populate questions table
# data = pd.read_csv("questions table.csv")
# data = data.iloc[:,[0,1,2]]
# data = data.values.tolist()
# for row in data:
#   cursor.execute("INSERT INTO questions(`label`,`questionHTML`) VALUES(?, ?)", (row[1],row[2]))
# print('Questions table data inserted successfully')

# except:
#     print('Questions table data NOT inserted')




data = pd.read_csv("technology table.csv")
data = data.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11]]
data = data.values.tolist()
for row in data:
  cursor.execute("INSERT INTO technology(`materialId`,`materialRequirements`,`wasteSource`,`requiredTechnology`,`technologySuppliers`,`byProduct`,`landSpace`,`estimatedCost`,`costUnits`,`environmentalImpact`,`resourceId`) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
print('Technology table data inserted successfully')

con.commit()
con.close()
