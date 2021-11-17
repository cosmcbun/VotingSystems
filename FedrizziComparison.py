import pandas as pd
import numpy as np
from numpy.polynomial.polynomial import polyfit
import matplotlib.pyplot as plt

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

rsquared_real = (np.corrcoef(fedrizziPointsRealX, fedrizziPointsRealY)[0,1])**2
rsquared_artificial = (np.corrcoef(fedrizziPointsArtificialX, fedrizziPointsArtificialY))[0,1]**2


print("Real R^2: " + str(rsquared_real))
print("Artificial R^2: " + str(rsquared_artificial))



fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Real and Artificial Data Fedrizzi Correlation')
ax1.plot(fedrizziPointsRealX, fedrizziPointsRealY, '.')
ax1.plot(fedrizziPointsRealX, bReal + mReal*fedrizziPointsRealX, '-')
ax2.plot(fedrizziPointsArtificialX, fedrizziPointsArtificialY, '.')
ax2.plot(fedrizziPointsArtificialX, bArtificial + mArtificial*fedrizziPointsArtificialX, '-')
# plt.xlabel("Fedrizzi Score")
# plt.ylabel("Data Score")

plt.savefig('fedrizzi_comparison.png')