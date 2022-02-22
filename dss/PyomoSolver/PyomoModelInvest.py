import matplotlib.pyplot as plt
import numpy as np

import shutil
import sys
import os.path

from pyomo.environ import *

import pandas as pd
from pandas import IndexSlice as idx
from .model import BaseModel

from .data import DataView


def runModel(budget):
    originalPath = os.getcwd()
    os.chdir('dss/PyomoSolver')
    #os.chdir('PyomoSolver')
    

    base_data = DataView.from_excel('case_data.xlsx', ['entity', 'material'])
    os.chdir(originalPath)
    
    agent = base_data['entity']
    agent = agent.rename(columns={'entity': 'name'})

    material = base_data['material']
    material = material.rename(columns={'material': 'name'})

    supply = base_data['industry_supply']
    supply.index.names = ['agent_id', 'material_id']

    demand = base_data['industry_demand']
    demand.index.names = ['agent_id', 'material_id']
    invest_demand = base_data['investment_demand']
    invest_demand.index.names = ['agent_id', 'material_id']
    demand = demand.append(invest_demand)

    invest_cost = base_data['invest_cost']
    invest_cost.index.names = ['agent_id']


    distance = base_data['distance']
    distance = distance.reset_index().melt(id_vars='entity')
    distance = distance.rename(columns={'entity': 'producer_id', 'variable': 'consumer_id', 'value': 'distance'})
    distance = distance.set_index(['producer_id', 'consumer_id'])
    distance = distance.dropna()

    edges = pd.merge(
                supply.index.to_frame(index=False, name=['producer', 'material']),
                demand.index.to_frame(index=False, name=['consumer', 'material']),
                on='material', how='inner'
            ).set_index(['producer', 'consumer', 'material'])

    # Mask out edges which are not included in the distance table
    mask = [(i,j) in distance.index for (i,j,m) in edges.index]
    edges = edges[mask]

    # Save edge list as a model attribute
    edges = edges.sort_index()

    E = edges.index



    # building the model
    model = ConcreteModel()
    model.dual = Suffix(direction=Suffix.IMPORT)

    # define parameters
    r_p = supply.reserve_price
    r_c = demand.reserve_price
    S_bar = supply.quantity
    D_bar = demand.quantity
    mu = distance.distance
    tau = supply.delivery_fee
    investment = invest_cost.invest_cost

    # declare decision variables
    model.supply = Var(E,domain=NonNegativeReals)
    model.demand = Var(E,domain=NonNegativeReals)
    model.y = Var(invest_cost.index,domain=Integers)

    #Objective function (EQUATION 1)
    model.surplus = Objective(expr = 
        sum(-r_p[i,m] * model.supply[i,j,m] for i,j,m in E)                #producer surplus
        +  sum(r_c[j,m] * model.demand[i,j,m] for i,j,m in E)              #consumer surplus
        -  sum(mu[i,j] * tau[i,m] * model.supply[i,j,m] for i,j,m in E)    #delivery fees
        ,sense = maximize)

    # Constraints
    model.supply_capacity = ConstraintList()
    model.demand_capacity = ConstraintList()
    model.demand_limit = ConstraintList()
    model.investdemand_limit = ConstraintList()
    model.investment_cost = ConstraintList()   

    # Supply capacity constraint (EQUATION 2)
    IM = {(i,m) for i,_,m in E if (i,m) in supply.index}
    for i,m in IM:
        E_im = edges.loc[idx[i,:,m], :].index
        x_im = sum( model.supply[i,j,m] for i,j,m in E_im) <= S_bar[i,m]
        model.supply_capacity.add(x_im)

    # Demand capacity constraint (EQUATION 3a)
    JM = {(j,m) for _,j,m in edges.index if (j,m) not in invest_demand.index}
    for j,m in JM:
        E_jm = edges.loc[idx[:,j,m], :].index
        x_jm = sum(model.demand[i,j,m] for i,j,m in E_jm) <= D_bar[j,m]
        model.demand_capacity.add(x_jm)

    # Demand capacity constraint (EQUATION 3b)
    JM = {(j,m) for _,j,m in edges.index if (j,m) in invest_demand.index}
    for j,m in JM:
        E_jm = edges.loc[idx[:,j,m], :].index
        x_jm = sum(model.demand[i,j,m] for i,j,m in E_jm) <= D_bar[j,m] * model.y[j]
        model.demand_capacity.add(x_jm)

        #x_jm = sum(model.demand[i,j,m] for i,j,m in E_jm) >= D_bar[j,m] * model.y[j] * 0.8
        #model.demand_limit.add(x_jm)

    #M = {m for _,_,m in edges.index}
    #for m in M:
    #    E_m = edges.loc[idx[:,:,m], :].index
    #    x_m = sum(model.demand[i,j,m] for i,j,m in E_m) <= total_industry_supply[m] - total_industry_demand[m]
    #    model.investdemand_limit.add(x_m)

    # Investment budget (EQUATION 4)
    cons = sum(investment[j] * model.y[j] for j in invest_cost.index)  <= int(budget)   #budget
    model.investment_cost.add(cons)


    # Market equilibrium constraint (EQUATION 5)
    model.market_equilibrium = ConstraintList()
    for i,j,m in edges.index:
        x_ijm = model.demand[i,j,m] - model.supply[i,j,m] == 0
        model.market_equilibrium.add(x_ijm)

    # solve

    SolverFactory('cbc').solve(model).write()

    demand_quantity = []
    for i,j,m in E:
        demand_quantity.append(model.demand[i,j,m]())

    # get market equilibrium price
    market_equilibrium_val = []
    for index in model.market_equilibrium:
        market_equilibrium_val.append(-model.dual[model.market_equilibrium[index]])
        

    soln = pd.DataFrame(
        data = map(list, zip(*[market_equilibrium_val,demand_quantity])), #transpose data
        index = pd.MultiIndex.from_tuples(E, names=['producer_id', 'consumer_id', 'material_id']),
        columns = ['price','quantity'],
    )
    soln = soln[soln!=0].dropna()
        
    print(soln)
    investment_decision = []
    for j in invest_cost.index:
        investment_decision.append((j,model.y[j]()))
    investment_decision_df = pd.DataFrame(investment_decision, columns = ['agent_id','quantity']).set_index('agent_id')
    
    print(investment_decision_df)
    
    return soln, investment_decision_df