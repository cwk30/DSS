from dss.models import Sample
import pandas as pd
from collections import defaultdict
from sqlalchemy.inspection import inspect
import math

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
        elif self.materialId == 14:
            questionCode = RSPFood(self.materialId, self.formData).generateId()
        else:
            questionCode = Others(self.materialId, self.formData).generateId()
        return questionCode

#sub classes
class RSPFood(Waste):
    """Q44,45,46,47,51,52,53"""
    """docstring for RSP/Organic Waste/Food Waste"""
    def __init__(self, materialId, formData):
        super().__init__(materialId,formData)
        
        self.CRatiomin = '_'
        self.CRatiomax = '_'
        self.NRatiomin = '_'
        self.NRatiomax = '_'
        self.Moisturemin = '_'
        self.Moisturemax = '_'
        self.pHmin = '_'
        self.pHmax = '_'
        self.cellulosicmin = '_'
        self.cellulosicmax = '_'
        self.particleSizemin = '_'
        self.particleSizemax = '_'
        self.unacceptableshells = '_'
        self.unacceptableshellspercent = '__'
        self.unacceptablebones = '_'
        self.unacceptablebonespercent = '__'
        self.unacceptablebamboo = '_'
        self.unacceptablebamboopercent = '__'
        self.unacceptablebanana = '_'
        self.unacceptablebananaspercent = '__'
        self.unacceptableothers = '_'
        self.unacceptableotherspercent = '__'
        self.contaminantCRatiomin = '_'
        self.contaminantCRatiomax = '_'
        self.contaminantNRatiomin = '_'
        self.contaminantNRatiomax = '_'
        self.contaminantMoisturemin = '_'
        self.contaminantMoisturemax = '_'
        self.contaminantpHmin = '_'
        self.contaminantpHmax = '_'
        self.contaminantCellulosicmin = '_'
        self.contaminantCellulosicmax = '_'
        self.contaminantparticleSizemin = '_'
        self.contaminantparticleSizemax = '_'
        self.byproductBiogas = '_'
        self.byproductChemical = '_'
        self.byproductMetal = '_'
        self.byproductBiochar = '_'
        self.byproductDigestate = '_'
        self.byproductOil = '_'
        self.byproductOthers = '_'
        self.outputBiogas = '_'
        self.outputDigestate = '_'
        self.outputDeviation = '_'


    def generateId(self):
        error=0
        error=self.populate()
        questionCode = ["F" + 
        self.acceptablemeat +
        self.acceptablefruit +
        self.acceptabledairy +
        self.acceptableeggs +
        self.acceptablebread +
        self.acceptablerice +
        self.acceptableuneaten +
        self.acceptabletea +
        self.acceptableall +
        self.acceptableothers +
        self.CRatiomin +
        self.CRatiomax +
        self.NRatiomin +
        self.NRatiomax +
        self.Moisturemin +
        self.Moisturemax +
        self.pHmin +
        self.pHmax +
        self.cellulosicmin +
        self.cellulosicmax +
        self.particleSizemin +
        self.particleSizemax +
        self.unacceptableshells +
        self.unacceptablebones +
        self.unacceptablebamboo +
        self.unacceptablebanana +
        self.unacceptableothers +
        self.byproductBiogas +
        self.byproductChemical +
        self.byproductMetal +
        self.byproductBiochar +
        self.byproductDigestate +
        self.byproductOil +
        self.byproductOthers +
        self.outputBiogas +
        self.outputDigestate +
        self.outputDeviation]
        if error!="0":
            return error
        else:
            return ''.join(map(str, questionCode))

    def populate(self):
        #get from the food breakdown
        # self.homogeneity = self.formData.form['Q1']
        error="0"
        if self.formData.form['Q44_1']==1:
            self.acceptablemeat="1"
        else:
            self.acceptablemeat="0"
        
        if self.formData.form['Q44_2']==1:
            self.acceptablefruit="1"
        else:
            self.acceptablefruit="0"
        
        if self.formData.form['Q44_3']==1:
            self.acceptabledairy="1"
        else:
            self.acceptabledairy="0"
        
        if self.formData.form['Q44_4']==1:
            self.acceptableeggs="1"
        else:
            self.acceptableeggs="0"
        
        if self.formData.form['Q44_5']==1:
            self.acceptablebread="1"
        else:
            self.acceptablebread="0"
        
        if self.formData.form['Q44_6']==1:
            self.acceptablerice="1"
        else:
            self.acceptablerice="0"
        
        if self.formData.form['Q44_7']==1:
            self.acceptableuneaten="1"
        else:
            self.acceptableuneaten="0"
        
        if self.formData.form['Q44_8']==1:
            self.acceptabletea="1"
        else:
            self.acceptabletea="0"
        
        if self.formData.form['Q44_9']==1:
            self.acceptableall="1"
        else:
            self.acceptableall="0"
        
        if self.formData.form['Q44_10']==1:
            self.acceptableothers="1"
        else:
            self.acceptableothers="0"
        
        self.CRatiomin = str(self.formData.form['Q45_min_C']).zfill(2)
        self.CRatiomax = str(self.formData.form['Q45_max_C']).zfill(2)
        self.NRatiomin = str(self.formData.form['Q45_min_N']).zfill(2)
        self.NRatiomax = str(self.formData.form['Q45_max_N']).zfill(2)
        
        self.Moisturemin = str(self.formData.form['Q46_min_moisture']).zfill(2)
        self.Moisturemax = str(self.formData.form['Q46_max_moisture']).zfill(2)
        if int(self.formData.form['Q46_min_ph'])<0 or int(self.formData.form['Q46_min_ph'])>14 or int(self.formData.form['Q46_max_ph'])<0 or int(self.formData.form['Q46_max_ph'])>14:
            print('ohno')
            error="Error: Check pH value!"
        self.pHmin = str(self.formData.form['Q46_min_ph']).zfill(2)
        self.pHmax = str(self.formData.form['Q46_max_ph']).zfill(2)
        
        self.cellulosicmin = str(self.formData.form['Q46_min_Cellulosic']).zfill(2)
        self.cellulosicmax = str(self.formData.form['Q46_max_Cellulosic']).zfill(2)
        self.particleSizemin = str(self.formData.form['Q46_min_Size']).zfill(2)
        self.particleSizemax = str(self.formData.form['Q46_max_Size']).zfill(2)
        if self.formData.form['Q47_1']==1:
            self.unacceptableshells="1"
        else:
            self.unacceptableshells="0"       
        if self.formData.form['Q47_2']==1:
            self.unacceptablebones="1"
        else:
            self.unacceptablebones="0"        
        if self.formData.form['Q47_3']==1:
            self.unacceptablebamboo="1"
        else:
            self.unacceptablebamboo="0"        
        if self.formData.form['Q47_4']==1:
            self.unacceptablebanana="1"
        else:
            self.unacceptablebanana="0"       
        if self.formData.form['Q47_5']==1:
            self.unacceptableothers="1"
        else:
            self.unacceptableothers="0"              
        
        if self.formData.form['Q51_Biogas']==1:
            self.byproductBiogas="1"
        else:
            self.byproductBiogas="0"
        if self.formData.form['Q51_Chemical']==1:
            self.byproductChemical="1"
        else:
            self.byproductChemical="0"
        if self.formData.form['Q51_Metal']==1:
            self.byproductMetal="1"
        else:
            self.byproductMetal="0"
        if self.formData.form['Q51_Biochar']==1:
            self.byproductBiochar="1"
        else:
            self.byproductBiochar="0"
        if self.formData.form['Q51_Digestate']==1:
            self.byproductDigestate="1"
        else:
            self.byproductDigestate="0"
        if self.formData.form['Q51_Oil']==1:
            self.byproductOil="1"
        else:
            self.byproductOil="0"
        if self.formData.form['Q51_Others']==1:
            self.byproductOthers="1"
        else:
            self.byproductOthers="0"   
        self.outputBiogas = str(self.formData.form['Q52_biogas']).zfill(2)
        self.outputDigestate = str(self.formData.form['Q52_digestate']).zfill(2)
        self.outputDeviation = str(self.formData.form['Q52_deviation']).zfill(2)
        return error

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
            self.moistureType = '1'
            self.moistureContent = str(int(self.formData.form['Q4Moisture'])).zfill(2)
            #salt placeholder
            self.pHType = '1'
            self.phValue = str(int(self.formData.form['Q5pH'])).zfill(2) 

        else:
            samples = Sample.query.all()
            result = defaultdict(list)
            for obj in samples:
                instance = inspect(obj)
                for key, x in instance.attrs.items():
                    result[key].append(x.value)    
            df = pd.DataFrame(result)
            weightage=[]
            Clist=[]
            Hlist=[]
            Nlist=[]
            moisturelist=[]
            pHlist=[]
            q3=['Q3_1','Q3_2','Q3_3']
            for i in q3:
                if self.formData.form[i]!="None":
                    weightage.append(int(self.formData.form[i+'_w']))
                    Clist.append(df.at[int(self.formData.form[i]),'C'])
                    Hlist.append(df.at[int(self.formData.form[i]),'H'])
                    Nlist.append(df.at[int(self.formData.form[i]),'N'])
                    moisturelist.append(df.at[int(self.formData.form[i]),'Moisture'])
                    pHlist.append(df.at[int(self.formData.form[i]),'pH'])
            if len(weightage)>0:
                C=0
                H=0
                N=0
                moisture=0
                ph=0
                for i in range(len(weightage)):
                    #print(C)
                    #print(int((int(weightage[0])/sum(weightage))*int(Clist[i])))
                    C+=float((float(weightage[0])/sum(weightage))*int(Clist[i]))
                    H+=float((weightage[0]/sum(weightage))*int(Hlist[i]))
                    N+=float((weightage[0]/sum(weightage))*int(Nlist[i]))
                    moisture+=float((weightage[0]/sum(weightage))*int(moisturelist[i]))
                    if math.isnan(pHlist[i]):
                        pass
                    else:
                        ph+=float((weightage[0]/sum(weightage))*int(pHlist[i]))
                total=C+H+N
                self.CRatio = str(round((C/total)*100)).zfill(2)
                self.HRatio = str(round((H/total)*100)).zfill(2)
                self.NRatio = str(round((N/total)*100)).zfill(2)
                if self.formData.form['Q4'] == '4': #Liquid
                    self.moistureType = '2'
                    self.moistureContent = '75'
                elif self.formData.form['Q4'] == '3': #Wet
                    self.moistureType = '2'
                    self.moistureContent = '40'
                elif self.formData.form['Q4'] == '2': #Slightly Wet
                    self.moistureType = '2'
                    self.moistureContent = '20'
                elif self.formData.form['Q4'] == '1': #Dry
                    self.moistureType = '2'
                    self.moistureContent = '05'
                elif self.formData.form['Q4'] == '5': #not sure
                    self.moistureType = '2'
                    self.moistureContent = str(int(moisture)).zfill(2)
                elif self.formData.form['Q4'] == '6': #known value
                    self.moistureType = '1'
                    self.moistureContent = str(int(self.formData.form['Q4Moisture'])).zfill(2)

                if self.formData.form['Q5'] == '4': #known value
                    self.pHType = '1'
                    self.phValue = str(int(self.formData.form['Q5pH'])).zfill(2) 
                elif self.formData.form['Q5'] == '1': #Highly Acidic
                    self.pHType = '2'
                    self.phValue = '02'
                    #phValue placeholder
                elif self.formData.form['Q5'] == '2': #Highly Alkaline
                    self.pHType = '2'
                    self.phValue = '13'
                elif self.formData.form['Q5'] == '5': #Neutral
                    self.pHType = '2'
                    self.phValue = '07'        
                elif self.formData.form['Q5'] == '3': #not sure
                    self.pHType = '02'
                    self.phValue = str(round(ph)).zfill(2) 
        #protein placeholder
        self.cellulosic = self.formData.form['Q6']
        #shell&bones placeholder
        #moisture placeholder
        #for key in self.formData.form:
            #print(key)
        #print("Moisture: ",self.formData.form['Q4'])
        
       
            

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
        

        