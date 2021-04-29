
#super class
class Waste(object):
    """docstring for Waste"""
    def __init__(self, materialId, formData):
        super(Waste, self).__init__()
        self.materialId = int(materialId)
        self.formData = formData

    def getId(self):
        if self.materialId == 1:
            questionCode = Food(self.materialId, self.formData).generateId()
        elif self.materialId == 3:
            questionCode = Ewaste(self.materialId, self.formData).generateId()
        elif self.materialId == 4:
            questionCode = AnimalManure(self.materialId, self.formData).generateId()
        elif self.materialId == 12:
            questionCode = WoodWaste(self.materialId, self.formData).generateId()
        elif self.materialId == 13:
            questionCode = Biochar(self.materialId, self.formData).generateId()
        else:
            questionCode = Others(self.materialId, self.formData).generateId()
        return questionCode

#sub classes
class Food(Waste):
    """docstring for Food"""
    def __init__(self, materialId, formData):
        super().__init__(materialId,formData)
        self.homogeneity = '_'
        self.CHNType = '_'
        self.CRatio = '__'
        self.HRatio = '__'
        self.NRatio = '__'
        self.proteinType = '_'
        self.proteinRatio = '__'
        self.cellulosic = '_'
        self.shellAndBones = '__'
        self.moistureType = '_'
        self.moistureContent = '__'
        self.saltType = '_'
        self.saltContent = '__'
        self.pHType = '_'
        self.phValue = '__'
        self.particleSize = '_'

    def generateId(self):
        self.populate()
        questionCode = ["F" + self.homogeneity 
        + self.CHNType + self.CRatio + self.HRatio + self.NRatio 
        + self.proteinType + self.proteinRatio
        + self.cellulosic
        + self.shellAndBones
        + self.moistureType + self.moistureContent
        + self.saltType + self.saltContent
        + self.pHType + self.phValue
        + self.particleSize]
        return ''.join(map(str, questionCode))

    def populate(self):
        #get from the food breakdown
        # self.homogeneity = self.formData.form['Q1']
        
        self.CHNType = self.formData.form['Q2YesNo']
        if self.CHNType == '1':
            #for actual CHN ratio
            CHN = list(map(int,self.formData.form['Q2_chn'].split(':')))
            total = sum(CHN)
            self.CRatio = str(round((CHN[0]/total)*100)).zfill(2)
            self.HRatio = str(round((CHN[1]/total)*100)).zfill(2)
            self.NRatio = str(round((CHN[2]/total)*100)).zfill(2)
        else:
            #for estimated CHN ratio
            pass
        #protein placeholder
        self.cellulosic = self.formData.form['Q6']
        #shell&bones placeholder
        #moisture placeholder
        #salt placeholder
        if self.formData.form['Q5'] == '4': #known value
            self.pHType = '1'
            self.phValue = str(int(self.formData.form['Q5pH'])).zfill(2) 
        elif self.formData.form['Q5'] == '1': #yes
            self.pHType = '2'
            #phValue placeholder
        elif self.formData.form['Q5'] == '2': #no
            self.pHType = '2'
            self.phValue = '07'
        else: #not sure
            self.pHType = '2'
            #phValue placeholder
        self.particleSize = self.formData.form['Q7']
        return










class Ewaste(Waste):
    """docstring for Ewaste"""
    def __init__(self, materialId, formData):
        super().__init__(materialId,formData)
        self.RoHS = '_'
        self.homogeneity = '_'
        self.type = '_'
        self.kind = '__'
        self.parts = '__' 

    def generateId(self):
        self.populate()
        questionCode = ["3" + self.RoHS
        + self.homogeneity
        + self.type
        + self.kind
        + self.parts]
        return ''.join(map(str, questionCode))

    def populate(self):
        self.RoHS = self.formData.form['Q1']
        self.homogeneity = self.formData.form['Q2']
        self.type = self.formData.form['Q3']
        self.kind = self.formData.form['Q4']
        self.parts = self.formData.form['Q5']
        return





class AnimalManure(Waste):
    """docstring for AnimalManure"""
    def __init__(self, materialId, formData):
        super().__init__(materialId,formData)
        self.category = '_'
        self.homogeneity = '_'
        self.moistureType = '_'
        self.moistureContent = '__'
        self.CHNType = '_'
        self.CRatio = '__'
        self.HRatio = '__'
        self.NRatio = '__'
        self.contaminantType = '_'
        self.contaminantCu = '__'
        self.contaminantZn = '__'
        self.contaminantAs = '__'
        self.contaminantPb = '__'
        self.contaminantCd = '__'
        self.contaminantCr = '__'
        

    def generateId(self):
        self.populate()
        questionCode = ["A" + self.category 
        + self.homogeneity
        + self.moistureType + self.moistureContent
        + self.CHNType + self.CRatio + self.HRatio + self.NRatio 
        + self.contaminantType + self.contaminantCu + self.contaminantZn + self.contaminantAs + self.contaminantPb + self.contaminantCd + self.contaminantCr]
        return ''.join(map(str, questionCode))

    def populate(self):
        self.category = self.formData.form['Q1']
        self.homogeneity = self.formData.form['Q2']
        
        if self.formData.form['Q3'] == '0':
            self.moistureType = '1'
            self.moistureContent = str(int(self.formData.form['Q3Moisture'])).zfill(2)
        else:
            self.moistureType = '2'
            self.moistureContent = self.formData.form['Q3']


        
        self.CHNType = self.formData.form['Q4YesNo']
        self.contaminantType = self.formData.form['Q4YesNo']
        if self.CHNType == '1':
            #for actual CHN ratio
            CHN = list(map(int,self.formData.form['Q4_chn'].split(':')))
            total = sum(CHN)
            self.CRatio = str(round((CHN[0]/total)*100)).zfill(2)
            self.HRatio = str(round((CHN[1]/total)*100)).zfill(2)
            self.NRatio = str(round((CHN[2]/total)*100)).zfill(2)
            
            self.contaminantType = '1'
            self.contaminantCu = self.formData.form['Q4_Cu'].zfill(2)
            self.contaminantZn = self.formData.form['Q4_Zn'].zfill(2)
            self.contaminantAs = self.formData.form['Q4_As'].zfill(2)
            self.contaminantPb = self.formData.form['Q4_Pb'].zfill(2)
            self.contaminantCd = self.formData.form['Q4_Cd'].zfill(2)
            self.contaminantCr = self.formData.form['Q4_Cr'].zfill(2)
        else:
            #for estimated CHN ratio
            #for estimated contaminants
            pass
        return


class WoodWaste(Waste):
    """docstring for WoodWaste"""
    def __init__(self, materialId, formData):
        super().__init__(materialId,formData)
        self.category = '_'
        self.homogeneity = '_'
        self.moistureType = '_'
        self.moistureContent = '__'
        self.size = '_'
        self.CHNType = '_'
        self.CRatio = '__'
        self.HRatio = '__'
        self.NRatio = '__'
        self.contaminantType = '_'
        self.contaminantCu = '__'
        self.contaminantZn = '__'
        self.contaminantAs = '__'
        self.contaminantPb = '__'
        self.contaminantCd = '__'
        self.contaminantCr = '__'
        

    def generateId(self):
        self.populate()
        questionCode = ["W" + self.category 
        + self.homogeneity
        + self.moistureType + self.moistureContent
        + self.size
        + self.CHNType + self.CRatio + self.HRatio + self.NRatio 
        + self.contaminantType + self.contaminantCu + self.contaminantZn + self.contaminantAs + self.contaminantPb + self.contaminantCd + self.contaminantCr]
        return ''.join(map(str, questionCode))

    def populate(self):
        self.category = self.formData.form['Q1']
        self.homogeneity = self.formData.form['Q2']
        
        if self.formData.form['Q3'] == '0':
            self.moistureType = '1'
            self.moistureContent = str(int(self.formData.form['Q3Moisture'])).zfill(2)
        else:
            self.moistureType = '2'
            self.moistureContent = self.formData.form['Q3']

        self.size = self.formData.form['Q4']
        
        self.CHNType = self.formData.form['Q5YesNo']
        self.contaminantType = self.formData.form['Q5YesNo']
        if self.CHNType == '1':
            #for actual CHN ratio
            CHN = list(map(int,self.formData.form['Q5_chn'].split(':')))
            total = sum(CHN)
            self.CRatio = str(round((CHN[0]/total)*100)).zfill(2)
            self.HRatio = str(round((CHN[1]/total)*100)).zfill(2)
            self.NRatio = str(round((CHN[2]/total)*100)).zfill(2)
            
            self.contaminantType = '1'
            self.contaminantCu = self.formData.form['Q5_Cu'].zfill(2)
            self.contaminantZn = self.formData.form['Q5_Zn'].zfill(2)
            self.contaminantAs = self.formData.form['Q5_As'].zfill(2)
            self.contaminantPb = self.formData.form['Q5_Pb'].zfill(2)
            self.contaminantCd = self.formData.form['Q5_Cd'].zfill(2)
            self.contaminantCr = self.formData.form['Q5_Cr'].zfill(2)
        else:
            #for estimated CHN ratio
            #for estimated contaminants
            pass
        return



class Biochar(Waste):
    """docstring for Biochar"""
    def __init__(self, materialId, formData):
        super().__init__(materialId,formData)
        self.category = '_'
        self.size = '_'
        self.moistureType = '_'
        self.moistureContent = '__'
        self.surfaceAreaType = '_'
        self.surfaceArea = '____'
        self.ash = '_'
        self.contaminantCu = '__'
        self.contaminantZn = '__'
        self.contaminantAs = '__'
        self.contaminantPb = '__'
        self.contaminantCd = '__'
        self.contaminantCr = '__'
        

    def generateId(self):
        self.populate()
        questionCode = ["W" + self.category 
        + self.size
        + self.moistureType + self.moistureContent
        + self.surfaceAreaType + self.surfaceArea
        + self.ash
        + self.contaminantCu + self.contaminantZn + self.contaminantAs + self.contaminantPb + self.contaminantCd + self.contaminantCr]
        return ''.join(map(str, questionCode))

    def populate(self):
        self.category = self.formData.form['Q1']
        self.size = self.formData.form['Q2']
        
        if self.formData.form['Q3'] == '0':
            self.moistureType = '1'
            self.moistureContent = str(int(self.formData.form['Q3Moisture'])).zfill(2)
        else:
            self.moistureType = '2'
            self.moistureContent = self.formData.form['Q3']

        if self.formData.form['Q4'] == '0':
            self.surfaceAreaType = '1'
            self.surfaceArea = str(int(self.formData.form['Q4SurfaceArea'])).zfill(4)
        else:
            self.surfaceAreaType = '2'
            self.surfaceArea = self.formData.form['Q4']
        
        self.ash = self.formData.form['Q5']        
        self.contaminantCu = self.formData.form['Q6_Cu'].zfill(2)
        self.contaminantZn = self.formData.form['Q6_Zn'].zfill(2)
        self.contaminantAs = self.formData.form['Q6_As'].zfill(2)
        self.contaminantPb = self.formData.form['Q6_Pb'].zfill(2)
        self.contaminantCd = self.formData.form['Q6_Cd'].zfill(2)
        self.contaminantCr = self.formData.form['Q6_Cr'].zfill(2)

        return


class Others(Waste):
    """docstring for Others"""
    def __init__(self, materialId, formData):
        super().__init__(materialId,formData)

    def generateId(self):
        questionCode = str(self.materialId)
        for question in self.formData.form:
            if question != 'description':
                questionCode += ''.join([str(elem) for elem in self.formData.form.getlist(question)]) 
        return questionCode
        

        