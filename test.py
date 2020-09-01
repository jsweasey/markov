from collections import *
import re as re
import math as math
import random as random

def listToCSV(listToConvert: list) -> str:
    csvToReturn = ''
    print(type(listToConvert[0]))
    for sentence in listToConvert:
        csvToReturn += ','.join(sentence)
        csvToReturn += ','
    return csvToReturn


def generateCSV(fileName: str, createNew: bool) -> str:
    fileText = ''
    word = ''
    csvGenerated = ''

    try:
        with open(fileName, 'r') as x:
            fileText = str(x.read())
    except:
        print('Error with reading file %s' %fileName)

    for char in fileText:
        if re.search(r'\W', char) and len(word) > 0:
            csvGenerated += word + ','
            word = ''
        elif re.search(r'\w', char):
            word += char.lower()
        else:
            pass

    if createNew:
        try:
            with open('generatedcsv.txt', 'w+') as x:
                x.write(csvGenerated)
        except:
            print('Error with creating generatedcsv.txt')

    return csvGenerated

def sampleSentenceParser(fileName: str, sentenceBreak: str) -> list:
    fileText = ''
    parsedSentenceList = []
    sentenceNumber = 0
    currentSentence = []
    word = ''

    try:
        with open(fileName, 'r') as x:
            fileText = str(x.read())
    except:
        print('Error with reading file %s' %fileName)

    for char in fileText:
        if char == sentenceBreak and (len(word) > 0 or len(currentSentence[-1:])):
            if len(word) > 0 : currentSentence.append(word)
            parsedSentenceList.append(currentSentence)
            currentSentence = []
            sentenceNumber += 1
            word = ''
        elif re.search(r'\s', char) and not re.search(r'\.|\s', prevChar):
            currentSentence.append(word)
            word = ''
        elif re.search(r'\w', char):
            word += char
        else:
            pass
        prevChar = char

    #print(sentenceNumber)
    return parsedSentenceList

a = sampleSentenceParser('sampletext.txt', '.')
b = generateCSV('sampletext.txt', True)
print(b)
