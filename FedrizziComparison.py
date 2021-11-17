import pandas as pd
import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

systems = ["Plurality", "Antiplurality", "Hare", "Coombs", "Borda", "Nanson", "Condorcet", "Black", "Dictator"]
fedrizziPointsArtificialX = []
fedrizziPointsArtificialY = []
fedrizziPointsRealX = []
fedrizziPointsRealY = []
dfFedrizzi = pd.read_excel("Fedrizzi.xlsx", sheet_name="Similarity", header=0, index_col=0)
dfArticialVotes = pd.read_excel('Voting system similarity heatmap.xlsx', sheet_name="MonteCarlo", header=0, index_col=0)
dfRealVotes = pd.read_excel('Voting system similarity heatmap.xlsx', sheet_name="RealData", header=0, index_col=0)
# print(dfFedrizzi.index)

for system1 in systems:
    for system2 in systems:
        fedrizziPointsArtificialX.append(dfFedrizzi.loc[system1, system2])
        fedrizziPointsArtificialY.append(dfArticialVotes.loc[system1, system2])
        fedrizziPointsRealX.append(dfFedrizzi.loc[system1, system2])
        fedrizziPointsRealY.append(dfRealVotes.loc[system1, system2])
fedrizziPointsArtificialX = np.asarray(fedrizziPointsArtificialX)
fedrizziPointsArtificialY = np.asarray(fedrizziPointsArtificialY)
fedrizziPointsRealX = np.asarray(fedrizziPointsRealX)
fedrizziPointsRealY = np.asarray(fedrizziPointsRealY)

bArtificial, mArtificial = polyfit(fedrizziPointsArtificialX, fedrizziPointsArtificialY, 1)
bReal, mReal = polyfit(fedrizziPointsRealX, fedrizziPointsRealY, 1)

coefficient_of_correlation_real = np.corrcoef(fedrizziPointsRealX, fedrizziPointsRealY)
coefficient_of_correlation_artificial = np.corrcoef(fedrizziPointsArtificialX, fedrizziPointsArtificialY)


print("Real correlation coefficient: " + str(coefficient_of_correlation_real))
print("Artificial correlation coefficient : " + str(coefficient_of_correlation_artificial))



fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Real and Artificial Data Fedrizzi Correlation')
ax1.plot(fedrizziPointsRealX, fedrizziPointsRealY, '.')
ax1.plot(fedrizziPointsRealX, bReal + mReal*fedrizziPointsRealX, '-')
ax2.plot(fedrizziPointsArtificialX, fedrizziPointsArtificialY, '.')
ax2.plot(fedrizziPointsArtificialX, bArtificial + mArtificial*fedrizziPointsArtificialX, '-')
plt.xlabel("Fedrizzi Score")
plt.xlabel("Data Score")

plt.savefig('fedrizzi_comparison.png')