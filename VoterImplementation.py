import copy
import math
import random
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

def generateCondorcetWinnerHeatmap(maxCandidates, maxVoters, iterationCount = 1000):
    print("Number of Voters", end="\t")
    for voterCount in range(10, maxVoters + 1, 10):
        print(voterCount, end="\t")
    for candidateCount in range(2, maxCandidates+1):
        print()
        print(candidateCount, end="\t")
        for voterCount in range(10, maxVoters+1, 10):
            winnersFound = 0
            for i in range(iterationCount):
                if condorcetVote(generateRandomVoteSet(generateGenericCandidates(candidateCount), voterCount)):
                    winnersFound+=1
            print(winnersFound/1000,end="\t")

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
            scores[ballot.getPreference(ballotIndex)] += ballot.getBallotLength() - ballotIndex
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

def printAllVotingSystemResults(voteSet):
    print("Plurality:", pluralityVote(voteSet))
    print("Antiplurality:", antipluralityVote(voteSet))
    print("Hare:", hareVote(voteSet))
    print("Coombs:", coombsVote(voteSet))
    print("Borda:", bordaCountVote(voteSet))
    print("Nanson:", nansonVote(voteSet))
    print("Condorcet:", condorcetVote(voteSet))
    print("Pairwise:", sequentialPairwiseVote(voteSet))
    print("Dictator:", dictatorshipVote(voteSet))

##### EXECUTION AREA
voteSet = generateRandomVoteSet(generateGenericCandidates(4), 10)
chairParadox = [Ballot(["A","B","C"]),Ballot(["B","C","A"]),Ballot(["C","A","B"])]
print(voteSet)
printAllVotingSystemResults(voteSet)
#print(sequentialPairwiseVote(voteSet))
#print(socialWellfareFunction(voteSet,condorcetVote))
#generateCondorcetWinnerHeatmap(20,70)