import numpy as np

class TechSpecifications(object):
    """docstring for TechSpecifications"""
    def __init__(self, noOfYears, capitalCost, rawMaterialCost, utilitiesCost, maintenanceCost, 
        maintenanceFrequency, salvageValue, byproductName, percentageExtraction, percentageComposition):

        super(TechSpecifications, self).__init__()
        self.noOfYears = noOfYears
        self.capitalCost = capitalCost
        self.rawMaterialCost = rawMaterialCost
        self.utilitiesCost = utilitiesCost
        self.maintenanceCost = maintenanceCost
        self.maintenanceFrequency = maintenanceFrequency
        self.salvageValue = salvageValue
        self.byproductName = byproductName
        self.percentageExtraction = percentageExtraction
        self.percentageComposition = percentageComposition

    def cashflow(self, weightPerYear, disposalCostPerTon, discountRate, price):
        
        savingsPerTon = 0
        weightExtracted = 0
        for i in range(len(self.percentageComposition)):
            savingsPerTon += self.percentageExtraction[i]*self.percentageComposition[i]*price[i]
            weightExtracted += self.percentageExtraction[i]*self.percentageComposition[i]

        yearlySavings = weightPerYear*savingsPerTon
        yearlyDisposalCost = disposalCostPerTon*(weightPerYear - weightExtracted)
        operatingCost = self.rawMaterialCost + self.utilitiesCost

        #cashflow generation
        cashflowList = [-self.capitalCost]
        for i in range(1,self.noOfYears+1):
            cashflow = yearlySavings - operatingCost - yearlyDisposalCost
            if i in self.maintenanceFrequency: cashflow -= self.maintenanceCost
            cashflowList.append(cashflow)
        #add salvage calue
        cashflowList[-1] += self.salvageValue
        return cashflowList

    def recycleNPV(self, weightPerYear, disposalCostPerTon, discountRate, price):
        cashflowList = self.cashflow(weightPerYear, disposalCostPerTon, discountRate, price)
        NPV = np.npv(discountRate,cashflowList)
        return round(NPV,2)   

    def originalNPV(self, weightPerYear, disposalCostPerTon, discountRate):
        originalCashlowList = [-disposalCostPerTon*weightPerYear]*self.noOfYears
        originalCashlowList.insert(0,0)
        NPV = np.npv(discountRate,originalCashlowList)
        return round(NPV,2)

# #user input
# weightPerYear = 1
# disposalCostPerTon = 77.00
# discountRate = 0.0525


# #tech specifications (stored in database)
# noOfYears = 10      #machine lifespan?
# capitalCost = 50000

# rawMaterialCost = 3017.13
# utilitiesCost = 49.91
# maintenanceCost = 5000
# maintenanceFrequency = [3,7]     #list of years that machine requires maintenance
# salvageValue = 25000


# #tech output 
# #figure out how to store this in database
# byproductName = ['gold', 'silver', 'palladium']
# percentageExtraction = [0.97, 0.98, 0.93]
# percentageComposition = [0.00025, 0.0001, 0.001]


# #see if can extract from Quandl
# price = [58141868.4, 620966.57, 65073624.0]




# #driver code

# #create technology object
# tech = TechSpecifications(noOfYears, capitalCost, rawMaterialCost, utilitiesCost, maintenanceCost, 
#     maintenanceFrequency, salvageValue, byproductName, percentageExtraction, percentageComposition)

# recycleNPV = tech.recycleNPV(weightPerYear, disposalCostPerTon, discountRate, price)
# print(recycleNPV)

# originalNPV  = tech.originalNPV(weightPerYear, disposalCostPerTon, discountRate)
# print(originalNPV)
