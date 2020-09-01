from collections import *
import re as re
import math as math
import random as random
import json as json

typeWordDDict = defaultdict(list)
wordTypeDict = {}
csvWordList = []


class model():


    def __init__(self, parsedSL: list, catagorySD: dict):
        self.sMarkov = defaultdict(lambda: defaultdict(int))
        self.parsedSL = parsedSL
        self.catagorySD = catagorySD
        for sentence in self.parsedSL:
            x = 0
            for word in sentence:
                if x == 0:
                    self.sMarkov['>'][word] += 1
                    prevWord = word
                    x += 1
                elif x == len(sentence)-1:
                    self.sMarkov[prevWord][word] += 1
                    self.sMarkov[word]['<'] += 1
                    x += 1
                else:
                    self.sMarkov[prevWord][word] += 1
                    prevWord = word
                    x += 1

        self.wTcMarkov = defaultdict(lambda: defaultdict(int))
        for sentence in self.parsedSL:
            x = 0
            for word in sentence:
                if x == 0:
                    self.wTcMarkov['>'][self.catagorySD.get(word)] += 1
                    prevWord = word
                    x += 1
                elif x == len(sentence)-1:
                    self.wTcMarkov[prevWord][self.catagorySD.get(word)] += 1
                    self.wTcMarkov[self.catagorySD.get(word)]['<'] += 1
                    x += 1
                else:
                    self.wTcMarkov[prevWord][self.catagorySD.get(word)] += 1
                    prevWord = word
                    x += 1
        print(list(self.wTcMarkov['boris'].items()))


    def generateSentence(self, sentenceLength: int) -> str:
        l = sentenceLength
        sentence = ''
        choices = []
        x = 0

        while True:
            if x == 0:
                for word in list(self.sMarkov['>'].items()):
                    for y in range(word[1]):
                        choices.append(word[0])
                word = random.choice(choices)
                sentence += '%s ' %(word)
                prevWord = word
            elif prevWord == '<':
                sentence = sentence.replace(' <', '...')
                break
            else:
                choices = []
                for word in list(self.sMarkov[prevWord].items()):
                    for y in range(word[1]):
                        choices.append(word[0])
                word = random.choice(choices)
                sentence += '%s ' %(word)
                prevWord = word
            x += 1

        return sentence


def initializeMain():
    global typeWordDDict
    global wordTypeDict
    global csvWordList

    with open('word_catagories.json', 'r') as x:
        wordTypeDict = json.load(x)

    with open('catagories_words.json', 'r') as x:
        typeWordDDict = json.load(x)


def sampleSentenceParser(fileName: str, sentenceBreak: str) -> list:
    fileText = ''
    parsedSentenceList = []
    sentenceNumber = 0
    currentSentence = []
    word = ''


    with open(fileName, 'r') as x:
        fileText = str(x.read())
    #try:
    #    with open(fileName, 'r') as x:
    #        fileText = str(x.read())
    #except:
    #    print('Error with reading file %s' %fileName)

    for char in fileText:
        if char == sentenceBreak and (len(word) > 0 or len(currentSentence[-1:])):
            if len(word) > 0 : currentSentence.append(word.lower())
            parsedSentenceList.append(currentSentence)
            currentSentence = []
            sentenceNumber += 1
            word = ''
        elif re.search(r'\s', char) and not re.search(r'\.|\s', prevChar):
            currentSentence.append(word.lower())
            word = ''
        elif re.search(r'\w', char):
            word += char
        else:
            pass
        prevChar = char

    print(sentenceNumber)
    return parsedSentenceList

def wordToCatagory(listToConvert: list, comparisonDictionary: dict) -> list:
    convertedList = []
    convertedSentence = []

    for sentence in listToConvert:
        convertedSentence = []
        for word in sentence:
            wordType = comparisonDictionary.get(word)
            convertedSentence.append(wordType)
        convertedList.append(convertedSentence)
    print(convertedList)
    return convertedList


cleanedWord = []
with open('sampletext.txt', 'r') as x:
    y = str(x.read())
z = y.split(' ')

for word in z:
    if re.search('[.*]', word) == None:
        cleanedWord.append(word.lower())

print(len(cleanedWord))

markovModel = defaultdict(lambda: defaultdict(int))
prevWord = cleanedWord[0]
for word in cleanedWord:
    markovModel[prevWord][word] +=1
    prevWord = word

with open('cleanedtext.txt', 'w') as x:
    xList = list(markovModel.keys())
    for word in xList:
        x.write(word + ',')

sentenceToMake = 5
firstWord = random.choice(cleanedWord)
print(firstWord)
wordsToPrint = []
wordsToPrint.append(firstWord)
for i in range(sentenceToMake):
    ii = 0
    wordsToPrint = []
    while True:
        secondWords = list(markovModel[firstWord].keys())
        if len(secondWords) == 0:
            secondWord = random.choice(cleanedWord)
        else:
            secondWord = random.choice(secondWords)
        wordsToPrint.append(secondWord)
        firstWord = secondWord
        ii += 1
        if ii > 150:
            wordsToPrint.append('...')
            break

    print(' '.join(wordsToPrint))
    print('\n')
initializeMain()
test = sampleSentenceParser('sampletext.txt', '.')
a = model(test, wordTypeDict)
print(a.generateSentence(20))
