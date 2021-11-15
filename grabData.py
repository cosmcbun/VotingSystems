import pandas as pd
import urllib.request
from itertools import chain

writer = pd.ExcelWriter('all_elections.xlsx', engine='xlsxwriter')
for electionNumber in chain(range(1, 36), range(48, 100)):
    url = "https://rangevoting.org/TiData/A" + str(electionNumber) + ".HIL"
    print(url)
    file = urllib.request.urlopen(url)
    fileLen = len(urllib.request.urlopen(url).readlines())
    listValue = electionNumber
    if electionNumber > 35:
        listValue = electionNumber - 12
    election = []
    for lineNum, line in enumerate(file):
        decodedLine = line.decode("utf-8")
        if lineNum == 0:
            maxCandidate = int(decodedLine.split(" ")[0])
            election.append([maxCandidate])
            continue
        elif (electionNumber == 1 and lineNum == fileLen - 3) or lineNum == fileLen - 1 or lineNum == fileLen - 2:
            continue
        splitLine = decodedLine.split(" ")
        ballotList = [str(int(candidate) - 1) for candidate in splitLine[1:-1]]
        if len(ballotList) == 0:
            continue
        election.append(ballotList)
        # print(ballotList)
    # print(election)
    df = pd.DataFrame(election)
    # print(df)
    df.to_excel(writer, sheet_name="Election" + str(listValue))
writer.save()