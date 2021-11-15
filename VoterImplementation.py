import copy
import math
import random
import pandas as pd
import urllib.request
from itertools import chain
from statistics import mean

##### BALLOT CLASS
class Ballot:
    def __init__(self, preferenceOrdering):
        self.preferences = preferenceOrdering
    def getPreference(self, index):
        return self.preferences[index]
    def getBallotLength(self):
        return len(self.preferences)
    def getCandidatePlacement(self, candidate):
        return self.preferences.index(candidate)
    def getPreferredCandidate(self, candidateA, candidateB):
        if self.preferences.index(candidateA) < self.preferences.index(candidateB): return candidateA
        else: return candidateB
    def removeCandidate(self, candidate):
        self.preferences.remove(candidate)
    def __repr__(self):
        return "["+" ".join(self.preferences)+"]"

##### DATAGRABBER FUNCTIONS
def grabBallots():
    elections = []
    for electionNumber in chain(range(1, 36), range(48, 100)):
        url = "https://rangevoting.org/TiData/A" + str(electionNumber) + ".HIL"
        print(url)
        file = urllib.request.urlopen(url)
        fileLen = len(urllib.request.urlopen(url).readlines())
        elections.append([])
        listValue = electionNumber
        if electionNumber > 35:
            listValue = electionNumber - 12
        for lineNum, line in enumerate(file):
            decodedLine = line.decode("utf-8")
            if lineNum == 0:
                maxCandidate = decodedLine.split(" ")[1]
                continue
            elif lineNum == fileLen - 1 or lineNum == fileLen - 2 or lineNum == fileLen - 3:
                continue
            splitLine = decodedLine.split(" ")
            ballotList = [int(candidate) - 1 for candidate in splitLine[1:-1]]
            elections[listValue-1].append(Ballot(ballotList))
    return(elections)

##### HELPER FUNCTIONS
def returnShuffledCopyOfList(l):
    lCopy = copy.copy(l)
    random.shuffle(lCopy)
    return lCopy

def generateGenericCandidates(numberOfCandidates):
    return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][:numberOfCandidates]

def generateRandomVoteSet(candidateSet, numberOfVoters):
    return [Ballot(returnShuffledCopyOfList(candidateSet)) for i in range(numberOfVoters)]

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

def generateVotingSystemWinnerHeatmap(listOfVoteSets, votingSystemsAndNames):
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

def printForSpreadsheet(listOfLines):
    for line in listOfLines:
        for element in line:
            print(element, end="\t")
        print()

def compareTwoCandidates(voteSet, candidateA, candidateB):
    countForMajority = math.floor(len(voteSet)/2+1)
    candidateAWins, candidateBWins = 0, 0
    for ballot in voteSet:
        winner = ballot.getPreferredCandidate(candidateA, candidateB)
        if winner == candidateA:
            candidateAWins+=1
            if candidateAWins >= countForMajority: return {candidateA}
        elif winner == candidateB:
            candidateBWins+=1
            if candidateBWins >= countForMajority: return {candidateB}
    return {candidateA, candidateB}

def getListOfCandidatesInElection(voteSet):
    return [voteSet[0].getPreference(i) for i in range(voteSet[0].getBallotLength())]

def removeCandidateFromElection(voteSet, candidate):
    for ballot in voteSet:
        ballot.removeCandidate(candidate)
    return voteSet

def printVotingSystemResults(voteSet, votingSystemsAndNames):
    for votingSystem in votingSystemsAndNames: print(votingSystem+":", votingSystem(voteSet))

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
        if ballot.getUnvoted():
            for vote in ballot.getUnvoted():
                scores[vote] += 1
        else:
            scores[ballot.getPreference(ballot.getBallotLength()-1)] += 1
    lowestScore = min(scores.values())
    return {candidate for candidate in scores if scores[candidate] == lowestScore}

def hareVote(voteSet):
    copiedVoteSet = copy.deepcopy(voteSet)
    return hareVoteHelper(copiedVoteSet)
def hareVoteHelper(voteSet):
    if voteSet[0].getBallotLength() == 1:
        return set(voteSet[0].getPreference(0))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            if ballot:
                scores[ballot.getPreference(0)] += 1

        highestScore = max(scores.values()) #A little optimization: if a candidate has plurality, they win autimatically
        if highestScore > len(voteSet)/2:
            for candidate in scores:
                if scores[candidate] == highestScore: return set(candidate)

        lowestScore = min(scores.values())
        for candidate in scores:
            if scores[candidate] == lowestScore:
                removeCandidateFromElection(voteSet, candidate)
        if voteSet[0].getBallotLength() == 0: return set(scores.keys())
        else: return hareVoteHelper(voteSet)

def coombsVote(voteSet): #Hare vote but you eliminate the option with the most last place votes
    copiedVoteSet = copy.deepcopy(voteSet)
    return coombsVoteHelper(copiedVoteSet)
def coombsVoteHelper(voteSet):
    if voteSet[0].getBallotLength() == 1:
        return set(voteSet[0].getPreference(0))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            scores[ballot.getPreference(ballot.getBallotLength()-1)] += 1
        highestScore = max(scores.values())
        for candidate in scores:
            if scores[candidate] == highestScore:
                removeCandidateFromElection(voteSet, candidate)
        if voteSet[0].getBallotLength() == 0: return set(scores.keys())
        else: return coombsVoteHelper(voteSet)

def bordaCountVote(voteSet):
    scores = {candidate:0 for candidate in getListOfCandidatesInElection(voteSet)}
    for ballot in voteSet:
        for ballotIndex in range(ballot.getBallotLength()):
            scores[ballot.getPreference(ballotIndex)] += getNumberOfTotalCandidates() - ballotIndex
    highestScore = max(scores.values())
    return {candidate for candidate in scores if scores[candidate] == highestScore}

def nansonVote(voteSet):
    copiedVoteSet = copy.deepcopy(voteSet)
    return nansonVoteHelper(copiedVoteSet)
def nansonVoteHelper(voteSet):
    if voteSet[0].getBallotLength() == 1:
        return set(voteSet[0].getPreference(0))
    else:
        scores = {candidate: 0 for candidate in getListOfCandidatesInElection(voteSet)}
        for ballot in voteSet:
            for ballotIndex in range(ballot.getBallotLength()):
                scores[ballot.getPreference(ballotIndex)] += ballot.getBallotLength() - ballotIndex
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
voteSet = generateRandomVoteSet(generateGenericCandidates(4), 10)

chairParadox = [Ballot(["A","B","C"]),Ballot(["B","C","A"]),Ballot(["C","A","B"])]
#print(voteSet)
#printAllVotingSystemResults(voteSet)
#print(sequentialPairwiseVote(voteSet))
#print(socialWellfareFunction(voteSet,condorcetVote))
#generateCondorcetWinnerHeatmap(7,30)
generateVotingSystemWinnerHeatmap(generateManyElections(generateGenericCandidates(5), 100, 10000), votingSystemsAndNames)
