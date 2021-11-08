import copy
import math
import random

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
    def __repr__(self):
        return "["+" ".join(self.preferences)+"]"

##### HELPER FUNCTIONS
def returnShuffledCopy(l):
    lCopy = copy.copy(l)
    random.shuffle(lCopy)
    return lCopy

def generateRandomVoteSet(candidateSet, numberOfVoters):
    return [Ballot(returnShuffledCopy(candidateSet)) for i in range(numberOfVoters)]

def generateCondorcetWinnerHeatmap(maxCandidates, maxVoters):
    print("Number of Voters", end="\t")
    for voterCount in range(10, maxVoters + 1, 10):
        print(voterCount, end="\t")
    for candidateCount in range(2, maxCandidates+1):
        print()
        print(candidateCount, end="\t")
        for voterCount in range(10, maxVoters+1, 10):
            winnersFound = 0
            for i in range(1000):
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

def getCandidatesInElection(voteSet):
    return [voteSet[0].getPreference(i) for i in range(voteSet[0].getBallotLength())]

def generateGenericCandidates(numberOfCandidates):
    return ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'][:numberOfCandidates]

##### VOTING SYSTEMS
def pluralityVote(voteSet):
    scores = {}
    for ballot in voteSet:
        firstPlaceChoice = ballot.getPreference(0)
        if firstPlaceChoice not in scores: scores[firstPlaceChoice] = 1
        else: scores[firstPlaceChoice] += 1
    highestScore = max(scores.values())
    return {candidate for candidate in scores if scores[candidate] == highestScore}

def hareVote(voteSet):
    pass

def bordaCountVote(voteSet):
    scores = {candidate:0 for candidate in getCandidatesInElection(voteSet)}
    for ballot in voteSet:
        for ballotIndex in range(ballot.getBallotLength()):
            scores[ballot.getPreference(ballotIndex)] += ballot.getBallotLength() - ballotIndex
    highestScore = max(scores.values())
    return {candidate for candidate in scores if scores[candidate] == highestScore}

def condorcetVote(voteSet):
    eligibleWinners = getCandidatesInElection(voteSet)
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

def sequentialPairwiseVote(voteSet, agenda = None):
    if not agenda: agenda = getCandidatesInElection(voteSet)
    pass

##### EXECUTION AREA
voteSet = generateRandomVoteSet(generateGenericCandidates(4), 10)
print(voteSet)
print(pluralityVote(voteSet))
print(bordaCountVote(voteSet))
print(condorcetVote(voteSet))
generateCondorcetWinnerHeatmap(20,200)