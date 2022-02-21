from PyomoSolver import PyomoModel
import pandas as pd
import os

report_path = 'dss/PyomoSolver/'
solution=PyomoModel.runModel()
writer = pd.ExcelWriter(os.path.join(report_path + 'solution.xlsx'), engine='xlsxwriter')
solution.to_excel(writer, sheet_name='soln',index=True)
writer.save()