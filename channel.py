from __future__ import division
import ast
from ngram import nGram

class error():   # noisy channel model implementation
    def __init__(self):
        self.ng = nGram(True, True)
        self.corpus_copy = ' '.join(self.ng.words)
        self.corpus = self.corpus_copy.replace('<s>','#')
        self.loadConfusionMatrix()
        self.dict = self.loadDict()
    def loadConfusionMatrix(self):
        f = open('confusion/addconfusion.data', 'r')
        data = f.read()
        f.close
        self.addmatrix = ast.literal_eval(data)
        f = open('confusion/subconfusion.data', 'r')
        data = f.read()
        f.close
        self.submatrix = ast.literal_eval(data)
        f = open('confusion/revconfusion.data', 'r')
        data = f.read()
        f.close
        self.revmatrix = ast.literal_eval(data)
        f = open('confusion/delconfusion.data', 'r')
        data = f.read()
        f.close
        self.delmatrix = ast.literal_eval(data)

    def loadDict(self):
        print("Loading dictionary from data file")
        f = open('vocab.txt', 'r')
        return f.read().split("\n")

    def dlEditDistance(self, str1, str2):
        len_str1 = len(str1) + 1
        len_str2 = len(str2) + 1
        matrix = [0 for n in range(len_str1 * len_str2)]
        # first row
        for i in range(len_str1):
            matrix[i] = i
        # first col
        for j in range(0, len(matrix), len_str1):
            if j % len_str1 == 0:
                matrix[j] = j // len_str1
        # Get the edit distance step by step according to the state transition equation
        for i in range(1, len_str1):
            for j in range(1, len_str2):
                if str1[i - 1] == str2[j - 1]:
                    cost = 0
                else:
                    cost = 1
                matrix[j * len_str1 + i] = min(matrix[(j - 1) * len_str1 + i] + 1,
                                               matrix[j * len_str1 + (i - 1)] + 1,
                                               matrix[(j - 1) * len_str1 + (i - 1)] + cost)

        return matrix[-1]

    def genCandidates(self, word,threshold):
        """Method to generate set of candidates for a given word using Damerau-Levenshtein Edit Distance."""
        candidates = dict()
        for item in self.dict:
            item = item.lower()
            # print item, ", ",
            distance = self.dlEditDistance(word, item)
            if distance <= threshold:
                candidates[item] = distance
            if  ''.join(sorted(item)) == ''.join(sorted(word)) and distance < threshold + 3:   # there --> three
                candidates[item] = distance
        return sorted(candidates, key=candidates.get, reverse=False)

    def editType(self, candidate, word):
        """Method to calculate edit type for single edit errors."""
        edit = [False] * 4
        correct = ""
        error = ""
        x = ''
        w = ''
        for i in range(min([len(word), len(candidate)])-1):
            if candidate[0:i + 1] != word[0:i + 1]:
                if candidate[i:] == word[i - 1:]:
                    edit[1] = True
                    correct = candidate[i - 1]
                    error = ''
                    x = candidate[i - 2]
                    w = candidate[i - 2] + candidate[i - 1]
                    break
                elif candidate[i:] == word[i + 1:]:

                    correct = ''
                    error = word[i]
                    if i == 0:
                        w = '#'
                        x = '#' + error
                    else:
                        w = word[i - 1]
                        x = word[i - 1] + error
                    edit[0] = True
                    break
                if candidate[i + 1:] == word[i + 1:]:
                    edit[2] = True
                    correct = candidate[i]
                    error = word[i]
                    x = error
                    w = correct
                    break
                if candidate[i] == word[i + 1] and candidate[i + 2:] == word[i + 2:]:
                    edit[3] = True
                    correct = candidate[i] + candidate[i + 1]
                    error = word[i] + word[i + 1]
                    x = error
                    w = correct
                    break
        candidate = candidate[::-1]
        word = word[::-1]
        for i in range(min([len(word), len(candidate)])):
            if candidate[0:i + 1] != word[0:i + 1]:
                if candidate[i:] == word[i - 1:]:
                    edit[1] = True
                    correct = candidate[i - 1]
                    error = ''
                    x = candidate[i - 2]
                    w = candidate[i - 2] + candidate[i - 1]
                    break
                elif candidate[i:] == word[i + 1:]:
                    correct = ''
                    error = word[i]
                    if i == 0:
                        w = '#'
                        x = '#' + error
                    else:
                        w = word[i - 1]
                        x = word[i - 1] + error
                    edit[0] = True
                    break
                if candidate[i + 1:] == word[i + 1:]:
                    edit[2] = True
                    correct = candidate[i]
                    error = word[i]
                    x = error
                    w = correct
                    break
            try:
                if candidate[i] == word[i + 1] and candidate[i + 2:] == word[i + 2:]:
                    edit[3] = True
                    correct = candidate[i] + candidate[i + 1]
                    error = word[i] + word[i + 1]
                    x = error
                    w = correct
                    break
            except IndexError:
                    pass
        if word == candidate:
            return "None", '', '', '', ''
        if edit[1]:
            return "Deletion", correct, error, x, w
        elif edit[0]:
            return "Insertion", correct, error, x, w
        elif edit[2]:
            return "Substitution", correct, error, x, w
        elif edit[3]:
            return "Reversal", correct, error, x, w

    def channelModel(self, x, y, edit):
        """Method to calculate channel model probability for errors."""
        if edit == 'add':
            if x == '#':
                if x + y in self.addmatrix.keys():
                    return (self.addmatrix[x + y]+1) / self.corpus.count(' ' + y)
                else:
                    return 0.0
            else:
                 if x + y in self.addmatrix.keys():
                      return (self.addmatrix[x + y]+1) / self.corpus.count(x)
                 else:
                     return 0.0
        if edit == 'sub':
            if x + y in self.submatrix.keys():
                return (self.submatrix[(x + y)[0:2]]+1) / self.corpus.count(y)
            else:
                return 0.0
        if edit == 'rev':
            if x + y in self.revmatrix.keys():
                return (self.revmatrix[x + y]+1) / self.corpus.count(x + y)
            else:
                return 0.0
        if edit == 'del':
            if x + y in self.delmatrix.keys():
                return (self.delmatrix[x + y] + 1) / self.corpus.count(x + y)
            else:
                return 0.0