
class CostSavings(object):
	"""docstring for CostSavings"""
	def __init__(self, sell=None, buy=None):
		super(CostSavings, self).__init__()

		self.sell = sell
		self.buy = buy
		
		if sell:
			self.wasteName = sell.materialSupplyName()
			self.sellReserve = sell.supplierReserve()
			self.surplus = sell.supplierSurplus()

		if buy:
			self.wasteName = buy.materialSupplyName()
			self.buyReserve = buy.demandReserve()
			self.surplus = buy.demandSurplus()
			self.distance = buy.transportDist()
			self.transportationCost = buy.transportationCost()


        
        





