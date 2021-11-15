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
    def isBallotEmpty(self):
        if self.preferences: return False
        else: return True
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
def grabSomeBallots():
    elections = []
    for electionNumber in range(5):
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

def generateTwoVotingSystemComparisonHeatmapOnFakeData(system1, system2, maxCandidates, maxVoters, minCandidates = 2, minVoters = 10, iterationCount = 1000):
    listOfLines = [["Number of Voters"] + list(range(minVoters, maxVoters + 1, 10))]
    for candidateCount in range(minCandidates, maxCandidates + 1):
        line = [candidateCount]
        for voterCount in range(minVoters, maxVoters + 1, 10):
            winnersFound = 0
            for i in range(iterationCount):
                if condorcetVote(generateRandomVoteSet(generateGenericCandidates(candidateCount), voterCount)):
                    winnersFound += 1
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
    return [ballot for ballot in voteSet if not ballot.isBallotEmpty()]

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
        return set(voteSet[0].getPreference(0))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            scores[ballot.getPreference(0)] += 1

        highestScore = max(scores.values()) #A little optimization: if a candidate has plurality, they win autimatically
        if highestScore > len(voteSet)/2:
            for candidate in scores:
                if scores[candidate] == highestScore: return set(candidate)

        lowestScore = min(scores.values())
        for candidate in scores:
            if scores[candidate] == lowestScore:
                removeCandidateFromElection(voteSet, candidate)
        if voteSet[0].getNumberOfTotalCandidates() == 0: return set(scores.keys())
        else: return hareVoteHelper(voteSet)

def coombsVote(voteSet): #Hare vote but you eliminate the option with the most last place votes
    copiedVoteSet = copy.deepcopy(voteSet)
    return coombsVoteHelper(copiedVoteSet)
def coombsVoteHelper(voteSet):
    if voteSet[0].getNumberOfTotalCandidates() == 1:
        return set(voteSet[0].getPreference(0))
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
        if voteSet[0].getNumberOfTotalCandidates() == 0: return set(scores.keys())
        else: return coombsVoteHelper(voteSet)

def bordaCountVote(voteSet):
    scores = {candidate:0 for candidate in voteSet[0].getBallot()}
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
        return set(voteSet[0].getPreference(0))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            for ballotIndex in range(ballot.getBallotLength()):
                scores[ballot.getPreference(ballotIndex)] += ballot.getNumberOfTotalCandidates() - ballotIndex
        averageScore = mean(scores.values())
        if set(scores.values()) == {averageScore}: return set(scores.keys())
        for candidate in scores:
            if scores[candidate] <= averageScore:
                removeCandidateFromElection(voteSet, candidate)
        else: return nansonVoteHelper(voteSet)

def condorcetVote(voteSet):
    eligibleWinners = getListOfCandidatesInElection(voteSet)
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
        return [winningSet] + socialWellfareFunction(voteSet, votingSystem)

votingSystemsAndNames = {"Plurality": pluralityVote, "Antiplurality": antipluralityVote, "Hare": hareVote,
                         "Coombs": coombsVote, "Borda": bordaCountVote, "Nanson": nansonVote, "Condorcet": condorcetVote,
                         "Black": blackVote, "Sequential Pairwise": sequentialPairwiseVote, "Dictator": dictatorshipVote}

##### EXECUTION AREA
voteSet = generateRandomVoteSet(generateGenericCandidates(10), 100)
#voteSet = grabBallots()
chairParadox = [Ballot(["A","B","C"]),Ballot(["B","C","A"]),Ballot(["C","A","B"])]
#print(voteSet)
printVotingSystemResults(voteSet, votingSystemsAndNames)
#print(sequentialPairwiseVote(voteSet))
#print(socialWellfareFunction(voteSet,condorcetVote))
#generateCondorcetWinnerHeatmap(7,30)
#generateVotingSystemWinnerHeatmap(generateManyElections(generateGenericCandidates(30), 1000, 10000), votingSystemsAndNames)