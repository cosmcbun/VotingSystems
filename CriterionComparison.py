import pandas as pd
import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt

systems = ["Plurality", "Antiplurality", "Hare", "Coombs", "Borda", "Nanson", "Condorcet", "Black", "Dictator"]
criteria = ["Monotonic", "Condorcet winner", "Majo­rity", "Condorcet loser", "Majority loser", "Mutual majority", "Smith", "ISDA", "LIIA", "Independence of clones", "Reversal symmetry", "Participation, Consistency", "Later-0‑harm", "Later-0‑help"]
criteria_dict = {criterion: [[0, 0, 0, 0], [0, 0, 0, 0]] for criterion in criteria}
dfFedrizzi = pd.read_excel("Fedrizzi.xlsx", sheet_name="Raw Data", header=0, index_col=0)
dfArtificialVotes = pd.read_excel('Voting system similarity heatmap.xlsx', sheet_name="MonteCarlo", header=0, index_col=0)
dfRealVotes = pd.read_excel('Voting system similarity heatmap.xlsx', sheet_name="RealData", header=0, index_col=0)
# print(dfFedrizzi.index)

for system1 in systems:
    for system2 in systems:
        for criterion in criteria:
            if((dfFedrizzi.loc[system1, criterion] + dfFedrizzi.loc[system2, criterion])%2):
                criteria_dict[criterion][0][2]+= (dfRealVotes.loc[system1, system2] + dfRealVotes.loc[system2, system1])/2
                criteria_dict[criterion][0][3]+= 1
                criteria_dict[criterion][1][2]+= (dfArtificialVotes.loc[system1, system2] + dfArtificialVotes.loc[system2, system1])/2
                criteria_dict[criterion][1][3]+= 1
            else:
                criteria_dict[criterion][0][0]+= (dfRealVotes.loc[system1, system2] + dfRealVotes.loc[system2, system1])/2
                criteria_dict[criterion][0][1]+= 1
                criteria_dict[criterion][1][0]+= (dfArtificialVotes.loc[system1, system2] + dfArtificialVotes.loc[system2, system1])/2
                criteria_dict[criterion][1][1]+= 1

outputList = {criterion: [0, 0] for criterion in criteria}
for criterion in criteria:
    outputList[criterion][0] = criteria_dict[criterion][0][0]/criteria_dict[criterion][0][1] - criteria_dict[criterion][0][2]/criteria_dict[criterion][0][3]
    outputList[criterion][1] = criteria_dict[criterion][1][0]/criteria_dict[criterion][1][1] - criteria_dict[criterion][1][2]/criteria_dict[criterion][1][3]

outputDf = pd.DataFrame(data=outputList)
outputDf.index = ["Real", "Artificial"]

outputDf.to_excel("CriteriaValues.xlsx")
