import random, copy

class Ballot:
    def __init__(self, preferenceOrdering):
        self.preferences = preferenceOrdering
    def getPreference(self, index):
        return self.preferences[index]
    def getBallotLength(self):
        return len(self.preferences)
    def __repr__(self):
        return "["+" ".join(self.preferences)+"]"

def returnShuffledCopy(l):
    lCopy = copy.copy(l)
    random.shuffle(lCopy)
    return lCopy

def generateRandomVoteSet(candidateSet, numberOfVoters):
    return [Ballot(returnShuffledCopy(candidateSet)) for i in range(numberOfVoters)]


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
    pass

voteSet = generateRandomVoteSet(["A", "B", "C"], 6)
print(voteSet)
print(pluralityVote(voteSet))