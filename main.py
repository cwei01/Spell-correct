# -*- coding = utf-8 -*-
# Copyright (C) The Chongqing University MLG Lab Authors. team - All Rights Reserved
# @IDE: PyCharm
# Written by Wei Chen <mlg_cwei@cqu.edu.cn>, Aug 19-th, 2021
try:
    import xml.etree.ElementTree as ET, getopt, logging, sys, random, re, copy
    from xml.sax.saxutils import escape
except:
    sys.exit('Some package is missing... Perhaps <re>?')
from channel import error
import math
import os
from multiprocessing import  Process
import warnings
import logging
warnings.filterwarnings("ignore")
logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)
sc = error()
def mergeText(filepath,outfilepath):
    filedir = os.getcwd() + filepath
    filenames = os.listdir(filedir)
    filenames.sort(key=lambda x: int(x.split('.')[0]))
    f = open(outfilepath, 'w')
    for filename in filenames:
        filepaths = filedir + '/' + filename
        f.writelines(open(filepaths))
    f.close()
    return
def load_testfile():
    path = 'testdata.txt'
    test_file = open(path,'r',encoding='utf-8')
    test_line = test_file.readlines()
    sentence_list = []
    for i in range(len(test_line)):
        _,  _, sentence = test_line[i].strip('\n').split('\t')
        sentence_list.append(sentence)
    return sentence_list
def del_file(path):
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            del_file(path_file)
def is_number(s):
    try:
        if len(s) > 4 and s[-4] == ',':
            s = s[:-4] + s[-3:]
        float(s)
        return True
    except ValueError:
        pass
    return False
def  count_zero(s):
    k = 0
    if s[2]=='0' :
        for i in range(3,len(s)):
            if s[i]  != '0':
                k = i
                break
    return  k-2
def  correct(input_sen):   #  main  program entry
    if  input_sen[-1] == '.':
        input_s = input_sen[:-1]
    elif input_sen[-3] == '.':
        input_s = input_sen[:-3]
    else:
        input_s = input_sen
    sentence = str(input_s.lower()).split()
    sentence.insert(0,'#')
    sentence.append('#')
    special_list = ['u.s.']
    correct_sen = ""
    for index, word in enumerate(sentence):
        if  word[-2:] == "'s":  ## start to change the reading format
            word = word[:-2]
        if word[-1] == "," or word[-1] == "'":
            word = word[:-1]
        if len(word) < 4 or word in special_list or  is_number(word) or '/' in word or '-' in word:
             candidates  = [word]
        else:
             candidates = sc.genCandidates(word, 1)
        if word in candidates:  # real-word spell correction
            NP = dict()
            P = dict()
            for item in candidates:
                if  item == word:
                    current_word,words_number = sc.ng.count_word(word,'bi')
                    if   current_word > 2:
                          NP[item] = 0.95
                    else:
                          NP[item] = 1/words_number
                edit = sc.editType(item, word)
                # print(edit)
                if edit == None:
                    continue
                if edit[0] == "Insertion":
                    NP[item] = sc.channelModel(edit[3][0], edit[3][1], 'add')
                if edit[0] == 'Deletion':
                    NP[item] = sc.channelModel(edit[4][0], edit[4][1], 'del')
                if edit[0] == 'Reversal':
                    NP[item] = sc.channelModel(edit[4][0], edit[4][1], 'rev')
                if edit[0] == 'Substitution':
                    NP[item] = sc.channelModel(edit[3], edit[4], 'sub')
            for item in NP:
                channel = NP[item]
                if len(sentence) - 1 != index:
                    bigram = math.pow(math.e, sc.ng.sentenceprobability(
                        sentence[index - 1] + ' ' + item + ' ' + sentence[index + 1], 'bi', 'antilog'))
                else:
                    bigram = math.pow(math.e, sc.ng.sentenceprobability(sentence[index - 1] + ' ' + item, 'bi', 'antilog'))
                weight = 1 / math.pow(count_zero(str(bigram)),18)
                P[item] = weight* channel * bigram * math.pow(10, 9)
            P = sorted(P, key=P.get, reverse=True)
            if P == []:
                P.append(word)
            correct_sen = correct_sen + P[0] + ' '
        else:  # no-word spell correction
            NP = dict()
            P = dict()
            for item in candidates:
                edit = sc.editType(item, word)
                if edit == None:
                    continue
                if edit[0] == "Insertion":
                    NP[item] = sc.channelModel(edit[3][0], edit[3][1], 'add')
                if edit[0] == 'Deletion':
                    NP[item] = sc.channelModel(edit[4][0], edit[4][1], 'del')
                if edit[0] == 'Reversal':
                    NP[item] = sc.channelModel(edit[4][0], edit[4][1], 'rev')
                if edit[0] == 'Substitution':
                    NP[item] = sc.channelModel(edit[3], edit[4], 'sub')
            for item in NP:
                channel = NP[item]
                if len(sentence) - 1 != index:
                    bigram = math.pow(math.e, sc.ng.sentenceprobability(
                        sentence[index - 1] + ' ' + item + ' ' + sentence[index + 1], 'bi', 'antilog'))
                else:
                    bigram = math.pow(math.e, sc.ng.sentenceprobability(sentence[index - 1] + ' ' + item, 'bi', 'antilog'))
                weight = 1 / math.pow(count_zero(str(bigram)),18)   #18 is designed for balancing the two terms(i.e., channel model  and language model)
                P[item] = weight * channel * bigram * math.pow(10, 9)
            P = sorted(P, key=P.get, reverse=True)
            if P == []:
                P.append(word)
            correct_sen = correct_sen + P[0] + ' '
    correct_sen = correct_sen.split()      ### complete printing, start to change the writing format....
    del(correct_sen[-1])
    del(correct_sen[0])
    output_sen = []
    nation_list = ['canada','brazil','america','board']
    for i in range(len(correct_sen)):
        if input_s.split()[i][-1] == ",":
            correct_sen[i] = correct_sen[i] +","
        if input_s.split()[i][-1] == "'":
            correct_sen[i] = correct_sen[i] +"'"
        if input_s.split()[i][-2:] == "'s":
            correct_sen[i] = correct_sen[i] +"'s"
        if correct_sen[i] == input_s.lower().split()[i]:
            output_sen.append(input_s.split()[i])
        else:
            if  input_s.split()[i][0].isupper():
                if  input_s.split()[i][-1].isupper():
                    output_sen.append(correct_sen[i].upper())
                elif  input_s.split()[i][1].isupper():
                    output_sen.append(correct_sen[i][:2].upper() + correct_sen[i][2:])
                else:
                   output_sen.append(correct_sen[i][0].upper() + correct_sen[i][1:])
            elif  input_s.split()[i][0].islower() and input_s.split()[i][-3].isupper():
                output_sen.append(correct_sen[i][0].upper() + correct_sen[i][1:])
            elif  input_s.split()[i][0].islower() and input_s.split()[i] in nation_list:
                output_sen.append(correct_sen[i][0].upper() + correct_sen[i][1:])
            else:
                output_sen.append(correct_sen[i])
    if input_sen[-1] =='.' or input_sen[-3] == '.' :
           output_sen = " ".join(output_sen)+'.'
    else:
           output_sen = " ".join(output_sen)
    return output_sen


#---------------------------------------------------------------------------------------------#
"""
in this part, we  we process the 1000 sentences in a parallel way, 
 thus we can increase the speed of operation.
"""
def  span_processing(start,end):
    sentence_list = load_testfile()
    for i in range(start,end):
        write_path = os.path.join('output/','%s.txt' %(i+1))
        write_file = open(write_path,'w')
        output_sen = correct(sentence_list[i])
        write_file.write(str(i+1)+'\t'+output_sen+'\n')
        write_file.close()
    return
dis = 500
def  per_task1():
    span_processing(0,dis)
def  per_task2():
    span_processing(dis,2*dis)
def multi_work(func_list):
    proc_record = []
    for i in range(len(func_list)):
        print("process:", i)
        p = Process(target=func_list[i], args=())
        p.start()
        proc_record.append(p)
    for p in proc_record:
          p.join()
    print("end processing....")
    mergeText('/output','result.txt')
    print("start deleting output file....")
    if os.path.exists('output'):
        del_file('output')
    logger.info("end deleting output file....")
#--------------------------------------------------------------------------------------------#
if __name__ == '__main__':
    work_list = [per_task1,per_task2]
    multi_work(work_list)








