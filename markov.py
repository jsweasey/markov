from collections import *
import re as re
import math as math
import random as random
import json as json
import os as os

class model():

    class word():

        def count(start=0):
            index = start
            while True:
                yield index
                index += 1

        def __init__(self, word, category='uncatagorized', counter=0):
            self.index = int
            self.word = word
            self.prev = defaultdict(int)
            self.next = defaultdict(int)
            self.category = category
            self.counter = counter


    def parseSentence(self, sample_text: str, sentence_stopper: str,) -> list:

        char, prev_char, word = ''
        sentence_number = 0
        current_sentence, parsed_sentences = []

        for char in sample_text:
            if char == sentence_stopper and (len(word) > 0 or len(current_sentence[-1:])):
                if len(word) > 0 : current_sentence.append(word.lower())
                parsed_sentences.append(current_sentence)
                current_sentence = []
                sentence_number += 1
                word = ''
            elif re.search(r'\s', char) and not re.search(r'\.|\s', prev_char):
                current_sentence.append(word.lower())
                word = ''
            elif re.search(r'\w', char):
                word += char
            else:
                pass
            prev_char = char

        return parsed_sentences

    def loadSampleText(self, file_location: str,) -> str:

        with open(file_location, 'r+') as file_to_read:
            sample_text = str(file_to_read.read())

        return sample_text

    def createModel(self, parsed_sentences: list,):

        word_counter = 0

        for sentence in parsed_sentences:
            word_counter = 0
            for word in sentence:
                if word in list(self.words_indexed.keys()):
                    if word_counter == 0:
                        self.words_indexed[word].prev['>'] += 1
                        self.words_indexed[word].counter += 1
                        prev_word = word
                        word_counter += 1
                    elif word_counter == len(sentence):
                        self.words_indexed[word].prev[prev_word] += 1
                        self.words_indexed[word].next['<'] += 1
                        self.words_indexed[word].counter += 1
                        word_counter += 1
                    else:
                        self.words_indexed[word].prev[prev_word] += 1
                        self.words_indexed[prev_word].next[word] += 1
                        self.words_indexed[word].counter += 1
                        word_counter += 1
                else:
                    self.words_indexed.update({word:word()})



    def __init__(self, file_location: str, sentence_stopper: str, ):

        self.words_indexed = {}

        if (os.path.exists(file_location)) and (os.path.getsize(file_location) > 0):
            sample_text = self.loadSampleText(file_location)
            sample_text2parsed_sentences = self.parseSentence(sample_text, sentence_stopper)
        elif os.path.exists(file_location) == False:
            print('File %s does not exist!' %file_location)
        elif os.path.getsize(file_location) == 0:
            print('File %s has no content!' %file_location)
