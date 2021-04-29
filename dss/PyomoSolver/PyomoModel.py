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


def runModel():
    originalPath = os.getcwd()
    os.chdir('dss/PyomoSolver')

    base_data = DataView.from_excel('demo_case_data.xlsx', ['entity', 'material'])
    os.chdir(originalPath)
    
    agent = base_data['entity']
    agent = agent.rename(columns={'entity': 'name'})

    material = base_data['material']
    material = material.rename(columns={'material': 'name'})

    supply = base_data['industry_supply']
    supply.index.names = ['agent_id', 'material_id']

    demand = base_data['industry_demand']
    demand.index.names = ['agent_id', 'material_id']

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

    # declare decision variables
    model.supply = Var(E,domain=NonNegativeReals)
    model.demand = Var(E,domain=NonNegativeReals)



    # declare objective
    r_p = supply.reserve_price
    r_c = demand.reserve_price
    mu = distance.distance
    tau = supply.delivery_fee

    #Objective function
    # Objective = producer_surplus + consumer_surplus - delivery_fees
    model.surplus = Objective(expr = 
        sum(-r_p[i,m] * model.supply[i,j,m] for i,j,m in E)                #producer surplus
        +  sum(r_c[j,m] * model.demand[i,j,m] for i,j,m in E)              #consumer surplus
        -  sum(mu[i,j] * tau[i,m] * model.demand[i,j,m] for i,j,m in E)    #delivery fees
        ,sense = maximize)


    # declare constraints
    S_bar = supply.quantity
    D_bar = demand.quantity

    # Constraints

    IM = {(i,m) for i,_,m in E if (i,m) in supply.index}
    model.supply_capacity = ConstraintList()
    for i,m in IM:
        E_im = edges.loc[idx[i,:,m], :].index
        x_im = sum( model.supply[i,j,m] for i,j,m in E_im) <= S_bar[i,m]
        model.supply_capacity.add(x_im)

    JM = {(j,m) for _,j,m in edges.index if (j,m) in demand.index}
    model.demand_capacity = ConstraintList()
    for j,m in JM:
        E_jm = edges.loc[idx[:,j,m], :].index
        x_jm = sum(model.demand[i,j,m] for i,j,m in E_jm) <= D_bar[j,m]
        model.demand_capacity.add(x_jm)


    model.market_equilibrium = ConstraintList()
    for i,j,m in edges.index:
        x_ijm = model.demand[i,j,m] - model.supply[i,j,m] == 0
        model.market_equilibrium.add(x_ijm)

    # solve
    
    SolverFactory('cbc').solve(model).write()
    


    demand_quantity = []
    for i,j,m in E:
        demand_quantity.append(model.demand[i,j,m]())

    # get market equilibrium
    market_equilibrium_val = []
    for index in model.market_equilibrium:
        market_equilibrium_val.append(-model.dual[model.market_equilibrium[index]])
        

    soln = pd.DataFrame(
        data = map(list, zip(*[market_equilibrium_val,demand_quantity])), #transpose data
        index = pd.MultiIndex.from_tuples(E, names=['producer_id', 'consumer_id', 'material_id']),
        columns = ['price','quantity'],
    )
    soln = soln[soln!=0].dropna()
    
    return soln