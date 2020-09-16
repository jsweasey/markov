from collections import *
import re as re
import math as math
import random as random
import json as json
import os as os
from itertools import count

class model():

    class word():

        _id = count(0)

        def __init__(self, word:str, category='uncatagorized', counter=0):
            self.id = next(self._id)
            self.word = word
            self.prev = defaultdict(int)
            self.next = defaultdict(int)
            self.category = category
            self.counter = counter


    def parseSentence(self, sample_text: str, sentence_stopper: str,) -> list:

        char, prev_char, word = '','',''
        sentence_number = 0
        current_sentence, parsed_sentences = [],[]

        add_extra = False #VAR TO ALLOW FOR WORDS AFTER LAST SENTENCE STOPPER TO BE ADDED TO parsed_sentences

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
        if add_extra:
            if len(current_sentence) > 0:
                parsed_sentences.append(current_sentence)
        print(parsed_sentences)
        return parsed_sentences

    def loadSampleText(self, file_location: str,) -> str:

        with open(file_location, 'r+') as file_to_read:
            sample_text = str(file_to_read.read())

        return sample_text

    def createModel(self, parsed_sentences: list,):

        word_counter = 0

        for sentence in parsed_sentences:
            word_counter = 0
            prev_word = ''
            for word in sentence:
                if word in list(self.words_indexed.keys()):
                    if word_counter == 0:
                        self.words_indexed[word].prev['>'] += 1
                        self.words_indexed['>'].next[word] += 1
                        self.words_indexed[word].counter += 1
                        prev_word = word
                        word_counter += 1
                    elif word_counter == (len(sentence)-1):
                        self.words_indexed[word].prev[prev_word] += 1
                        self.words_indexed[word].next['<'] += 1
                        self.words_indexed[prev_word].next[word] += 1
                        self.words_indexed[word].counter += 1
                        word_counter += 1
                    else:
                        self.words_indexed[word].prev[prev_word] += 1
                        self.words_indexed[prev_word].next[word] += 1
                        self.words_indexed[word].counter += 1
                        prev_word = word
                        word_counter += 1
                else:
                    if word_counter == 0:
                        self.words_indexed.update({word:self.word(word)})
                        self.words_indexed[word].prev['>'] += 1
                        self.words_indexed['>'].next[word] += 1
                        self.words_indexed[word].counter += 1
                        prev_word = word
                        word_counter += 1
                    elif word_counter == (len(sentence)-1):
                        self.words_indexed.update({word:self.word(word)})
                        self.words_indexed[word].prev[prev_word] += 1
                        self.words_indexed[word].next['<'] += 1
                        self.words_indexed[prev_word].next[word] += 1
                        self.words_indexed[word].counter += 1
                        word_counter += 1
                    else:
                        self.words_indexed.update({word:self.word(word)})
                        self.words_indexed[word].prev[prev_word] += 1
                        self.words_indexed[prev_word].next[word] += 1
                        self.words_indexed[word].counter += 1
                        prev_word = word
                        word_counter += 1

    def initializeModel(self):
        file_location = self.file_location
        self.words_indexed.update({'>':self.word('>')}) #MAYBE THINK ABOUT MOVING THIS INITIALIZATION
        if self.file_good:
            sample_text = self.loadSampleText(file_location)
            sample_text2parsed_sentences = self.parseSentence(sample_text, self.sentence_stopper)
            self.createModel(sample_text2parsed_sentences)
            print('Initialized model succesfully')
        else:
            print('Issue with %s, please re initialize' %file_location)

    def checkFile(self, file_location : str) -> bool:

        if (os.path.exists(file_location)) and (os.path.getsize(file_location) > 0):
            return_bool = True
        elif os.path.exists(file_location) == False:
            return_bool = False
        elif os.path.getsize(file_location) == 0:
            return_bool = False

        return return_bool

    def __init__(self, file_location: str, sentence_stopper: str, **keyword_args):
        self.words_indexed = {}
        self.file_good = False
        self.file_location = file_location
        self.sentence_stopper = sentence_stopper
        self.file_good = self.checkFile(self.file_location)

        if self.file_good == False:
            print('File %s is not good, please check' %self.file_location)
        else:
            if ('auto_init' in keyword_args) and (keyword_args['auto_init'] == True):
                self.initializeModel()

    def wordCanBeSeed(self, word2check:str) -> bool:
        return_bool = False
        seed_words = list(self.words_indexed['>'].next.keys())
        if (word2check in seed_words):
            return_bool = True

        return return_bool

    def nextGenWord(self, word2check:str) -> str:
        prob_list = []
        next_list = list(self.words_indexed[word2check].next.keys())
        for word in next_list:
            for i in range(self.words_indexed[word2check].next.get(word)):
                prob_list.append(word)
        word_return = prob_list[random.randint(0, (len(prob_list)-1))]

        return word_return

    def list2str(self, list2convert:list) -> str:
        word_return = ''
        for word in list2convert:
            word_return += ('%s ' %word)

        return word_return


    def generate(self, **keyword_args): #args = seed_word, min_length, sentence_num,

        seed = ''
        m_len = 0
        no_min = False
        past_min = False
        s_num = 10
        w_num = 0
        g_sentence = []
        g_sentences = []

        #checking kwargs
        if ('seed_word' in keyword_args and self.wordCanBeSeed(keyword_args['seed_word'])):
            seed = keyword_args['seed_word']
        else:
            rand_int = random.randint(0, len(self.words_indexed['>'].next))
            seed = list(self.words_indexed['>'].next.keys())[rand_int]
        if ('min_length' in keyword_args and isinstance(keyword_args['min_length'], int)):
            m_len = keyword_args['min_length']
        else:
            no_min = True
        if ('sentence_num' in keyword_args and isinstance(keyword_args['sentence_num'], int)):
            s_num = keyword_args['sentence_num']
        print('seed: %s, m_len: %s, s_num: %s' %(seed, m_len, s_num))

        for x in range(s_num):
            w_num = 0
            n_word = ''
            g_sentence = []
            if no_min:
                past_min = True
            else:
                past_min = False
            while True:
                if (w_num > m_len) and (past_min == False):
                    past_min = True
                if n_word == '<':
                    if (w_num > m_len) or (past_min):
                        g_sentences.append(self.list2str(g_sentence))
                        break
                    else:
                        g_sentence = []
                        n_word = seed
                if w_num == 0:
                    g_sentence.append(seed)
                    n_word = self.nextGenWord(seed)
                else:
                    g_sentence.append(n_word)
                    if n_word != '<':
                        n_word = self.nextGenWord(n_word)
                w_num = len(g_sentence)

        print(g_sentences)


m = model('sampletext.txt','.',auto_init=True)
#m.initializeModel()
m.generate(min_length=50)
