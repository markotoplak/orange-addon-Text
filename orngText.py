"""
This module is used for text mining in Orange.

The following languages are supported:
bg - Bulgarian
cs - Czech
en - English
es - Spanish
et - Estonian
fr - French
ge - German
hr - Croatian
hu - Hungarian
it - Italian
ro - Romanian
sl - Slovenian
sr - Serbian
"""

"""
list(string) = tokenize(string)

>>> tokenize("Mico Mrkaic je isao po dlekom putu.")
["Mico", " ", "Mrkaic", " ", "je", " ", "isao" ," ", "po",  " ", "dlekom", " ", "putu", "."]

token = lemmatize(token)
text = lemmatize(text, lemmatizer=None)
list(token) = lemmatize(list(token), lemmatizer=None)

p = preprocess() # default english
p = preprocess(language="hrvatski")
print p.stopwords
p.stopwords = ['a', 'the']

p.lemmatize('idemo')
ici

p.lemmatize('idemo kuci')
'ici kuca'

p.lemmatize(['idemo','kuci'])
['ici','kuca']

p.removeStopwords(text)
p.removeStopwords(list(token))
p.removeStopwords(token) # returns token or None

print p.tokenize('I am the best.')
I am best.

table[0]['rijeci7']

encoding - tmt uvijek prima i vraca UTF8 string
da li je string ili lista je sugavo napravljeno
dokumentacija
dodati nove jezike
text je zadnji string atribut
from orngText import orngText - jel moze to bolje (proucit python pakete)

##supportedLangs = [('bg', 'Bulgarian'), ('cs', 'Czech'), ('en', 'English'), ('es', 'Spanish')\
##('et', 'Estonian'), ('fr', 'French'), ('ge', 'German'), ('hr', 'Croatian'),\
##('hu', 'Hungarian'), ('it', 'Italian'), ('ro', 'Romanian'), ('sl', 'Slovenian'),\
##('sr', 'Serbian')]

"""



import sys
if sys.version < "2.4":
   from sets import Set
   set = Set
from xml.sax import handler, make_parser
import os.path
import re
import orange
import orngTextWrapper
import types

def loadWordSet(f):
    try:
       f = open(f, 'r')
    except:
       return set([])
    setW = set([])
    lines = f.readlines()
    f.close()
    for line in lines:
        line = line.lower()
        if line.find(';') != -1:
            line = line[:line.find(';')]
        line = line.strip(' \t\r\n')
        if len(line):
            setW.add(line)
    return setW


def boundary_split(s, removePunctuation = True):
    if removePunctuation:
        p = re.compile('[\.,!?()\[\]{}:;"\'<>/ \n\r\t]')
        return [el for el in p.split(s) if el]
    else:
        t = []
        s = re.split('\s', s)
        p = re.compile('(\W)')
        for phrase in s:
            words = p.split(phrase)
            for word in words:
                t.append(word)
        return [el for el in t if el]

class Preprocess(object):

    def __init__(self, language=None, inputEncoding='utf-8', outputEncoding='utf-8', normType = 'lemmatize'):
        language = language or 'en'
        self.inputEncoding = inputEncoding
        self.outputEncoding = outputEncoding
        self.tokenize = boundary_split
        if normType == 'stem' and len(self.langData[language]) == 3:
            self.lemmatizer, self.stopwords = (self.langData[language][2], self.langData[language][1])
        else:
            self.lemmatizer, self.stopwords = self.langData[language][:2]

    def _in2utf(self, s):
       return s.decode(self.inputEncoding, 'replace').encode('utf-8', 'ignore')

    def _utf2out(self, s):
       return s.decode('utf-8', 'ignore').encode(self.outputEncoding, 'ignore')
        
    def doOnExampleTable(self, data, textAttributePos, meth, callback = None):
        newData = orange.ExampleTable(data)
        for ex in newData:
            ex[textAttributePos] = meth(ex[textAttributePos].value)
            if callback:
                callback()
        return newData
        
    def lemmatizeExampleTable(self, data, textAttributePos, callback = None):
        return self.doOnExampleTable(data, textAttributePos, self.lemmatize, callback)
        
    def lemmatize(self, token):
        if isinstance(token, types.StringTypes):
            return self._utf2out(self.lemmatizer(self._in2utf(token)))
        elif isinstance(token, types.ListType):
            return [self._utf2out(self.lemmatizer(self._in2utf(t))) for t in token]
        else:
            raise TypeError

    def lowercase(self, text):
        """Converts the word to lowercase."""

#        import string
#        return string.lower(text)
        text = text.decode(self.inputEncoding, "ignore")
        return text.lower().encode(self.inputEncoding)
    
##        try:
##            # token or text
##            token + ""
##            return self._utf2out(self.lemmatizer(token))
##        except TypeError:
##            # list
##            return [self._utf2out(self.lemmatizer(t)) for t in token]

    def removeStopwordsFromExampleTable(self, data, textAttributePos, callback = None):
        return self.doOnExampleTable(data, textAttributePos, self.removeStopwords, callback)
    
    def removeStopwords(self, text):
        if isinstance(text, types.StringTypes):
            tokens = self.tokenize(text)
            tokens = [token for token in tokens if self.lowercase(token) not in self.stopwords]
            text = ' '.join(tokens)
            return text
            #return self._utf2out(tmt.removeWords(self._in2utf(text), list(self.stopwords)))
        elif isinstance(text, types.ListType):
            return [t for t in text if self.lowercase(t) not in self.stopwords] or None
            #return [self._utf2out(t) for t in text if t not in self.stopwords] or None
        else:
            raise TypeError

##        try:
##            # token or text
##            token + ""
##            #return " ".join([t for t in self.tokenize(token) if t not in self.stopwords]) or None #TODO: tmt.removeStopwordstext
##            return self._utf2out(tmt.removeWords(token, list(self.stopwords)))
##        except TypeError:
##            # list
##            return [self._utf2out(t) for t in token if t not in self.stopwords] or None
            

    __languageDataPath = os.path.join(os.path.dirname(__file__), 'language_data')
    langData = {
#            'en' : (lambda x: x, [], lambda x: re.split(r'\b', x, re.DOTALL)),
            'en' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-en.bin')).lemmatizeText,
                    loadWordSet(os.path.join(__languageDataPath,'stopwords_en.txt')),
                    orngTextWrapper.porter().lemmatizeText),
            'hr' : (orngTextWrapper.lemmatizer(os.path.join(__languageDataPath,'lem-hr.fsa')).lemmatizeText,
                    loadWordSet(os.path.join(__languageDataPath,'stopwords_hr.txt'))),
            'fr' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-fr.bin')).lemmatizeText,
                    loadWordSet(os.path.join(__languageDataPath,'stopwords_fr.txt'))),
            'bg' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-bg.bin')).lemmatizeText, set()),
            'cs' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-cs.bin')).lemmatizeText, set()),
            'et' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-et.bin')).lemmatizeText, set()),
            'ge' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-ge.bin')).lemmatizeText, set()),
            'hu' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-hu.bin')).lemmatizeText, set()),
            'it' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-it.bin')).lemmatizeText, set()),
            'ro' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-ro.bin')).lemmatizeText, set()),
            'sl' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-sl.bin')).lemmatizeText, set()),
            'es' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-es.bin')).lemmatizeText, set()),
            'sr' : (orngTextWrapper.lemmagen(os.path.join(__languageDataPath,'lem-sr.bin')).lemmatizeText, set()),
            }

def loadReuters(dirName):
    """Load all .sgm files from the directory dirName."""
    from xml.sax import make_parser, handler   
    import os, copy 

    cat = orange.StringVariable("category")
    name = orange.StringVariable("name")
    meta = orange.StringVariable("text")
    lewis = orange.StringVariable("lewissplit")
    date = orange.StringVariable("date")
    topics = orange.StringVariable("topics")
    addCat = [cat, name, meta, lewis, date, topics]
    dom = orange.Domain(addCat, 0)

    data = orange.ExampleTable(dom)
    cat = orange.StringVariable("category")
    name = orange.StringVariable("name")
    meta = orange.StringVariable("text")
    lewis = orange.StringVariable("lewissplit")
    date = orange.StringVariable("date")
    topics = orange.StringVariable("topics")
    addCat = [cat, name, meta, lewis, date, topics]
    dom = orange.Domain(addCat, 0)

    data = orange.ExampleTable(dom)


    class ReutersHandler(handler.ContentHandler):
        def __init__(self):
            self.chars = []
            self.parse = True                        
            self.ignoreTags = set(['places','people','orgs','exchanges','companies','unknown'])
            self.normalTags = set(['date','topics','title','dateline','body','text'])
            self.document = {'dateline':'','title':'','body':''}
            self.f = None
            self.ex = orange.Example(dom)
                        
        def startElement(self, name, attrs):
            if name.lower() == 'reuters':
                for attName in attrs.keys():
                    if attName.lower() == 'newid':
                        self.ex['name'] = attrs.getValue(attName).encode('utf8','ignore')
                    elif attName.lower() == 'topics':
                       self.ex['topics'] = attrs[attName].encode('utf8','ignore')
                    elif attName.lower() == 'lewissplit':
                       self.ex['lewissplit'] = attrs.getValue(attName).encode('utf8','ignore')
            elif name.lower() in self.ignoreTags:
                self.parse = False
            elif name.lower() in self.normalTags:
                self.parse = True
            else:
                pass

        def endElement(self, name):
            if name.lower() in self.ignoreTags:
                self.parse = True
            elif name.lower() in self.normalTags:
                if name.lower() == 'date':
                   self.ex['date'] = ' '.join(self.chars).encode('utf8','ignore')
                elif name.lower() == 'topics':
                   for i in self.chars:
                      if i in set(['',' ','\n','\r','\t']):
                         self.chars.remove(i)
                   self.ex['category']= '+'.join(self.chars).encode('utf8','ignore')
                self.document[name.lower()] = ' '.join(self.chars).encode('utf8','ignore')
                self.chars = []
            elif name.lower() == 'reuters':
                self.ex['text'] = self.document['title'] + '\n' + self.document['dateline'] + '\n' + self.document['body']
                data.append(self.ex)
                self.ex = orange.Example(dom)
                self.chars = []
            else:
                pass


        def characters(self, chrs):
            if self.parse:
                self.chars.append(chrs)

    files = os.listdir(dirName)
    files.sort()
    for fileName in files:
      fileName = os.path.join(dirName, fileName)
      if fileName[-4:] == '.sgm':
          p = make_parser()
          p.setContentHandler(ReutersHandler())
          f = open(fileName)
          forbidden = set(['&#5;','&#22;','&#1;','&#31;','&#2;','&#3;','&#27;[B','&#30;','&#127;','\xFC'])
          tmp = '_tmpsgmFile'
          g = open(tmp, 'w')
          g.write('<?xml version=\"1.0\" ?>\n')
          g.write('<docset>')
          f.readline()
          for line in f:
              for c in forbidden:
                  line = line.replace(c, '')
              g.write(line)
          f.close()
          g.write('</docset>')
          g.close()
          f = open(tmp)
          try:
             p.parse(f)
          except:
             print 'Error loading file %s\n' % fileName
          f.close()
          os.remove(tmp)         

    return data

def loadFromXML(fileName, tags={}, doNotParse=[]):
    """returns ExampleTable, as already implemented by Mladen"""
    cat = orange.StringVariable("category")
    sel = orange.StringVariable("selection")
    name = orange.StringVariable("name")
    meta = orange.StringVariable("text")
    addCat = [cat, sel, name, meta]
    dom = orange.Domain(addCat, 0)    
    data = orange.ExampleTable(dom)
    
    f = open(fileName, "r")
    t = DocumentSetRetriever(f, tags = tags, doNotParse = doNotParse)
    
    while 1:
        # load document
        ex = orange.Example(dom)
        doc = t.getNextDocument()
        
        if not len(doc): break
        ex['category'] = ".".join([d.strip().encode('utf-8','ignore') for d in doc['categories']])
        ex['selection'] = ''
        ex['name'] = " ".join([("%s" % meta[1]).encode('utf-8','ignore') for meta in doc['meta']])
        ex['text'] = doc['content'].strip().encode('utf-8','ignore')
        
        
        data.append(ex)
    return data
        
def loadFromListWithCategories(fileName):
    """
    File has two lines for each document:
       *  first line contains the path to the document
       *  second line contains space separated categories
    
    ExampleTable is returned whose domain contains category, name and text
    """
    cat = orange.StringVariable("category")
    name = orange.StringVariable("name")
    meta = orange.StringVariable("text")
    addCat = [cat, name, meta]
    dom = orange.Domain(addCat, 0)    
    data = orange.ExampleTable(dom)
    
    
    f = open(fileName)
    while 1:
        path = f.readline().strip()
        if not path: break
        categories = f.readline().strip().split(" ")
        
        tmpFile = open(path)
               
        ex = orange.Example(dom)
        ex["name"] = path
        ex["category"] = ".".join(categories)
        ex["text"] = "".join(tmpFile.readlines())
        data.append(ex) 
            
    f.close()
    return data


def bagOfWords(exampleTable, preprocessor=None, textAtribute=None, stopwords = None, callback = None):
    """
        by default, text attribute is the last string attribute in the list of attributes ----> no default, or text default (reason, all attributes are String)
    """
    p = preprocessor #or Preprocess('en')
    #domain = exampleTable.domain

    domaincopy = orange.Domain(exampleTable.domain)
    # create new ExampleTable
    data = orange.ExampleTable(exampleTable)
    #data.domain = orange.Domain(exampleTable.domain)

    # for ex in exampleTable:
    #       kreiraj newEx koji ima attribut category i name
    #       tokeniziraj ex["text"]
    #       svaki token koji nije interpunkcija dodaj u newex kao metaattribut koristeci incFreqWord
    #       dodaj newex u newexampletable

    allWords = {}
    for ex in data:
        if not preprocessor:
           if stopwords:
              tokens = boundary_split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
              tokens = [w for w in tokens if w.lower() not in stopwords]
           else:
              tokens = boundary_split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
        else:
            tokens = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
        wordList = dict.fromkeys(tokens, 0)
        for token in tokens:
            wordList[token] += 1.0

        for k in wordList.keys():
           id = allWords.get(k, 0)
           if not id:
              id = orange.newmetaid()
              allWords[k] = id
           ex[id] = wordList[k]
        if callback:
            callback()

    data.domain.addmetas(dict([(id, orange.FloatVariable(k)) for k, id in allWords.items()]), True)

    #exampleTable.domain = orange.Domain(data.domain.attributes)
    exampleTable.changeDomain(domaincopy)
    # vrati newexampletable
    return data

#selectFeaturesByFrequency(bof, min=1, max=None)
#selectFeaturesByChiSquare(bof, min=4.0)


#########data = loadFromListWithCategories('list.txt')
#p = Preprocess()
################print p.tokenize(data[0]['text'].value)
######################bow = bagOfWords(data)

############################################
##
## Parse document
## It could be better to use exsting lib for parsing XML (Beautiful Soup)

class DocumentSetHandler(handler.ContentHandler):            
    def __init__(self, tags = None, doNotParse = []):
        self.tagsToHandle = ["content", "category", "document", "categories"]
        # set default XML tags
        self.name2tag = {}
        if not tags:
            self.tags = {}
            for tag in self.tagsToHandle:
                self.tags[tag] = tag
                self.name2tag[tag] = tag
        else:
            self.tags = {}
            for tag in self.tagsToHandle:
                if not tags.has_key(tag):
                    self.tags[tag] = tag
                    self.name2tag[tag] = tag
                else:
                    self.tags[tag] = tags[tag]
                    self.name2tag[tags[tag]] = tag
            

                
            
        # for current document being parsed
        self.curDoc = {}
        self.documents = []
        self.level = []
            
        # other settings
        self.doNotParse = doNotParse[:]
        self.doNotParseFlag = 0
    def startElement(self, name, attrs):
        if self.name2tag.has_key(name):
            name = self.name2tag[name]
##        if name == "document": 
##            globals()['countdoc'] =globals()['countdoc'] + 1
        if name in self.doNotParse:
            self.doNotParseFlag += 1
        else:
            try:
                func = getattr(self, 'do' + name.capitalize())
                self.level.append(name)
                func(attrs)
            except:
                if name in self.tags:
                    self.level.append(name)
                    self.curDoc[name] = []
    def endElement(self, name):
        if self.name2tag.has_key(name):
            name = self.name2tag[name]        
        if name in self.tags:
            self.level.pop()
            if name == "document":
                self.curDoc["category"] = []
                self.curDoc["content"] = "".join(self.curDoc["content"])
                self.documents.append(self.curDoc)
                self.curDoc = {}
            elif name == "category":
                self.curDoc["categories"].append("".join(self.curDoc["category"]))
            elif name != "categories":
                self.curDoc[name] = "".join(self.curDoc[name])
        elif name in self.doNotParse:
            self.doNotParseFlag -= 1
    def characters(self, chrs):
        if not self.doNotParseFlag:
            try:
                # check in which tag are the characters
                # only tagsToHandle are parsed, others will raise exception that is ignored
                name = self.level[-1]
                if name not in ["document", "categories"]:
                    self.curDoc[name].append(chrs)
            except:
                pass
    def doDocument(self, attrs):
        self.curDoc["meta"] = attrs.items()[:]
        self.curDoc["content"] = []
        self.curDoc["category"] = []
        self.curDoc["categories"] = [] 
    def doContent(self, attrs):
        self.curDoc["content"] = []
    def doCategory(self, attrs):
        self.curDoc["category"] = []
    def doCategories(self, attrs):
        self.curDoc["categories"] = []

class DocumentSetRetriever:

    def __init__(self, source, tags = None, doNotParse = []):
        self.source = source
        self.handler = DocumentSetHandler(tags, doNotParse)
        self.parser = make_parser()
        self.parser.reset()
        self.parser.setContentHandler(self.handler)

    def getNextDocument(self):
        while 1:
            if len(self.handler.documents):
                curDoc = self.handler.documents.pop(0)
                return curDoc
            if self.source.closed:
                return {}
            chunk = self.source.read(10000)
            if not chunk:
                self.parser.close()
                return {}
            else:
                self.parser.feed(chunk)

def saveExampleTable(table, fileName):
   from pickle import dump

   f = open(fileName, 'w')
   dump(table, f)
   f.close()

def loadExampleTable(fileName):
   from pickle import load

   f = open(fileName)
   table = load(f)
   f.close()
   return table

class Preprocessor_norm:
   def __call__(self, data, LNorm = 2, callback = None):
      """Normalizes the ExampleTable table using the given L-Norm. The default norm is L2."""
      from math import sqrt
      newtable = orange.ExampleTable(data)
      if LNorm == 2:
         for example in newtable:
            sum = 0         
            for v in example.getmetas().values():
               #val = example[word].value
               sum += v*v
            sum = sqrt(sum)
            for word in example.getmetas().keys():
               example[word] = example[word] / sum
            if callback: callback()
         return newtable
      elif LNorm == 1:
         for example in newtable:
            sum = 0         
            for v in example.getmetas().values():
               #val = example[word].value
               sum += v
            for word in example.getmetas().keys():
               example[word] = example[word] / sum
            if callback: callback()
         return newtable      
      elif LNorm > 2:
         from math import pow
         for example in newtable:
            sum = 0         
            for v in example.getmetas().values():
               #val = example[word].value
               sum += pow(v, LNorm)
            sum = pow(sum, 1 / LNorm)
            for word in example.getmetas().keys():
               example[word] = example[word] / sum
            if callback: callback()
         return newtable
      elif LNorm == 0:
         for example in newtable:
            sum = 0         
            for v in example.getmetas().values():
                  #val = example[word].value
                  if v > sum:
                     sum = v
            for word in example.getmetas().keys():
               example[word] = example[word] / sum
            if callback: callback()
         return newtable
      #return data
      
import math

class Preprocessor_tfidf:
    def __init__(self, termNormalizers):
        self.termNormalizers = termNormalizers

    def __call__(self, data, callback = None):
        if type(data) == orange.ExampleTable:
            newData = orange.ExampleTable(data)
            for ex in newData:
                for id, val in ex.getmetas().items():
                    ex[id] *= self.termNormalizers.get(id, 0)
                if callback: callback()
            return newData
        else:
            ex = orange.Example(data)
            for id, val in ex.getmetas().items():
                ex[id] *= self.termNormalizers.get(id, 0)
            return ex


class PreprocessorConstructor_tfidf:
    def __call__(self, data):
        frequencies = {}
        for ex in data:
            for id in ex.getmetas():
                frequencies[id] = frequencies.get(id, 0) + 1

        N = float(len(data))
        normalizers = dict([(id, math.log(N/f)) for id, f in frequencies.items()])
        return Preprocessor_tfidf(normalizers)



def cos(data, normalize = False, distance = 0, callback = None):
    import numpy
    from math import sqrt
    from time import time
    time1 = time()
    c = orange.SymMatrix(len(data))
##    for i, ex1 in enumerate(data):
##        for j in range(i):
##            ex1metas = ex1.getmetas()
##            ex2metas = data[j].getmetas()
##            c[i, j] = sum([v1 * ex2metas.get(id, 0) for id, v1 in ex1metas.items()])
##            if normalize and c[i, j]:
##                c[i, j] /= sqrt(sum([i**2 for i in ex2metas.values()]) * sum([i**2 for i in ex1metas.values()]))

    metas = {}
    for i, ex in enumerate(data):
        metas[i] = ex.getmetas()
    for i, ex1 in enumerate(data):
        for j in range(i):
            #ex1metas = ex1.getmetas()
            #ex2metas = data[j].getmetas()
            if not distance:
                c[i, j] = float(sum([v1 * metas[j].get(id, 0) for id, v1 in metas[i].items()]))
            else:
                try:
                    c[i, j] = 1. / float(sum([v1 * metas[j].get(id, 0) for id, v1 in metas[i].items()]))
                except:
                    c[i, j] = 10000000
            if normalize and c[i, j]:
                c[i, j] /= sqrt(sum([k**2 for k in metas[j].values()]) * sum([p**2 for p in metas[i].values()]))
            if callback: callback()
        
    print "Total time for cos was %s seconds" % str(time() - time1)
    return c


def FSMRandom(table, perc = True):
   from random import random
   words = {}
   for ex in table:
      for v in ex.getmetas().values():
         varname = v.variable.name
         if not words.has_key(varname):
            words[varname] = random()
   t = [(k, v) for k, v in words.items()]
   if perc:
      t.sort(cmp = lambda x, y: cmp(x[1], y[1]), reverse = True)
   return t
 


def FSMTDF(table, perc = True):
   words = {}
   for ex in table:
      for v in ex.getmetas().values():
         varname = v.variable.name
         if words.has_key(varname):
            words[varname] += 1.0
         else:
            words[varname] = 1.0
   t = [(k, v) for k, v in words.items()]
   if perc:
      t.sort(cmp = lambda x, y: cmp(x[1], y[1]), reverse = True)
   return t


def FSMTF(table, perc = True):
   words = {}
   #featureTotal = len(table.domain.getmetas())
   #featNo = featureTotal * perc / 100
   for ex in table:
      for v in ex.getmetas().values():
         varname = v.variable.name
         if words.has_key(varname):
            words[varname] += v.value
         else:
            words[varname] = v.value
   t = [(k, v) for k, v in words.items()]
   if perc:
      t.sort(cmp = lambda x, y: cmp(x[1], y[1]), reverse = True)
   return t
   #someList = [k for k, v in t] 
   #return set(someList[int(math.ceil(featNo)):])


def FSMMin(table, threshold, perc = True):
   """removes the features that occur less than a minimal threshold"""
   #gets a dictionary with examples already sorted by decreasing values
   #print 't %s ' % table
   if perc:
      featTotal = len(table)
      #number of features to remove
      featNo = int(math.ceil(featTotal * threshold))      
      return [i[0] for i in table[-featNo:]]
   
   else:
      return [i[0] for i in table if i[1] < threshold]
##      i = 0
##      while 1:
##         if table[i][1] < threshold or i == len(table) - 1:
##            break
##         i += 1
##      #feature has to have the value more than threshold to be kept
##      return [i[0] for i in table[i + 1:]]

def FSMMax(table, threshold, perc = True):
   """removes the features that occur more than a minimal threshold"""
   #gets a list of tuples with examples already sorted by decreasing values
   if perc:
      featTotal = len(table)
      #number of features to remove
      featNo = int(math.ceil(featTotal * threshold))
      return [i[0] for i in table[:featNo]]
   else:
      return [i[0] for i in table if i[1] > threshold]
##      i = len(table) - 1
##      while 1:
##         if table[i][1] > threshold or i == 0:
##            break
##         i -= 1
##      return [i[0] for i in table[:i + 1]]

def FSS(table, funcName, operator, threshold, perc = True):
   import math
   if perc and threshold > 1:
      threshold = threshold / 100.
      threshold = min(threshold, 1)
   operators = {'MAX': FSMMax, 'MIN': FSMMin}
   functions = {'TF': FSMTF, 'RAND': FSMRandom, 'TDF': FSMTDF}
   #each FSM function returs a set of metaattributes that need to be removed
   #newTable = orange.ExampleTable(table)
   #newTable.domain = orange.Domain(table.domain)
   removeList = operators[operator](functions[funcName](table, perc), threshold, perc)

   remMetas = set([])
##   for k in removeList:
##      met = table.domain.metaid(k)
##      #newTable.removeMetaAttribute(met)
##      #[ex.removemeta(k) for ex in newTable if ex.hasmeta(k)]
##      remMetas.add(met)
   remMetas = set(removeList)
   #a = set(table.domain.getmetas())
   a = set([i.name for i in table.domain.getmetas(str).values()])
   metas = a.difference(remMetas)
   #domaincopy = orange.Domain(table.domain.attributes, False) 
   #newTable = orange.ExampleTable(orange.Domain(domaincopy))

   metadict = dict([(table.domain.metaid(i), orange.FloatVariable(i)) for i in metas])
   print 'I know what to remove'
   #m2 = dict([(v.name, k) for k, v in metadict.items()])
##   for ex in table:
##      newex = orange.Example(domaincopy)
##      for att in newex.domain:
##         newex[att] = ex[att]
##      for k in ex.getmetas().keys():
##         if k in metadict.keys():
##            newex[k] = ex[k]
##      newTable.append(newex)

##   newTable = orange.ExampleTable(orange.Domain(table.domain.attributes), table)
##   newkeys = {}
##   for ex in table:
##      for k in ex.getmetas().keys():
##         if k in metadict.keys():
##            id = newkeys.get(metadict[k].name, 0)
##            if not id:
##               id = orange.newmetaid()
##               newkeys[metadict[k].name] = id
##            newex[id] = ex[k]
##      newTable.append(newex)
##   #newTable.domain.addmetas(metadict)
##   newTable.domain.addmetas(dict([(id, orange.FloatVariable(k)) for k, id in newkeys.items()]), True)

   newTable = orange.ExampleTable(orange.Domain(table.domain), table)
   newTable.domain.removemeta(removeList)
   for ex in newTable:
      for k, v in ex.getmetas().items():
         if not v.variable:
            ex.removemeta(k)
   return newTable


def DSMNF(table, threshold, max):
    #number of features, removes documents according to a number
    #of different features it has
    removeList = []
    for ex in table:
        features = len(ex.getmetas())
        if max and features > threshold:
            removeList.append(0)
        elif not max and features < threshold:
            removeList.append(0)
        else:
            removeList.append(1)
    return removeList
        


def DSMWF(table, threshold, max):
   """word frequency, removes documents according to the total number of words
   """
   removeList = []
   for ex in table:
      words = 0
      for freq in ex.getmetas().values():
         words += freq
      if max and words > threshold:
         removeList.append(0)
      elif not max and words < threshold:
         removeList.append(0)
      else:
         removeList.append(1)
   return removeList



def DSS(table, funcName, operator, threshold):
   """Document subset selection. Takes a function name and an operator and
    removes the documents with the desired measure below (or above) the threshold.
   """
   import math
   functions = {'WF': DSMWF, 'NF': DSMNF}
   newTable = orange.ExampleTable(table)
   operators = {'MAX': True, 'MIN': False}

   #removelist is a list of indices of examples that need to be removed(zeroes indicate that an example is to be removed)
   removeList = functions[funcName](table, threshold, operators[operator])

   removed = newTable.select(removeList, negate=1)
   newTable = newTable.select(removeList)
   removedMetas = set([])
   for ex in removed:
        for k in ex.getmetas().keys():
            removedMetas.add(k)
        
   
   for ex in newTable:
        for k, v in ex.getmetas().items():
            if k in removedMetas:
                removedMetas.remove(k)

   for k in removedMetas:
        newTable.domain.removemeta(k)
   return newTable

   

def extractLetterNGram(table, n=2, callback = None):
   """Builds the letter ngram features.
    n is the window size (size of ngrams).
   """
    
   domaincopy = orange.Domain(table.domain)
   newTable = orange.ExampleTable(table)
   #newTable.domain = orange.Domain(table.domain)

   ngramsSet = set([])
   allngrams = {}
   for ex in newTable:
      text = ex['text'].value
      i = 0
      ngrams = {}
      while i < len(text) - n + 1:
         ng = text[i:i+n]
         ngrams[ng] = ngrams.get(ng, 0) + 1.0
         i += 1
         
      #exdomain = ex.domain
      for k in ngrams.keys():
         id = allngrams.get(k, 0)
         if not id:
            id = orange.newmetaid()
            allngrams[k] = id
         ex[id] = ngrams[k]
      if callback: callback()

   newTable.domain.addmetas(dict([(id, orange.FloatVariable(k)) for k, id in allngrams.items()]), True)
   #table.domain = orange.Domain(domaincopy)
   table.changeDomain(domaincopy)
   #table.domain.removemeta(table.domain.getmetas().keys())
   return newTable




def extractWordNGram(table, preprocessor = None, n = 2, stopwords = None, threshold = 4, measure = 'FREQ'):
   """Builds the word ngram features."""
   import re
   domaincopy = orange.Domain(table.domain)
   newTable = orange.ExampleTable(table)
   seps = '.,!?()[]{}:; \n\r\t"\''
   notAllowed = ''
##   separators = set(seps)
   p = re.compile('[\.,!?(){}:;]')
   ps = re.compile('[ \n\r\t"]')
   na = re.compile('\\W')

############################################################################################################
##                                        DIGRAMS                                                         ##
############################################################################################################
   if n == 2:
      wordfreqs = {}
      digramfreqs = {}
      digrams = {}
      
      for ex in newTable:
         if not preprocessor:
            phrases = p.split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
         else:
            phrases = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
         #sad imam tokene, makni prazne stringove
         phrases = [i for i in phrases if i]
         for phrase in phrases:
             i = 0
             tokens = ps.split(phrase)
             tokens = [tok for tok in tokens if tok]
             if not tokens: continue
             while i < len(tokens) - 1:
                wordfreqs[tokens[i]] = wordfreqs.get(tokens[i], 0) + 1.0
                if stopwords:
                   if tokens[i].lower() in stopwords or tokens[i+1].lower() in stopwords or tokens[i].isdigit() or tokens[i+1].isdigit() or na.search(tokens[i]) or na.search(tokens[i+1]):
                      i += 1
                      continue
                digramfreqs[tokens[i] + ' ' + tokens[i+1]] = digramfreqs.get(tokens[i] + ' ' + tokens[i+1], 0) + 1.0
                i += 1
             #don't forget to count the last word
             wordfreqs[tokens[i]] = wordfreqs.get(tokens[i], 0) + 1.0

      #now we have all the needed information to comptue statistics and filter them (using threshold)
      digramFeatures = set([]) #this set contains the digrams that will be added as features
      N = sum(digramfreqs.values())
      M = sum(wordfreqs.values())
      if measure == 'FREQ':
         for k, v in digramfreqs.items():
            if v >= threshold:
               digramFeatures.add(k)
      elif measure == 'MI':
         from math import log
         for k, v in digramfreqs.items():
            mi = log((v * v * M * M) / (wordfreqs[k.split(' ')[0]] * wordfreqs[k.split(' ')[1]] * N), 2.)
            if mi >= threshold:
               digramFeatures.add(k)
      elif measure == 'DICE':
         for k, v in digramfreqs.items():
            dice = (2 * v) / (wordfreqs[k.split(' ')[0]] + wordfreqs[k.split(' ')[1]])
            if dice >= threshold:
               digramFeatures.add(k)
      elif measure == 'CHI':
##         N = sum(digramfreqs.values())
##         M = sum(wordfreqs.values())
         for k, v in digramfreqs.items():
            o11 = v
            o01 = wordfreqs[k.split(' ')[1]] - v + 1e-307
            o10 = wordfreqs[k.split(' ')[0]] - v + 1e-307
            o00 = N - v
            pa = wordfreqs[k.split(' ')[0]] / M
            pb = wordfreqs[k.split(' ')[1]] / M
            e11 = pa * pb * N
            e01 = (1 - pa) * pb * N
            e10 = pa * (1 - pb) * N
            e00 = (1 - pa) * (1 - pb) * N
            chi1 = ((e11 - o11) ** 2) / e11
            chi2 = ((e10 - o10) ** 2) / e10
            chi3 = ((e01 - o01) ** 2) / e01
            chi4 = ((e00 - o00) ** 2) / e00
            chi = chi1 + chi2 + chi3 + chi4
            if chi >= threshold:
               digramFeatures.add(k)
      elif measure == 'LL':
         from math import log
##         N = sum(digramfreqs.values())
##         M = sum(wordfreqs.values())
         for k, v in digramfreqs.items():
            o11 = v
            o01 = wordfreqs[k.split(' ')[1]] - v + 1e-307
            o10 = wordfreqs[k.split(' ')[0]] - v + 1e-307
            o00 = N - v
            pa = wordfreqs[k.split(' ')[0]] / M
            pb = wordfreqs[k.split(' ')[1]] / M
            e11 = pa * pb * N
            e01 = (1 - pa) * pb * N
            e10 = pa * (1 - pb) * N
            e00 = (1 - pa) * (1 - pb) * N
            log1 = o11 * (log(o11, 10) - log(e11, 10))
            log2 = o10 * (log(o10, 10) - log(e10, 10))
            log3 = o01 * (log(o01, 10) - log(e01, 10))
            log4 = o00 * (log(o00, 10) - log(e00, 10))
            ll = log1 + log2 + log3 + log4
            if ll >= threshold:
               digramFeatures.add(k)
               
      #finally, add the features         
      for ex in newTable:
         if not preprocessor:
            phrases = p.split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
         else:
            phrases = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
         #sad imam tokene, makni prazne stringove
         phrases = [i for i in phrases if i]
         localdigrams = {}
         for phrase in phrases:
             i = 0
             tokens = ps.split(phrase)
             tokens = [tok for tok in tokens if tok]
             while i < len(tokens) - 1:
                if tokens[i] + ' ' + tokens[i+1] in digramFeatures:
                   localdigrams[tokens[i] + ' ' + tokens[i+1]] = localdigrams.get(tokens[i] + ' ' + tokens[i+1], 0) + 1.0
                i += 1
                
         for k in localdigrams.keys():
            id = digrams.get(k, 0)
            if not id:
               id = orange.newmetaid()
               digrams[k] = id
            ex[id] = localdigrams[k]

      newTable.domain.addmetas(dict([(id, orange.FloatVariable(k)) for k, id in digrams.items()]), True)

############################################################################################################
##                                        TRIGRAMS                                                        ##
############################################################################################################
   elif n == 3:
      wordfreqs = {}
      digramfreqs = {}
      trigramfreqs = {}
      trigrams = {}
      
      for ex in newTable:
         if not preprocessor:
            phrases = p.split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
         else:
            phrases = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
         #sad imam tokene, makni prazne stringove
         phrases = [i for i in phrases if i]
         for phrase in phrases:
             i = 0
             tokens = ps.split(phrase)
             tokens = [tok for tok in tokens if tok]
             if not tokens: continue
             while i < len(tokens) - 2:
                wordfreqs[tokens[i]] = wordfreqs.get(tokens[i], 0) + 1.0
                digramfreqs[tokens[i] + ' ' + tokens[i+1]] = digramfreqs.get(tokens[i] + ' ' + tokens[i+1], 0) + 1.0
                if stopwords:
                   if tokens[i].lower() in stopwords or tokens[i+2].lower() in stopwords or tokens[i].isdigit() or tokens[i+2].isdigit() or na.search(tokens[i]) or na.search(tokens[i+2]):
                      i += 1
                      continue
                trigramfreqs[tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2]] = trigramfreqs.get(tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2], 0) + 1.0
                i += 1
             #don't forget to count the last words
             if len(tokens) >= 1:
                wordfreqs[tokens[i]] = wordfreqs.get(tokens[i], 0) + 1.0
                if len(tokens)>=2:
                     wordfreqs[tokens[i+1]] = wordfreqs.get(tokens[i+1], 0) + 1.0
                     digramfreqs[tokens[i] + ' ' + tokens[i+1]] = digramfreqs.get(tokens[i] + ' ' + tokens[i+1], 0) + 1.0

      trigramFeatures = set([]) #this set contains the trigrams that will be added as features
      N = sum(trigramfreqs.values())
      M = sum(wordfreqs.values())
      if measure == 'FREQ':
         for k, v in trigramfreqs.items():
            if v >= threshold:
               trigramFeatures.add(k)
      elif measure == 'MI':
##         N = len(trigramfreqs)
##         M = len(wordfreqs)
         from math import log
         for k, v in trigramfreqs.items():
            mi = log((v * M * M * M) / (wordfreqs[k.split(' ')[0]] * wordfreqs[k.split(' ')[1]] * wordfreqs[k.split(' ')[2]] * N), 2.)
            if mi >= threshold:
               trigramFeatures.add(k)
      elif measure == 'H':
         if not stopwords:
            return table
         from math import log
##         N = len(trigramfreqs)
         for k, v in trigramfreqs.items():
            if wordfreqs[k.split(' ')[1]] in stopwords:
               h = 2 * log((v * N) / (wordfreqs[k.split(' ')[0]] * wordfreqs[k.split(' ')[2]]), 2.)
            else:
               h = log((v * N * N) / (wordfreqs[k.split(' ')[0]] * wordfreqs[k.split(' ')[1]] * wordfreqs[k.split(' ')[2]]), 2.)
            if h >= threshold:
               trigramFeatures.add(k)
      elif measure == 'DICE':
         for k, v in trigramfreqs.items():
            dice = (3 * v) / (wordfreqs[k.split(' ')[0]] + wordfreqs[k.split(' ')[1]] + wordfreqs[k.split(' ')[2]])
            if dice >= threshold:
               trigramFeatures.add(k)
      elif measure == 'CHI':
##         N = sum(trigramfreqs.values())
##         M = sum(wordfreqs.values())
         for k, v in trigramfreqs.items():
            splitList = k.split(' ')
            o000 = N - v
            o001 = wordfreqs[splitList[2]] - v + 1e-307
            o010 = wordfreqs[splitList[1]] - v + 1e-307
            o100 = wordfreqs[splitList[0]] - v + 1e-307
            o110 = digramfreqs[splitList[0] + ' ' + splitList[1]] - v + 1e-307
            o011 = digramfreqs[splitList[1] + ' ' + splitList[2]] - v + 1e-307
            o111 = v
            pa = wordfreqs[splitList[0]] / M
            pb = wordfreqs[splitList[1]] / M
            pc = wordfreqs[splitList[2]] / M
            e000 = (1 - pa) * (1 - pb) * (1 - pc) * N
            e001 = (1 - pa) * (1 - pb) * pc * N
            e010 = (1 - pa) * pb * (1 - pc) * N
            e100 = pa * (1 - pb) * (1 - pc) * N
            e110 = pa * pb * (1 - pc) * N
            e011 = (1 - pa) * pb * pc * N
            e111 = pa * pb * pc * N
            
            chi1 = ((e111 - o111) ** 2) / e111
            chi2 = ((e100 - o100) ** 2) / e100
            chi3 = ((e001 - o001) ** 2) / e001
            chi4 = ((e010 - o010) ** 2) / e010
            chi5 = ((e000 - o000) ** 2) / e000
            chi6 = ((e011 - o011) ** 2) / e011
            chi7 = ((e110 - o110) ** 2) / e110
            chi = chi1 + chi2 + chi3 + chi4 + chi5 + chi6 + chi7
            if chi >= threshold:
               trigramFeatures.add(k)
      elif measure == 'LL':
         from math import log
##         N = sum(trigramfreqs.values())
##         M = sum(wordfreqs.values())
         for k, v in trigramfreqs.items():
            splitList = k.split(' ')
            o000 = N - v
            o001 = wordfreqs[splitList[2]] - v + 1e-307
            o010 = wordfreqs[splitList[1]] - v + 1e-307
            o100 = wordfreqs[splitList[0]] - v + 1e-307
            o110 = digramfreqs[splitList[0] + ' ' + splitList[1]] - v + 1e-307
            o011 = digramfreqs[splitList[1] + ' ' + splitList[2]] - v + 1e-307
            o111 = v
            pa = wordfreqs[splitList[0]] / M
            pb = wordfreqs[splitList[1]] / M
            pc = wordfreqs[splitList[2]] / M
            e000 = (1 - pa) * (1 - pb) * (1 - pc) * N
            e001 = (1 - pa) * (1 - pb) * pc * N
            e010 = (1 - pa) * pb * (1 - pc) * N
            e100 = pa * (1 - pb) * (1 - pc) * N
            e110 = pa * pb * (1 - pc) * N
            e011 = (1 - pa) * pb * pc * N
            e111 = pa * pb * pc * N
            
            log1 = o111 * (log(o111, 10) - log(e111, 10))
            log2 = o110 * (log(o110, 10) - log(e110, 10))
            log3 = o011 * (log(o011, 10) - log(e011, 10))
            log4 = o001 * (log(o001, 10) - log(e001, 10))
            log5 = o100 * (log(o100, 10) - log(e100, 10))
            log6 = o010 * (log(o010, 10) - log(e010, 10))
            log7 = o000 * (log(o000, 10) - log(e000, 10))
            ll = log1 + log2 + log3 + log4 + log5 + log6 + log7
            if ll >= threshold:
               trigramFeatures.add(k)               
               
      #finally, add the features         
      for ex in newTable:
         if not preprocessor:
            phrases = p.split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
         else:
            phrases = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
         #sad imam tokene, makni prazne stringove
         phrases = [i for i in phrases if i]
         localtrigrams = {}
         for phrase in phrases:
             i = 0
             tokens = ps.split(phrase)
             tokens = [tok for tok in tokens]
             while i < len(tokens) - 2:
                if tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2] in trigramFeatures:
                   localtrigrams[tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2]] = localtrigrams.get(tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2], 0) + 1.0
                i += 1
            
         for k in localtrigrams.keys():
            id = trigrams.get(k, 0)
            if not id:
               id = orange.newmetaid()
               trigrams[k] = id
            ex[id] = localtrigrams[k]

      newTable.domain.addmetas(dict([(id, orange.FloatVariable(k)) for k, id in trigrams.items()]), True)

############################################################################################################
##                                        TETRAGRAMS                                                      ##
############################################################################################################
      
   elif n == 4:
      wordfreqs = {}
      digramfreqs = {}
      trigramfreqs = {}
      tetragramfreqs = {}
      tetragrams = {}
      
      for ex in newTable:
         if not preprocessor:
            phrases = p.split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
         else:
            phrases = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
         #sad imam tokene, makni prazne stringove
         phrases = [i for i in phrases if i]
         for phrase in phrases:
             i = 0
             tokens = ps.split(phrase)
             tokens = [tok for tok in tokens if tok]
             if not tokens: continue
             while i < len(tokens) - 3:
                wordfreqs[tokens[i]] = wordfreqs.get(tokens[i], 0) + 1.0
                digramfreqs[tokens[i] + ' ' + tokens[i+1]] = digramfreqs.get(tokens[i] + ' ' + tokens[i+1], 0) + 1.0
                trigramfreqs[tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2]] = trigramfreqs.get(tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2], 0) + 1.0
                if stopwords:
                   if tokens[i].lower() in stopwords or tokens[i+3].lower() in stopwords or tokens[i].isdigit() or tokens[i+3].isdigit() or na.search(tokens[i]) or na.search(tokens[i+3]):
                      i += 1
                      continue
                tetragramfreqs[tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2] + ' ' + tokens[i+3]] = tetragramfreqs.get(tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2] + ' ' + tokens[i+3], 0) + 1.0
                i += 1
             #don't forget to count the last words
             lt = len(tokens)
             if lt >= 1:
                wordfreqs[tokens[i]] = wordfreqs.get(tokens[i], 0) + 1.0
                if lt >= 2:
                    wordfreqs[tokens[i+1]] = wordfreqs.get(tokens[i+1], 0) + 1.0
                    digramfreqs[tokens[i] + ' ' + tokens[i+1]] = digramfreqs.get(tokens[i] + ' ' + tokens[i+1], 0) + 1.0
                    if lt >= 3:
                        wordfreqs[tokens[i+2]] = wordfreqs.get(tokens[i+2], 0) + 1.0                
                        digramfreqs[tokens[i+1] + ' ' + tokens[i+2]] = digramfreqs.get(tokens[i+1] + ' ' + tokens[i+2], 0) + 1.0
                        trigramfreqs[tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2]] = trigramfreqs.get(tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2], 0) + 1.0

      tetragramFeatures = set([]) #this set contains the tetragrams that will be added as features
      N = sum(tetragramfreqs.values())
      M = sum(wordfreqs.values())
      if measure == 'FREQ':
         for k, v in tetragramfreqs.items():
            if v >= threshold:
               tetragramFeatures.add(k)
      elif measure == 'MI':
##         N = len(tetragramfreqs)
##         M = len(wordfreqs)
         from math import log
         for k, v in tetragramfreqs.items():
            mi = log((v * M * M * M * M) / (wordfreqs[k.split(' ')[0]] * wordfreqs[k.split(' ')[1]] * wordfreqs[k.split(' ')[2]] * wordfreqs[k.split(' ')[3]] * N), 2.)
            if mi >= threshold:
               tetragramFeatures.add(k)
      elif measure == 'DICE':
         for k, v in tetragramfreqs.items():
            dice = (4 * v) / (wordfreqs[k.split(' ')[0]] + wordfreqs[k.split(' ')[1]] + wordfreqs[k.split(' ')[2]] + wordfreqs[k.split(' ')[3]])
            if dice >= threshold:
               tetragramFeatures.add(k)
      elif measure == 'CHI':
##         N = len(tetragramfreqs)
##         M = len(wordfreqs)
         for k, v in tetragramfreqs.items():
            splitList = k.split(' ')
            o0000 = N - v
            o0001 = wordfreqs[splitList[3]] - v + 1e-307
            o0010 = wordfreqs[splitList[2]] - v + 1e-307
            o0100 = wordfreqs[splitList[1]] - v + 1e-307
            o1000 = wordfreqs[splitList[0]] - v + 1e-307
            o0011 = digramfreqs[splitList[2] + ' ' + splitList[3]] - v + 1e-307
            o0110 = digramfreqs[splitList[1] + ' ' + splitList[2]] - v + 1e-307
            o1100 = digramfreqs[splitList[0] + ' ' + splitList[1]] - v + 1e-307
            o0111 = trigramfreqs[splitList[1] + ' ' + splitList[2] + ' ' + splitList[3]] - v + 1e-307
            o1110 = trigramfreqs[splitList[0] + ' ' + splitList[1] + ' ' + splitList[2]] - v + 1e-307
            o1111 = v
            pa = splitList[0] / M
            pb = splitList[1] / M
            pc = splitList[2] / M
            pd = splitList[3] / M
            e0000 = (1 - pa) * (1 - pb) * (1 - pc) * (1 - pd) * N
            e0001 = (1 - pa) * (1 - pb) * (1 - pc) * pd * N
            e0010 = (1 - pa) * (1 - pb) * pc * (1 - pd) * N
            e0100 = (1 - pa) * pb * (1 - pc) * (1 - pd) * N
            e1000 = pa * (1 - pb) * (1 - pc) * (1 - pd) * N
            e0011 = (1 - pa) * (1 - pb) * pc * pd * N
            e0110 = (1 - pa) * pb * pc * (1 - pd) * N
            e1100 = pa * pb * (1 - pc) * (1 - pd) * N
            e0111 = (1 - pa) * pb * pc * pd * N
            e1110 = pa * pb * pc * (1 - pd) * N
            e1111 = pa * pb * pc * pd * N
            
            chi1 = ((e1111 - o1111) ** 2) / e1111
            chi2 = ((e0001 - o0001) ** 2) / e0001
            chi3 = ((e0010 - o0010) ** 2) / e0010
            chi4 = ((e0100 - o0100) ** 2) / e0100
            chi5 = ((e1000 - o1000) ** 2) / e1000
            chi6 = ((e0011 - o0011) ** 2) / e0011
            chi7 = ((e0110 - o0110) ** 2) / e0110
            chi8 = ((e1100 - o1100) ** 2) / e1100
            chi9 = ((e1110 - o1110) ** 2) / e1110
            chi10 = ((e0111 - o0111) ** 2) / e0111
            chi11 = ((e0000 - o0000) ** 2) / e0000
            chi = chi1 + chi2 + chi3 + chi4 + chi5 + chi6 + chi7 + chi8 + chi9 + chi10 + chi11
            if chi >= threshold:
               tetragramFeatures.add(k)
      elif measure == 'LL':
         from math import log
##         N = len(tetragramfreqs)
##         M = len(wordfreqs)
         for k, v in tetragramfreqs.items():
            splitList = k.split(' ')
            o0000 = N - v
            o0001 = wordfreqs[splitList[3]] - v + 1e-307
            o0010 = wordfreqs[splitList[2]] - v + 1e-307
            o0100 = wordfreqs[splitList[1]] - v + 1e-307
            o1000 = wordfreqs[splitList[0]] - v + 1e-307
            o0011 = digramfreqs[splitList[2] + ' ' + splitList[3]] - v + 1e-307
            o0110 = digramfreqs[splitList[1] + ' ' + splitList[2]] - v + 1e-307
            o1100 = digramfreqs[splitList[0] + ' ' + splitList[1]] - v + 1e-307
            o0111 = trigramfreqs[splitList[1] + ' ' + splitList[2] + ' ' + splitList[3]] - v + 1e-307
            o1110 = trigramfreqs[splitList[0] + ' ' + splitList[1] + ' ' + splitList[2]] - v + 1e-307
            o1111 = v
            pa = splitList[0] / M
            pb = splitList[1] / M
            pc = splitList[2] / M
            pd = splitList[3] / M
            e0000 = (1 - pa) * (1 - pb) * (1 - pc) * (1 - pd) * N
            e0001 = (1 - pa) * (1 - pb) * (1 - pc) * pd * N
            e0010 = (1 - pa) * (1 - pb) * pc * (1 - pd) * N
            e0100 = (1 - pa) * pb * (1 - pc) * (1 - pd) * N
            e1000 = pa * (1 - pb) * (1 - pc) * (1 - pd) * N
            e0011 = (1 - pa) * (1 - pb) * pc * pd * N
            e0110 = (1 - pa) * pb * pc * (1 - pd) * N
            e1100 = pa * pb * (1 - pc) * (1 - pd) * N
            e0111 = (1 - pa) * pb * pc * pd * N
            e1110 = pa * pb * pc * (1 - pd) * N
            e1111 = pa * pb * pc * pd * N
            
            log1 = o1111 * (log(o1111, 10) - log(e1111, 10))
            log2 = o0001 * (log(o0001, 10) - log(e0001, 10))
            log3 = o0010 * (log(o0010, 10) - log(e0010, 10))
            log4 = o0100 * (log(o0100, 10) - log(e0100, 10))
            log5 = o1000 * (log(o1000, 10) - log(e1000, 10))
            log6 = o0011 * (log(o0011, 10) - log(e0011, 10))
            log7 = o0110 * (log(o0110, 10) - log(e0110, 10))
            log8 = o1100 * (log(o1100, 10) - log(e1100, 10))
            log9 = o0111 * (log(o0111, 10) - log(e0111, 10))
            log10 = o1110 * (log(o1110, 10) - log(e1110, 10))
            log11 = o0000 * (log(o0000, 10) - log(e0000, 10))
            ll = log1 + log2 + log3 + log4 + log5 + log6 + log7 + log8 + log9 + log10 + log11
            if ll >= threshold:
               tetragramFeatures.add(k)                           

      #finally, add the features         
      for ex in newTable:
         if not preprocessor:
            phrases = p.split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
         else:
            phrases = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
         #sad imam tokene, makni prazne stringove
         phrases = [i for i in phrases if i]
         localtetragrams = {}
         for phrase in phrases:
            i = 0
            tokens = ps.split(phrase)
            tokens = [tok for tok in tokens if tok]
            while i < len(tokens) - 3:
                if tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2] + ' ' + tokens[i+3] in tetragramFeatures:
                   localtetragrams[tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2] + ' ' + tokens[i+3]] = localtetragrams.get(tokens[i] + ' ' + tokens[i+1] + ' ' + tokens[i+2] + ' ' + tokens[i+3], 0) + 1.0
                i += 1
            
         for k in localtetragrams.keys():
            id = tetragrams.get(k, 0)
            if not id:
               id = orange.newmetaid()
               tetragrams[k] = id
            ex[id] = localtetragrams[k]

      newTable.domain.addmetas(dict([(id, orange.FloatVariable(k)) for k, id in tetragrams.items()]), True)         
   else:
      return table
   table.changeDomain(domaincopy)
   return newTable


def extractNames(text):
   """Return a list of named entities. This function is called by
    extractNamedEntities function. """

   in1 = set('.!?()[]{}/\\<>:;')
   in2 = set(',\'"')
   name = ''
   names = []
   state = 0
   for letter in text:
      if state == 0:
         if letter.isalnum():
            state = 4
      elif state == 1:
         if letter.isupper(): #or isdigit
            state = 2
            name += letter
         elif letter in in1:
            state = 0
      elif state == 2:
         if letter.isspace():
            name += ' '
            state = 3
         elif letter in in1:
            state = 0
            names.append(name)
            name = ''
         elif letter.islower() or letter.isupper() or letter.isdigit():
            name += letter
         elif letter in in2:
            name += letter
            state = 3
      elif state == 3:
         if letter.islower() or letter in in1 or letter.isdigit():
            names.append(name[:-1])
            name = ''
            state = 1
         elif letter.isupper():# or letter.isdigit()
            name += letter
            state = 2
         elif letter.isspace() or letter in in2:
            name += letter
      elif state == 4:
         if letter.isspace() or letter in in1 or letter in in2:
            state = 1
            
   if name:
      names.append(name)
   return [w.rstrip(',\'" ') for w in names]


def extractNamedEntities(table, preprocessor = None, stopwords = None, callback = None):
   """Adds named entities to an ExampleTable in a similar way bagOfWords adds
    words."""
    
   p = re.compile('[\.,!?(){}:; \n\r\t"]')
   na = re.compile('\\W')
   domaincopy = orange.Domain(table.domain)
   newTable = orange.ExampleTable(table)
   #newTable.domain = orange.Domain(table.domain)

   allNames = {}
   for ex in newTable:
      if not preprocessor:
         tokens = p.split(ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore'))
      else:
         tokens = preprocessor.removeStopwords(preprocessor.tokenize(preprocessor.lemmatize(preprocessor.lowercase(ex['text'].value))))
         
      flag = False
      hadName = False
      names = {}
      name = ''
      for token in tokens:
         if flag and token and (token[0].isupper() or token[0].isdigit()):
            name += token + ' '
            hadName = True
         elif hadName:
            if name[:-1].find(' ') == -1 and (len(name) <= 4 or name.isdigit()):
               pass
            else:
               names[name] = names.get(name, 0) + 1.0
            name = ''
            hadName = False
         flag = token

      text = ex['text'].value.decode('utf-8','ignore').encode('cp1250','ignore')
      names = extractNames(text)
      #some postprocessing is in order, remove stopwords and one-letter words
      if stopwords:
        names = [n for n in names if n.lower() not in stopwords]
      names = [n for n in names if len(n) > 1]
      names = dict([(n, float(text.count(n))) for n in names])         
      #exdomain = ex.domain
      for k in names.keys():
         id = allNames.get(k, 0)
         if not id:
            id = orange.newmetaid()
            allNames[k] = id
         ex[id] = names[k]

   newTable.domain.addmetas(dict([(id, orange.FloatVariable(k)) for k, id in allNames.items()]), True)
   #table.domain = orange.Domain(domaincopy)
   table.changeDomain(domaincopy)
   #table.domain.removemeta(table.domain.getmetas().keys())
   return newTable
   



