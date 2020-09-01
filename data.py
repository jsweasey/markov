import requests as requests
import bs4 as bs4
import collections as collections
import time as time
import random as random
import json as json
import sys as sys
import re as re

path = r'C:\Users\jack\Desktop\python stuff\markov\cleanedtext.txt'
urlBase = 'https://www.lexico.com/definition/'
requestHeaders = {
'host' : 'www.lexico.com',
'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'accept-language' : 'en-GB,en;q=0.5',
'accept-encoding' : 'gzip, deflate, br',
'referer' : 'https://www.lexico.com/',
'upgrade-insecure-requests' : '1',
'dnt' : '1',
'te' : 'trailers'
}

csvWordList = []

typeWordDDict = collections.defaultdict(list)
typeWordDDict_prev = {}
wordTypeDict = {}
wordTypeDict_prev = {}
wordTypeDict_prev_keys = {}
deletedWords = {}

changeSinceSave = False


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


def initializeMain():
    global typeWordDDict
    global typeWordDDict_prev
    global wordTypeDict
    global wordTypeDict_prev
    global wordTypeDict_prev_keys
    global deletedWords
    global csvWordList
    global changeSinceSave
    csvFile = '\markov\sampletext.txt'

    loadCsv = input('Generate new CSV to check from: %s? y/n' %csvFile)
    if loadCsv.upper() == 'Y':
        generateCSV('sampletext.txt', True)
        with open('generatedcsv.txt', 'r') as x:
            csv = x.read()
        word = ''
        char = 0
        while char < len(csv):
            if csv[char] != ',':
                word += csv[char]
            else:
                csvWordList.append(word)
                word = ''
            char += 1
    else:
        with open('generatedcsv.txt', 'r') as x:
            csv = x.read()
        word = ''
        char = 0
        while char < len(csv):
            if csv[char] != ',':
                word += csv[char]
            else:
                print(word)
                csvWordList.append(word)
                word = ''
            char += 1


    with open('catagories_words.json', 'r') as x:
        typeWordDDict_prev = json.load(x)

    with open('word_catagories.json', 'r') as x:
        wordTypeDict_prev = json.load(x)

    with open('deletedwords.json', 'r') as x:
        deletedWords = json.load(x)

    wordTypeDict_prev_keys = list(wordTypeDict_prev.keys())

    for word in wordTypeDict_prev_keys:
        wordType = wordTypeDict_prev.get(word)
        wordTypeDict.update({word:wordType})

    for catagory in typeWordDDict_prev:
        for word in typeWordDDict_prev[catagory]:
            typeWordDDict[catagory].append(word)

    for word in list(wordTypeDict.keys()):
        if word not in typeWordDDict[wordTypeDict.get(word)]:
            catagory = wordTypeDict.get(word)
            typeWordDDict[catagory].append(word)
            print('%s not in typeWordDDict, adding with catagory: %s' %(word, catagory))
            changeSinceSave = True

    for catagory in typeWordDDict:
        for word in typeWordDDict[catagory]:
            if word not in list(wordTypeDict.keys()):
                wordTypeDict.update({word: catagory})
                print('%s not in wordTypeDict, adding with catagory: %s' %(word, catagory))
                changeSinceSave = True

    for word in csvWordList:
        if word not in list(wordTypeDict.keys()):
            if word not in list(deletedWords.keys()):
                print('Adding %s from CSV to datasets!' %word)
                wordType = 'uncatagorized'
                typeWordDDict[wordType].append(word)
                wordTypeDict.update({word:wordType})
                changeSinceSave = True
            else:
                print('%s has already been deleted from this dataset, ignoring for now!' %word)


def printHelp():
    print('Commands can be any case:')
    print('\'help\' : Lists all commands and their functions')
    print('\'save\' : Saves all current changes')
    print('\'check\' : Check the status of words')
    print('\'sort\' : Manual sorting of uncatagorized words')
    print('\'online\' : Uses online dictionary to automatically sort uncatagorized words')
    print('\'edit\' : Add, remove or update words')
    #print('\'settings\' : Change settings')
    print('\'exit\' : Exits the program')


def compareDatasets():
    tempCatagories = []
    print('Comparing to check for duplicates...')
    for word in list(wordTypeDict.keys()):
        tempCatagories = []
        for catagory in typeWordDDict:
            if word in typeWordDDict[catagory]:
                tempCatagories.append(catagory)
        if len(tempCatagories) > 1:
            print('%s is in multiple catagories: %s' %(word, str(tempCatagories)))
            while True:
                correct = input('Please enter correct catagory for %s\n' %word)
                if correct in tempCatagories:
                    tempCatagories.remove(correct)
                    for catagory in tempCatagories:
                        typeWordDDict[catagory].remove(word)
                    break
            print('%s only in catagory: %s' %(word, correct))
    print('All words compared!')





def listToCSV(listToConvert: list) -> str:
    csvToReturn = ''
    if type(listToConvert[0]) == 'list':
        for sentence in listToConvert:
            csvToReturn += ','.join(sentence)
            csvToReturn += ','
    else:
        csvToReturn = ','.join(listToConvert)
    return csvToReturn


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


def wordToCatagory(listToConvert: list) -> list:


    return convertedList


def saveFiles():
    global wordTypeDict
    global typeWordDDict
    global changeSinceSave
    global deletedWords

    if len(wordTypeDict) == 0:
        yn = input('wordTypeDict not yet instantiated, saving now will erase saved data for file catagories_words.json, continue? y/n')
        if yn == 'y' or yn == 'Y':
            try:
                with open('catagories_words.json', 'w+') as x:
                    json.dump(dict(typeWordDDict), x)
                    print('Saved: catagories_words.json')
            except:
                print('Error with saving: catagories_words.json! Did not save!')
            try:
                with open('word_catagories.json', 'w+') as x:
                    json.dump(wordTypeDict, x)
                    print('Saved: word_catagories.json')
            except:
                print('Error with saving: word_catagories.json! Did not save!')
            try:
                with open('generatedcsv.txt', 'w+') as x:
                    csvToSave = listToCSV(csvWordList)
                    x.write(csvToSave)
                    print('Saved: generatedcsv.txt')
            except:
                print('Error with saving: generatedcsv.txt! Did not save!')
            try:
                with open('deletedwords.json', 'w+') as x:
                    json.dump(deletedWords, x)
                    print('Saved: deletedwords.json')
            except:
                print('Error with saving: deletedwords.json! Did not save!')
            changeSinceSave = False
        else:
            print('Cancelled saving')
    else:
        try:
            with open('catagories_words.json', 'w+') as x:
                json.dump(dict(typeWordDDict), x)
                print('Saved: catagories_words.json')
        except:
            print('Error with saving: catagories_words.json! Did not save!')
        try:
            with open('word_catagories.json', 'w+') as x:
                json.dump(wordTypeDict, x)
                print('Saved: word_catagories.json')
        except:
            print('Error with saving: word_catagories.json! Did not save!')
        try:
            with open('generatedcsv.txt', 'w+') as x:
                csvToSave = listToCSV(csvWordList)
                x.write(csvToSave)
                print('Saved: generatedcsv.txt')
        except:
            print('Error with saving: generatedcsv.txt! Did not save!')
        try:
            with open('deletedwords.json', 'w+') as x:
                json.dump(deletedWords, x)
                print('Saved: deletedwords.json')
        except:
            print('Error with saving: deletedwords.json! Did not save!')
        changeSinceSave = False


def sortUncatagorized():
    global typeWordDDict
    global wordTypeDict
    global changeSinceSave
    global deletedWords

    wordDone = False
    iCatagorized = 0
    iDeleted = 0
    iNewCatagories = 0
    iSkipped = 0
    listToSort = list(typeWordDDict['uncatagorized'])
    listToSortDisplay = list(typeWordDDict['uncatagorized'])
    toSort = input('Sort uncatagorized? (There are %d word(s) to catagorize) y/n\n' %len(listToSort))
    if toSort.upper() == 'Y':
        changeSinceSave = True
        for word in listToSort:
            wordDone = False
            while wordDone != True:
                wordDone = False
                print('Words left to sort: ' + str(listToSortDisplay))
                catagory = input(word + ': Enter catagory or enter \'delete\' to remove entry from list...\n')
                if catagory.upper() == 'DELETE':
                    listToSortDisplay.remove(word)
                    deletedWords.update({word:wordTypeDict.get(word)})
                    typeWordDDict['uncatagorized'].remove(word)
                    wordTypeDict.pop(word)
                    print(word + ' removed!')
                    iDeleted += 1
                    wordDone = True
                elif catagory.upper() == 'SKIP':
                    listToSortDisplay.remove(word)
                    print('Skipping current word: %s' %word)
                    iSkipped += 1
                    wordDone = True
                elif catagory.lower() in list(typeWordDDict.keys()):
                    wordTypeDict.pop(word)
                    wordTypeDict.update({word:catagory})
                    typeWordDDict['uncatagorized'].remove(word)
                    typeWordDDict[catagory].append(word)
                    print(word + ' added to catagory, ' + catagory)
                    iCatagorized += 1
                    wordDone = True
                else:
                    while True:
                        newCatagory = input(catagory + ' is not a current catagory, add %s to new catagory? y/n\n' %word)
                        if newCatagory.upper() == 'Y':
                            wordTypeDict.pop(word)
                            wordTypeDict.update({word:catagory})
                            typeWordDDict['uncatagorized'].remove(word)
                            typeWordDDict[catagory].append(word)
                            print(word + ' added to catagory, ' + catagory)
                            iNewCatagories += 1
                            wordDone = True
                        elif newCatagory.upper() == 'N':
                            print('Returning to initial state... ')
                            break
                        else:
                            print('Invalid input... ')

    elif toSort.upper() == 'N':
        pass
    else:
        sortUncatagorized()
    print('Words catagorized: ' + str(iCatagorized) +', Words deleted: ' + str(iDeleted) + ', New catagories created: ' + str(iNewCatagories) + ', Words skipped: ' + str(iSkipped))
    if len(typeWordDDict['uncatagorized']) > 0:
        repeatInput = input('There are still some uncatagorized words, repeat process? y/n')
        if repeatInput.upper() == 'Y':
            sortUncatagorized()
        else:
            pass
    if iDeleted > 0 or iCatagorized > 0 or iNewCatagories > 0:
        toSave = input('Changes have been made, would you like to save? y/n')
        if toSave.upper() == 'Y':
            saveFiles()


def checkWordsOnline():
    global wordTypeDict_prev_keys
    global typeWordDDict
    global wordTypeDict
    global wordTypeDict_prev
    global changeSinceSave

    changeSinceSave = True
    for word in list(wordTypeDict.keys()):
        if wordTypeDict_prev_keys.count(word) == 0 or wordTypeDict_prev.get(word) == 'uncatagorized':
            timeDelay = random.randint(25, 60)/10
            print(timeDelay)
            time.sleep(timeDelay)
            print('looking for ' + word)
            urlLink = urlBase + word
            r = requests.get(urlLink, headers = requestHeaders)
            pageContent = r.content
            soup = bs4.BeautifulSoup(pageContent, 'html.parser')
            try:
                wordType = soup.find('span', class_= 'pos').get_text()
                typeWordDDict[wordType].append(word)
                wordTypeDict.update({word:wordType})
                if word in typeWordDDict['uncatagorized']:
                    typeWordDDict['uncatagorized'].remove(word)
                print('%s found, catagory: %s' %(word,wordType))
            except:
                if word not in typeWordDDict['uncatagorized'] and word not in list(wordTypeDict.keys()):
                    typeWordDDict['uncatagorized'].append(word)
                    wordTypeDict.update({word:'uncatagorized'})
                    print(word + ' not found')
                elif word in typeWordDDict['uncatagorized'] and wordTypeDict[word] == 'uncatagorized':
                    print('%s not found, already uncatagorized' %word)
                else:
                    print('ISSUE %s NOT UNIFORM' %word)


        else:
            wordType = wordTypeDict_prev.get(word)
            print(word + ' already catagorized: ' + wordType)


def editWords():
    global wordTypeDict
    global typeWordDDict
    global deletedWords

    while True:
        arue = input('Type \'a\' to add a new word, \'r\' to remove a word, \'u\' to update a word or \'e\' to exit editing\n')
        if arue.upper() == 'A':
            while True:
                wordToAdd = input('What word to add: ')
                if wordToAdd in list(wordTypeDict.keys()):
                    print('%s already exists in catagory: %s, returning to editing...' %(wordToAdd, wordTypeDict.get(wordToAdd)))
                    break
                checkOnline = input('Check word type online? y/n')
                if checkOnline.upper() == 'Y':
                    urlLink = urlBase + wordToAdd
                    r = requests.get(urlLink, headers = requestHeaders)
                    pageContent = r.content
                    soup = bs4.BeautifulSoup(pageContent, 'html.parser')
                    try:
                        wordType = soup.find('span', class_= 'pos').get_text()
                        typeWordDDict[wordType].append(wordToAdd)
                        wordTypeDict.update({wordToAdd:wordType})
                        print('%s found with catagory: %s' %(wordToAdd, wordType))
                        break
                    except:
                        print('Current word catagories are: %s' %list(typeWordDDict.keys()))
                        currentInput = input('%s not found online, please enter word catagory, or enter \'skip\' to exit process: ')
                        if currentInput.upper() == 'SKIP':
                            print('Skipping process for word %s' %wordToAdd)
                            break
                        elif currentInput in list(typeWordDDict.keys()):
                            typeWordDDict[currentInput].append(wordToAdd)
                            wordTypeDict.update({wordToAdd:currentInput})
                            print('%s added to catagory: %s' %(wordToAdd, currentInput))
                            break
                        else:
                            yn = input('Catagory: %s doesn\'t exist yet, create it? y/n' %currentInput)
                            if yn.upper() == 'Y':
                                typeWordDDict[currentInput].append(wordToAdd)
                                wordTypeDict.update({wordToAdd:currentInput})
                                print('%s added to catagory: %s' %(wordToAdd, currentInput))
                                break
                            else:
                                print('Skipping process for word %s' %wordToAdd)
                                break
                elif checkOnline.upper() == 'N':
                    print('Current word catagories are: %s' %list(typeWordDDict.keys()))
                    wordType = input('Enter the catagory for %s, ' %wordToAdd)
                    if wordType in list(typeWordDDict.keys()):
                        typeWordDDict[wordType].append(wordToAdd)
                        wordTypeDict.update({wordToAdd:wordType})
                        print('%s added to catagory %s' %(wordToAdd, wordType))
                        break
                    else:
                        currentInput = input('Catagory: %s doesn\'t exist yet, create it? y/n' %wordType)
                        if currentInput.upper() == 'Y':
                            typeWordDDict[wordType].append(wordToAdd)
                            wordTypeDict.update({wordToAdd:wordType})
                            print('%s added to catagory %s' %(wordToAdd, wordType))
                        else:
                            print('Skipping process for word %s' %wordToAdd)
                            break
                else:
                    print('Incorrect input...')

        elif arue.upper() == 'R':
            wordToRemove = input('Enter the word to remove: ')
            if wordToRemove in list(wordTypeDict.keys()):
                deletedWords.update({word:wordTypeDict.get(word)})
                wordType = wordTypeDict.get(wordToRemove)
                typeWordDDict[wordType].remove(wordToRemove)
                wordTypeDict.pop(wordToRemove)
                print('%s removed from catagory: %s' %(wordToRemove, wordType))
            else:
                print('%s does not currently exist in the data, returning to editing...' %wordToRemove)

        elif arue.upper() == 'U':
            wordToUpdate = input('Enter the word to update: ')
            if wordToUpdate in list(wordTypeDict.keys()):
                newCatagory = input('%s is currently in catagory: %s, enter a new catagory for word %s: ' %(wordToUpdate, wordTypeDict.get(wordToUpdate), wordToUpdate))
                if newCatagory in list(typeWordDDict.keys()):
                    oldCatagory = wordTypeDict.get(wordToUpdate)
                    wordTypeDict.pop(wordToUpdate)
                    typeWordDDict[oldCatagory].remove(wordToUpdate)
                    wordTypeDict.update({wordToUpdate:newCatagory})
                    typeWordDDict[newCatagory].append(wordToUpdate)
                    print('%s removed from catagory: %s, now added to catagory: %s' %(wordToUpdate, oldCatagory, newCatagory))
                else:
                    yn = input('Catagory: %s doesn\'t exist yet, create it? y/n' %newCatagory)
                    if yn.upper() == 'Y':
                        oldCatagory = wordTypeDict.get(wordToUpdate)
                        wordTypeDict.pop(wordToUpdate)
                        typeWordDDict[oldCatagory].remove(wordToUpdate)
                        wordTypeDict.update({wordToUpdate:newCatagory})
                        typeWordDDict[newCatagory].append(wordToUpdate)
                        print('%s removed from catagory: %s, now added to catagory: %s' %(wordToUpdate, oldCatagory, newCatagory))
                    else:
                        print('Skipping process for word %s' %wordToUpdate)
            else:
                print('%s does not exist in data, returning to editing...' %wordToUpdate)

        elif arue.upper() == 'E':
            print('Exiting editing...')
            break

        else:
            print('Incorrect input...')


def lookupWords():
    while True:
        wordOrCatagory = input('Enter \'w\' to check words, \'c\' to check catagories, \'d\' to see deleted words or \'e\' to exit\n')
        if wordOrCatagory.upper() == 'W':
            wordsToCheck_list = []
            char = 0
            word = ''
            while True:
                wordsToCheck_str = input('Enter a word to check or a sequence of words seperated by commans (e.g. the,egg,boris,)\n')
                if len(wordsToCheck_str) == 0:
                    pass
                else:
                    while char < len(wordsToCheck_str):
                        if wordsToCheck_str[char] != ',':
                            word += wordsToCheck_str[char]
                        else:
                            print(word)
                            wordsToCheck_list.append(word)
                            word = ''
                        char += 1
                    if len(word) > 0:
                        print('egg')
                        wordsToCheck_list.append(word)
                    for word in wordsToCheck_list:
                        if wordTypeDict.get(word) == None:
                            print('Word: %s is not in the dataset' %(word))
                        else:
                            print('Word: %s   Catagory: %s' %(word, wordTypeDict.get(word)))
                    break
            break
        elif wordOrCatagory.upper() == 'C':
            print('Current catagories are: %s' %typeWordDDict.keys())
            catagoryToCheck = input('Enter catagory to display words of\n')
            if catagoryToCheck.lower() in list(typeWordDDict.keys()):
                print(typeWordDDict[catagoryToCheck])
                break
            else:
                print('%s does not exist as a catagory of word' %catagoryToCheck)
                break
        elif wordOrCatagory.upper() == 'D':
            print('Current deleted words are:')
            print(list(deletedWords.keys()))
        elif wordOrCatagory.upper() == 'E':
            break
        else:
            pass


def exitProgram():
    if changeSinceSave:
        yn = input('The data has not been saved since most recent changes, are you sure you want to exit? y/n')
        if yn == 'y' or yn == 'Y':
            exit()
        else:
            pass
    elif len(typeWordDDict['uncatagorized']) > 0:
        yn = input('There are %d uncatagorized word(s), are you sure you want to exit? y/n' %len(typeWordDDict['uncatagorized']))
        if yn == 'y' or yn == 'Y':
            exit()
        else:
            pass
    else:
        sys.exit()

def incorrectCommand():
    print(command + ' is an invalid command, try typing \'help\' ')

commands = {
'HELP' : printHelp,
'SAVE' : saveFiles,
'CHECK' : lookupWords,
'SORT' : sortUncatagorized,
'ONLINE' : checkWordsOnline,
'EDIT' : editWords,
'EXIT' : exitProgram,
'COMPARE' : compareDatasets
}

initializeMain()

while True:

    command = input('Todo = ')
    try:
        commands[command.upper()]()
    except KeyError:
        print('%s is not a valid command, try \'help\' for a list of commands...' %command)
