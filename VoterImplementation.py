<<<<<<< HEAD
import copy
import math
import random
import pandas as pd
import urllib.request
from itertools import chain
from statistics import mean

##### BALLOT CLASS
class Ballot:
    def __init__(self, preferenceOrdering, fullCandidatesList = None):
        self.preferences = preferenceOrdering
        if fullCandidatesList is not None:
            self.fullCandidatesList = list(fullCandidatesList)
            self.candidatesNotVotedFor = set(fullCandidatesList).difference(set(preferenceOrdering))
        else:
            self.fullCandidatesList = list(preferenceOrdering)
            self.candidatesNotVotedFor = set()
    def getPreference(self, index):
        return self.preferences[index]
    def getCandidatePlacement(self, candidate):
        if candidate in self.preferenceOrdering:
            return self.preferences.index(candidate)
        else: return None
    def getNumberOfTotalCandidates(self):
        return len(self.fullCandidatesList)
    def getBallotLength(self):
        return len(self.preferences)
    def getPreferredCandidate(self, candidateA, candidateB):
        if candidateA in self.preferences:
            if candidateB in self.preferences:
                if self.preferences.index(candidateA) < self.preferences.index(candidateB): return candidateA
                else: return candidateB
            else: return candidateA
        else:
            if candidateB in self.preferences: return candidateB
            else: return None
    def removeCandidate(self, candidate):
        if candidate in self.preferences:
            self.preferences.remove(candidate)
        else:
            self.candidatesNotVotedFor.remove(candidate)
        self.fullCandidatesList.remove(candidate)
    def getSetOfCandidatesNotVotedFor(self):
        return self.candidatesNotVotedFor
    def getFullCandidatesList(self):
        return self.fullCandidatesList
    def getBallot(self):
        return self.preferences
    def __repr__(self):
        return "["+" ".join(self.preferences)+"]"

##### DATAGRABBER FUNCTIONS
def grabBallots():
    elections = []
    for electionNumber in range(87):
        df = pd.read_excel("all_elections.xlsx", sheet_name=electionNumber)
        ballots = df.values.tolist()
        elections.append([])
        for lineNum, line in enumerate(ballots):
            if lineNum == 0:
                maxCandidate = line[1]
                continue
            elections[electionNumber].append(Ballot([str(candidate) for candidate in line[1:]], range(int(maxCandidate))))
        print(elections[electionNumber])
    return elections
def grabSomeBallots(numBallots=5):
    elections = []
    for electionNumber in range(numBallots):
        df = pd.read_excel("all_elections.xlsx", sheet_name=electionNumber)
        ballots = df.values.tolist()
        elections.append([])
        for lineNum, line in enumerate(ballots):
            if lineNum == 0:
                maxCandidate = line[1]
                continue
            elections[electionNumber].append(Ballot([str(candidate) for candidate in line[1:]], range(int(maxCandidate))))
        print(elections[electionNumber])
    return elections

##### HELPER FUNCTIONS
def returnShuffledCopyOfList(l):
    lCopy = copy.copy(l)
    random.shuffle(lCopy)
    return lCopy

def generateGenericCandidates(numberOfCandidates):
    return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][:numberOfCandidates]

def generateRandomVoteSet(candidateSet, numberOfVoters, candidatesToSkip = 0):
    return [Ballot(returnShuffledCopyOfList(candidateSet)[:len(candidateSet)-candidatesToSkip], candidateSet) for i in range(numberOfVoters)]

def generateRandomVoteSetWithMissingCandidates(candidateSet, numberOfVoters):
    return [Ballot(returnShuffledCopyOfList(candidateSet)[:random.randint(1, len(candidateSet))], candidateSet) for i in range(numberOfVoters)]

def generateManyElections(candidateSet, numberOfVoters, electionCount):
    return [generateRandomVoteSet(candidateSet, numberOfVoters) for i in range(electionCount)]

def generateCondorcetWinnerHeatmap(maxCandidates, maxVoters, minCandidates = 2, minVoters = 10, iterationCount = 1000):
    listOfLines = [["Number of Voters"]+list(range(minVoters, maxVoters + 1, 10))]
    for candidateCount in range(minCandidates, maxCandidates+1):
        line = [candidateCount]
        for voterCount in range(minVoters, maxVoters+1, 10):
            winnersFound = 0
            for i in range(iterationCount):
                if condorcetVote(generateRandomVoteSet(generateGenericCandidates(candidateCount), voterCount)):
                    winnersFound+=1
            line.append(winnersFound/iterationCount)
        listOfLines.append(line)
    printForSpreadsheet(listOfLines)


def generateMultiVotingSystemComparisonHeatmap(listOfVoteSets, votingSystemsAndNames):
    allNames = list(votingSystemsAndNames.keys())
    scores = {name: {comparedName:0 for comparedName in allNames} for name in allNames}
    for voteSet in listOfVoteSets:
        winningSets = {name: votingSystemsAndNames[name](voteSet) for name in allNames}
        for system1 in scores:
            for system2 in scores[system1]:
                if winningSets[system1].issubset(winningSets[system2]):
                    scores[system1][system2] += 1
    countOfVoteSets = len(listOfVoteSets)
    listOfLines = [["How often does the left select a subset of the top?"]+allNames] + \
                  [[name]+[scores[name][comparedName]/countOfVoteSets for comparedName in allNames] for name in allNames]
    printForSpreadsheet(listOfLines)

def generateTwoVotingSystemComparisonHeatmapOnFakeData(system1, system2, maxCandidates, maxVoters,
                                                       minCandidates = 2, minVoters = 10, iterationCount = 1000):
    listOfLines = [["Initial Election Conditions"] + list(range(minVoters, maxVoters + 1, 10))]
    for candidateCount in range(minCandidates, maxCandidates + 1):
        line = [candidateCount]
        for voterCount in range(minVoters, maxVoters + 1, 10):
            winnersFound = 0
            for i in range(iterationCount):
                voteSet = generateRandomVoteSetWithMissingCandidates(generateGenericCandidates(candidateCount), voterCount)
                if system1(voteSet).issubset(system2(voteSet)): winnersFound += 1
            line.append(winnersFound / iterationCount)
        listOfLines.append(line)
    printForSpreadsheet(listOfLines)

def printForSpreadsheet(listOfLines):
    for line in listOfLines:
        for element in line:
            print(element, end="\t")
        print()

def compareTwoCandidates(voteSet, candidateA, candidateB):
    candidateAWins, candidateBWins = 0, 0
    for ballot in voteSet:
        winner = ballot.getPreferredCandidate(candidateA, candidateB)
        if winner == candidateA:
            candidateAWins+=1
        elif winner == candidateB:
            candidateBWins+=1
    if candidateAWins > candidateBWins: return {candidateA}
    elif candidateAWins < candidateBWins: return {candidateB}
    elif candidateAWins == candidateBWins: return {candidateA, candidateB}

def getListOfCandidatesInElection(voteSet):
    return voteSet[0].getFullCandidatesList()

def removeCandidateFromElection(voteSet, candidate):
    for ballot in voteSet:
        ballot.removeCandidate(candidate)

def getVoteSetWithoutEmptyBallots(voteSet):
    return [ballot for ballot in voteSet if ballot.getBallotLength() > 0]

def printVotingSystemResults(voteSet, votingSystemsAndNames):
    for votingSystem in votingSystemsAndNames: print(votingSystem+":", votingSystemsAndNames[votingSystem](voteSet))

##### VOTING SYSTEMS
def pluralityVote(voteSet):
    scores = {candidate:0 for candidate in getListOfCandidatesInElection(voteSet)}
    for ballot in voteSet:
        scores[ballot.getPreference(0)] += 1
    highestScore = max(scores.values())
    return {candidate for candidate in scores if scores[candidate] == highestScore}

def antipluralityVote(voteSet):
    scores = {candidate:0 for candidate in getListOfCandidatesInElection(voteSet)}
    for ballot in voteSet:
        if ballot.getSetOfCandidatesNotVotedFor():
            for candidate in ballot.getSetOfCandidatesNotVotedFor():
                scores[candidate] += 1
        else:
            scores[ballot.getPreference(ballot.getNumberOfTotalCandidates()-1)] += 1
    lowestScore = min(scores.values())
    return {candidate for candidate in scores if scores[candidate] == lowestScore}

def hareVote(voteSet):
    copiedVoteSet = copy.deepcopy(voteSet)
    return hareVoteHelper(copiedVoteSet)
def hareVoteHelper(voteSet):
    if voteSet[0].getNumberOfTotalCandidates() == 1:
        return set(getListOfCandidatesInElection(voteSet))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            if ballot.getBallotLength() == 0: print(voteSet)
            scores[ballot.getPreference(0)] += 1

        highestScore = max(scores.values()) #A little optimization: if a candidate has plurality, they win automatically
        if highestScore > len(voteSet)/2:
            for candidate in scores:
                if scores[candidate] == highestScore: return set(candidate)

        lowestScore = min(scores.values())
        for candidate in scores:
            if scores[candidate] == lowestScore:
                removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        if voteSet == []: return set(scores.keys())
        else: return hareVoteHelper(voteSet)

def coombsVote(voteSet): #Hare vote but you eliminate the option with the most last place votes
    copiedVoteSet = copy.deepcopy(voteSet)
    return coombsVoteHelper(copiedVoteSet)
def coombsVoteHelper(voteSet):
    if voteSet[0].getNumberOfTotalCandidates() == 1:
        return set(getListOfCandidatesInElection(voteSet))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            if ballot.getSetOfCandidatesNotVotedFor():
                for candidate in ballot.getSetOfCandidatesNotVotedFor():
                    scores[candidate] += 1
            else:
                scores[ballot.getPreference(ballot.getNumberOfTotalCandidates() - 1)] += 1
        highestScore = max(scores.values())
        for candidate in scores:
            if scores[candidate] == highestScore:
                removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        if voteSet == []: return set(scores.keys())
        else: return coombsVoteHelper(voteSet)

def bordaCountVote(voteSet):
    scores = {candidate:0 for candidate in getListOfCandidatesInElection(voteSet)}
    for ballot in voteSet:
        for ballotIndex in range(ballot.getBallotLength()):
            scores[ballot.getPreference(ballotIndex)] += ballot.getNumberOfTotalCandidates() - ballotIndex
        for candidate in ballot.getSetOfCandidatesNotVotedFor():
            scores[candidate]+=1
    highestScore = max(scores.values())
    return {candidate for candidate in scores if scores[candidate] == highestScore}

def nansonVote(voteSet):
    copiedVoteSet = copy.deepcopy(voteSet)
    return nansonVoteHelper(copiedVoteSet)
def nansonVoteHelper(voteSet):
    if voteSet[0].getNumberOfTotalCandidates() == 1:
        return set(getListOfCandidatesInElection(voteSet))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            for ballotIndex in range(ballot.getBallotLength()):
                scores[ballot.getPreference(ballotIndex)] += ballot.getNumberOfTotalCandidates() - ballotIndex
            for candidate in ballot.getSetOfCandidatesNotVotedFor():
                scores[candidate] += 1

        averageScore = mean(scores.values())
        if set(scores.values()) == {averageScore}: return set(scores.keys())

        for candidate in scores:
            if scores[candidate] <= averageScore:
                removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        return nansonVoteHelper(voteSet)

def condorcetVote(voteSet):
    eligibleWinners = getListOfCandidatesInElection(voteSet)[:]
    candidatesToBeat = {candidate:eligibleWinners[:] for candidate in eligibleWinners}
    for candidate in candidatesToBeat:
        candidatesToBeat[candidate].remove(candidate)
    while eligibleWinners and [] not in candidatesToBeat.values():
        firstCompetitor = eligibleWinners[0]
        secondCompetitor = candidatesToBeat[firstCompetitor][0]
        winner = compareTwoCandidates(voteSet, firstCompetitor, secondCompetitor)
        if firstCompetitor in winner:
            if secondCompetitor in eligibleWinners: eligibleWinners.remove(secondCompetitor)
            del candidatesToBeat[firstCompetitor][0]
        if secondCompetitor in winner: #If there's a tie, both of these can be true
            del eligibleWinners[0]
            candidatesToBeat[secondCompetitor].remove(firstCompetitor)
    return set(eligibleWinners)

def blackVote(voteSet):
    condorcetWinner = condorcetVote(voteSet)
    if condorcetWinner: return condorcetWinner
    else: return bordaCountVote(voteSet)

def sequentialPairwiseVote(voteSet, agenda = None, tiebreaker = pluralityVote):
    if not agenda: agenda = returnShuffledCopyOfList(getListOfCandidatesInElection(voteSet))
    candidatesInContention = []
    for candidate in agenda:
        candidatesInContention.append(candidate)
        if len(candidatesInContention) == 2:
            candidatesInContention = list(compareTwoCandidates(voteSet, candidatesInContention[0], candidatesInContention[1]))
        elif len(candidatesInContention) >= 3:
            copyOfVoteSet = copy.deepcopy(voteSet)
            for candidateToRemove in getListOfCandidatesInElection(voteSet):
                if candidateToRemove not in candidatesInContention:
                    removeCandidateFromElection(copyOfVoteSet, candidateToRemove)
            copyOfVoteSet = getVoteSetWithoutEmptyBallots(copyOfVoteSet)
            candidatesInContention = list(tiebreaker(copyOfVoteSet))
    return set(candidatesInContention)

def copelandVote(voteSet):  #https://en.wikipedia.org/wiki/Copeland%27s_method
    pass

def minimaxVote(voteSet):  #https://en.wikipedia.org/wiki/Minimax_Condorcet_method
    pass

def bucklinVote(voteSet):  #https://en.wikipedia.org/wiki/Bucklin_voting
    pass

def dictatorshipVote(voteSet, dictatorIndex = 0):
    return set(voteSet[dictatorIndex].getPreference(0))

def socialWellfareFunction(voteSet, votingSystem):
    winningSet = votingSystem(voteSet)
    if not winningSet:
        return [set(getListOfCandidatesInElection(voteSet))]
    elif len(winningSet) == len(getListOfCandidatesInElection(voteSet)):
        return [winningSet]
    else:
        for candidate in winningSet:
            removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        return [winningSet] + socialWellfareFunction(voteSet, votingSystem)

votingSystemsAndNames = {"Plurality": pluralityVote, "Antiplurality": antipluralityVote, "Hare": hareVote,
                         "Coombs": coombsVote, "Borda": bordaCountVote, "Nanson": nansonVote, "Condorcet": condorcetVote,
                         "Black": blackVote, "Sequential Pairwise": sequentialPairwiseVote, "Dictator": dictatorshipVote}

##### EXECUTION AREA

#print(socialWellfareFunction(voteSet,condorcetVote))
# generateCondorcetWinnerHeatmap(20,100, minCandidates=2, minVoters=80, iterationCount=100000)
=======
import copy
import math
import random
import pandas as pd
import urllib.request
from itertools import chain
from statistics import mean

##### BALLOT CLASS
class Ballot:
    def __init__(self, preferenceOrdering, fullCandidatesList = None):
        self.preferences = preferenceOrdering
        if fullCandidatesList is not None:
            self.fullCandidatesList = list(fullCandidatesList)
            self.candidatesNotVotedFor = set(fullCandidatesList).difference(set(preferenceOrdering))
        else:
            self.fullCandidatesList = list(preferenceOrdering)
            self.candidatesNotVotedFor = set()
    def getPreference(self, index):
        return self.preferences[index]
    def getCandidatePlacement(self, candidate):
        if candidate in self.preferenceOrdering:
            return self.preferences.index(candidate)
        else: return None
    def getNumberOfTotalCandidates(self):
        return len(self.fullCandidatesList)
    def getBallotLength(self):
        return len(self.preferences)
    def getPreferredCandidate(self, candidateA, candidateB):
        if candidateA in self.preferences:
            if candidateB in self.preferences:
                if self.preferences.index(candidateA) < self.preferences.index(candidateB): return candidateA
                else: return candidateB
            else: return candidateA
        else:
            if candidateB in self.preferences: return candidateB
            else: return None
    def removeCandidate(self, candidate):
        if candidate in self.preferences:
            self.preferences.remove(candidate)
        else:
            self.candidatesNotVotedFor.remove(candidate)
        self.fullCandidatesList.remove(candidate)
    def getSetOfCandidatesNotVotedFor(self):
        return self.candidatesNotVotedFor
    def getFullCandidatesList(self):
        return self.fullCandidatesList
    def getBallot(self):
        return self.preferences
    def __repr__(self):
        return "["+" ".join(self.preferences)+"]"#+"".join(self.fullCandidatesList)

##### DATAGRABBER FUNCTIONS
def grabElections(ballotCount = 87):
    elections = []
    for electionNumber in range(ballotCount):
        df = pd.read_excel("all_elections.xlsx", sheet_name=electionNumber)
        ballots = df.values.tolist()
        elections.append([])
        for lineNum, line in enumerate(ballots):
            if lineNum == 0:
                maxCandidate = line[1]
                continue
            elections[electionNumber].append(Ballot([str(int(candidate)) for candidate in line[1:] if not pd.isna(candidate)], [str(i) for i in range(int(maxCandidate))]))
    return elections

##### HELPER FUNCTIONS
def returnShuffledCopyOfList(l):
    lCopy = copy.copy(l)
    random.shuffle(lCopy)
    return lCopy

def generateGenericCandidates(numberOfCandidates):
    return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][:numberOfCandidates]

def generateRandomVoteSet(candidateSet, numberOfVoters, candidatesToSkip = 0):
    return [Ballot(returnShuffledCopyOfList(candidateSet)[:len(candidateSet)-candidatesToSkip], candidateSet) for i in range(numberOfVoters)]

def generateRandomVoteSetWithMissingCandidates(candidateSet, numberOfVoters):
    return [Ballot(returnShuffledCopyOfList(candidateSet)[:random.randint(1, len(candidateSet))], candidateSet) for i in range(numberOfVoters)]

def generateManyElections(candidateSet, numberOfVoters, electionCount):
    return [generateRandomVoteSet(candidateSet, numberOfVoters) for i in range(electionCount)]

def generateCondorcetWinnerHeatmap(maxCandidates, maxVoters, minCandidates = 2, minVoters = 10, iterationCount = 1000):
    listOfLines = [["Number of Voters"]+list(range(minVoters, maxVoters + 1, 10))]
    for candidateCount in range(minCandidates, maxCandidates+1):
        line = [candidateCount]
        for voterCount in range(minVoters, maxVoters+1, 10):
            winnersFound = 0
            for i in range(iterationCount):
                if condorcetVote(generateRandomVoteSet(generateGenericCandidates(candidateCount), voterCount)):
                    winnersFound+=1
            line.append(winnersFound/iterationCount)
        listOfLines.append(line)
    printForSpreadsheet(listOfLines)

def generateMultiVotingSystemComparisonHeatmap(listOfVoteSets, votingSystemsAndNames):
    allNames = list(votingSystemsAndNames.keys())
    scores = {name: {comparedName:0 for comparedName in allNames} for name in allNames}
    for voteSet in listOfVoteSets:
        winningSets = {name: votingSystemsAndNames[name](voteSet) for name in allNames}
        for system1 in scores:
            for system2 in scores[system1]:
                if winningSets[system1].issubset(winningSets[system2]):
                    scores[system1][system2] += 1
    countOfVoteSets = len(listOfVoteSets)
    listOfLines = [["How often does the left select a subset of the top?"]+allNames] + \
                  [[name]+[scores[name][comparedName]/countOfVoteSets for comparedName in allNames] for name in allNames]
    printForSpreadsheet(listOfLines)

def votingSystemSimilarityValue(listOfVoteSets, systemA, systemB):
    similarity = 0
    for voteSet in listOfVoteSets:
        winnerA = systemA(voteSet)
        winnerB = systemB(voteSet)
        if winnerA.issubset(winnerB): similarity += 1
        if winnerB.issubset(winnerA): similarity += 1
    return similarity / (2*len(listOfVoteSets))

def generateTwoVotingSystemComparisonHeatmapOnFakeData(system1, system2, maxCandidates, maxVoters,
                                                       minCandidates = 2, minVoters = 10, iterationCount = 1000):
    listOfLines = [["Initial Election Conditions"] + list(range(minVoters, maxVoters + 1, 10))]
    for candidateCount in range(minCandidates, maxCandidates + 1):
        line = [candidateCount]
        for voterCount in range(minVoters, maxVoters + 1, 10):
            winnersFound = 0
            for i in range(iterationCount):
                voteSet = generateRandomVoteSetWithMissingCandidates(generateGenericCandidates(candidateCount), voterCount)
                if system1(voteSet).issubset(system2(voteSet)): winnersFound += 1
            line.append(winnersFound / iterationCount)
        listOfLines.append(line)
    printForSpreadsheet(listOfLines)

def printForSpreadsheet(listOfLines):
    for line in listOfLines:
        for element in line:
            print(element, end="\t")
        print()

def compareTwoCandidates(voteSet, candidateA, candidateB):
    candidateAWins, candidateBWins = 0, 0
    for ballot in voteSet:
        winner = ballot.getPreferredCandidate(candidateA, candidateB)
        if winner == candidateA:
            candidateAWins+=1
        elif winner == candidateB:
            candidateBWins+=1
    if candidateAWins > candidateBWins: return {candidateA}
    elif candidateAWins < candidateBWins: return {candidateB}
    elif candidateAWins == candidateBWins: return {candidateA, candidateB}

def getListOfCandidatesInElection(voteSet):
    return voteSet[0].getFullCandidatesList()

def removeCandidateFromElection(voteSet, candidate):
    for ballot in voteSet:
        ballot.removeCandidate(candidate)

def getVoteSetWithoutEmptyBallots(voteSet):
    return [ballot for ballot in voteSet if ballot.getBallotLength() > 0]

def printVotingSystemResults(voteSet, votingSystemsAndNames):
    for votingSystem in votingSystemsAndNames: print(votingSystem+":", votingSystemsAndNames[votingSystem](voteSet))

##### VOTING SYSTEMS
def pluralityVote(voteSet):
    scores = {candidate:0 for candidate in getListOfCandidatesInElection(voteSet)}
    for ballot in voteSet:
        scores[ballot.getPreference(0)] += 1
    highestScore = max(scores.values())
    return {candidate for candidate in scores if scores[candidate] == highestScore}

def antipluralityVote(voteSet):
    scores = {candidate:0 for candidate in getListOfCandidatesInElection(voteSet)}
    for ballot in voteSet:
        if ballot.getSetOfCandidatesNotVotedFor():
            for candidate in ballot.getSetOfCandidatesNotVotedFor():
                scores[candidate] += 1
        else:
            scores[ballot.getPreference(ballot.getNumberOfTotalCandidates()-1)] += 1
    lowestScore = min(scores.values())
    return {candidate for candidate in scores if scores[candidate] == lowestScore}

def hareVote(voteSet):
    copiedVoteSet = copy.deepcopy(voteSet)
    return hareVoteHelper(copiedVoteSet)
def hareVoteHelper(voteSet):
    if voteSet[0].getNumberOfTotalCandidates() == 1:
        return set(getListOfCandidatesInElection(voteSet))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            if ballot.getBallotLength() == 0: print(voteSet)
            scores[ballot.getPreference(0)] += 1

        highestScore = max(scores.values()) #A little optimization: if a candidate has plurality, they win automatically
        if highestScore > len(voteSet)/2:
            for candidate in scores:
                if scores[candidate] == highestScore: return set(candidate)

        lowestScore = min(scores.values())
        for candidate in scores:
            if scores[candidate] == lowestScore:
                removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        if voteSet == []: return set(scores.keys())
        else: return hareVoteHelper(voteSet)

def coombsVote(voteSet): #Hare vote but you eliminate the option with the most last place votes
    copiedVoteSet = copy.deepcopy(voteSet)
    return coombsVoteHelper(copiedVoteSet)
def coombsVoteHelper(voteSet):
    if voteSet[0].getNumberOfTotalCandidates() == 1:
        return set(getListOfCandidatesInElection(voteSet))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            if ballot.getSetOfCandidatesNotVotedFor():
                for candidate in ballot.getSetOfCandidatesNotVotedFor():
                    scores[candidate] += 1
            else:
                scores[ballot.getPreference(ballot.getNumberOfTotalCandidates() - 1)] += 1
        highestScore = max(scores.values())
        for candidate in scores:
            if scores[candidate] == highestScore:
                removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        if voteSet == []: return set(scores.keys())
        else: return coombsVoteHelper(voteSet)

def bordaCountVote(voteSet):
    scores = {candidate:0 for candidate in getListOfCandidatesInElection(voteSet)}
    for ballot in voteSet:
        for ballotIndex in range(ballot.getBallotLength()):
            scores[ballot.getPreference(ballotIndex)] += ballot.getNumberOfTotalCandidates() - ballotIndex
        for candidate in ballot.getSetOfCandidatesNotVotedFor():
            scores[candidate]+=1
    highestScore = max(scores.values())
    return {candidate for candidate in scores if scores[candidate] == highestScore}

def nansonVote(voteSet):
    copiedVoteSet = copy.deepcopy(voteSet)
    return nansonVoteHelper(copiedVoteSet)
def nansonVoteHelper(voteSet):
    if voteSet[0].getNumberOfTotalCandidates() == 1:
        return set(getListOfCandidatesInElection(voteSet))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            for ballotIndex in range(ballot.getBallotLength()):
                scores[ballot.getPreference(ballotIndex)] += ballot.getNumberOfTotalCandidates() - ballotIndex
            for candidate in ballot.getSetOfCandidatesNotVotedFor():
                scores[candidate] += 1

        averageScore = mean(scores.values())
        if set(scores.values()) == {averageScore}: return set(scores.keys())

        for candidate in scores:
            if scores[candidate] <= averageScore:
                removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        return nansonVoteHelper(voteSet)

def condorcetVote(voteSet):
    eligibleWinners = getListOfCandidatesInElection(voteSet)[:]
    candidatesToBeat = {candidate:eligibleWinners[:] for candidate in eligibleWinners}
    for candidate in candidatesToBeat:
        candidatesToBeat[candidate].remove(candidate)
    while eligibleWinners and [] not in candidatesToBeat.values():
        firstCompetitor = eligibleWinners[0]
        secondCompetitor = candidatesToBeat[firstCompetitor][0]
        winner = compareTwoCandidates(voteSet, firstCompetitor, secondCompetitor)
        if firstCompetitor in winner:
            if secondCompetitor in eligibleWinners: eligibleWinners.remove(secondCompetitor)
            del candidatesToBeat[firstCompetitor][0]
        if secondCompetitor in winner: #If there's a tie, both of these can be true
            del eligibleWinners[0]
            candidatesToBeat[secondCompetitor].remove(firstCompetitor)
    return set(eligibleWinners)

def blackVote(voteSet):
    condorcetWinner = condorcetVote(voteSet)
    if condorcetWinner: return condorcetWinner
    else: return bordaCountVote(voteSet)

def sequentialPairwiseVote(voteSet, agenda = None, tiebreaker = pluralityVote):
    if not agenda: agenda = returnShuffledCopyOfList(getListOfCandidatesInElection(voteSet))
    candidatesInContention = []
    for candidate in agenda:
        candidatesInContention.append(candidate)
        if len(candidatesInContention) == 2:
            candidatesInContention = list(compareTwoCandidates(voteSet, candidatesInContention[0], candidatesInContention[1]))
        elif len(candidatesInContention) >= 3:
            copyOfVoteSet = copy.deepcopy(voteSet)
            for candidateToRemove in getListOfCandidatesInElection(voteSet):
                if candidateToRemove not in candidatesInContention:
                    removeCandidateFromElection(copyOfVoteSet, candidateToRemove)
            copyOfVoteSet = getVoteSetWithoutEmptyBallots(copyOfVoteSet)
            candidatesInContention = list(tiebreaker(copyOfVoteSet))
    return set(candidatesInContention)

def copelandVote(voteSet):  #https://en.wikipedia.org/wiki/Copeland%27s_method
    pass

def minimaxVote(voteSet):  #https://en.wikipedia.org/wiki/Minimax_Condorcet_method
    pass

def bucklinVote(voteSet):  #https://en.wikipedia.org/wiki/Bucklin_voting
    pass

def dictatorshipVote(voteSet, dictatorIndex = 0):
    return set(voteSet[dictatorIndex].getPreference(0))

def socialWellfareFunction(voteSet, votingSystem):
    winningSet = votingSystem(voteSet)
    if not winningSet:
        return [set(getListOfCandidatesInElection(voteSet))]
    elif len(winningSet) == len(getListOfCandidatesInElection(voteSet)):
        return [winningSet]
    else:
        for candidate in winningSet:
            removeCandidateFromElection(voteSet, candidate)
        voteSet = getVoteSetWithoutEmptyBallots(voteSet)
        return [winningSet] + socialWellfareFunction(voteSet, votingSystem)

votingSystemsAndNames = {"Plurality": pluralityVote, "Antiplurality": antipluralityVote, "Hare": hareVote,
                         "Coombs": coombsVote, "Borda": bordaCountVote, "Nanson": nansonVote, "Condorcet": condorcetVote,
                         "Black": blackVote, "Sequential Pairwise": sequentialPairwiseVote, "Dictator": dictatorshipVote}

realDataVoterDistribution, realDataCandidateDistribution = [380, 371, 981, 43, 750, 280, 79, 78, 3419, 83, 963, 76, 104, 73, 77, 129, 867, 976, 860, 2785, 741, 44, 91, 82, 183, 100, 77, 115, 68, 58, 32, 148, 9, 63, 176, 923, 575, 561, 41, 667, 460, 922, 302, 680, 306, 216, 683, 196, 199, 166, 155, 192, 195, 191, 180, 49, 86, 525, 499, 272, 525, 253, 311, 403, 213, 486, 362, 269, 902, 369, 1123, 276, 158, 157, 120, 134, 255, 365, 661, 537, 561, 579, 587, 564, 284, 279, 275], [10, 9, 15, 14, 16, 9, 17, 7, 12, 19, 10, 20, 26, 17, 21, 3, 13, 6, 7, 5, 8, 11, 29, 5, 3, 5, 6, 4, 3, 3, 4, 5, 18, 14, 17, 10, 13, 4, 6, 10, 10, 11, 10, 13, 9, 7, 7, 6, 4, 4, 7, 3, 10, 6, 14, 4, 9, 9, 8, 3, 5, 3, 4, 5, 3, 4, 8, 7, 11, 4, 4, 7, 4, 5, 4, 9, 5, 20, 14, 13, 4, 4, 7, 6, 4, 4, 4]

##### EXECUTION AREA
voteSet = generateRandomVoteSet(generateGenericCandidates(4), 10, 2)
voteSet = grabElections(1)[0]
chairParadox = [Ballot(["A","B","C"]),Ballot(["B","C","A"]),Ballot(["C","A","B"])]
#generateTwoVotingSystemComparisonHeatmapOnFakeData(pluralityVote, antipluralityVote, 10, 100, iterationCount=10)
#print(voteSet)
#printVotingSystemResults(voteSet, votingSystemsAndNames)
#elections = grabElections(1)
for ballot in voteSet:
    print(len(ballot.getSetOfCandidatesNotVotedFor()))
    print(ballot, ballot.getSetOfCandidatesNotVotedFor())
    print()
"""for x in votingSystemsAndNames:
    for y in votingSystemsAndNames:
        print(x, y, votingSystemSimilarityValue(ballots, votingSystemsAndNames[x], votingSystemsAndNames[y]))"""
#generateMultiVotingSystemComparisonHeatmap(ballots, votingSystemsAndNames)
"""for c in range(2,10):
    for v in range (5, 20):
        for elim in range (c):
            voteSet = generateRandomVoteSet(generateGenericCandidates(c), v, elim)
            print(voteSet)
            printVotingSystemResults(voteSet, votingSystemsAndNames)"""
#print(socialWellfareFunction(voteSet,condorcetVote))
#generateCondorcetWinnerHeatmap(7,30)
>>>>>>> a84eb405c49bbd282291e86304c01a5efeac40df
#generateVotingSystemWinnerHeatmap(generateManyElections(generateGenericCandidates(30), 1000, 10000), votingSystemsAndNames)