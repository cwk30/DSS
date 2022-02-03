from onemapsg import OneMap

email = "e0175262@u.nus.edu"
passw = "Password1"

locSupply = '596321'
locDemand = '238858'


# print(sorted([locSupply,locDemand]))
#loc1, loc2 = [locSupply,locDemand].sort()


onemap = OneMap(email,passw)
loc1 = onemap.search(locSupply).results[0]
loc2 = onemap.search(locDemand).results[0]

loc1_latlong = ','.join(loc1.lat_long)
loc2_latlong = ','.join(loc2.lat_long)

route = onemap.route(loc1_latlong, loc2_latlong, 'drive')
print(route.route_summary)
print(route.route_summary['total_distance'])