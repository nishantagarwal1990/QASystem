import nltk
import os
#from nltk.corpus import conll2000
#from code_classifier_chunker import ConsecutiveNPChunker
jar_folder = "/Users/nishantagarwal/stanford-ner-2015-04-20/stanford-ner.jar"
os.environ['CLASSPATH']=jar_folder

from nltk.tag import StanfordNERTagger
path_to_jar = "/Users/nishantagarwal/stanford-ner-2015-04-20/stanford-ner.jar"
path_to_model = "/Users/nishantagarwal/stanford-ner-2015-04-20/classifiers/english.all.3class.distsim.crf.ser.gz"#english.muc.7class.distsim.crf.ser.gz"
#train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])
#test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
#chunker = ConsecutiveNPChunker(train_sents)
l = 'The school has turned its one-time metal shop - lost to budget cuts almost two years ago - \
into a money-making professional fitness club.'
#print chunker.parse(l)
grammar = "NP: {<LOCATION><O>?<LOCATION>+}"
qetag = StanfordNERTagger(path_to_model,path_to_jar)
l = nltk.word_tokenize(l)
ne_tagged = qetag.tag(l)
tagged =  nltk.pos_tag(l)
print tagged
print ne_tagged
cp = nltk.RegexpParser(grammar)
tre = cp.parse(ne_tagged)
for subtree in tre.subtrees():
	if subtree.label() == 'NP':
		break
#print subtree.leaves()
#print(chunker.evaluate(test_sents))
#subtree = subtree.leaves()
answer = ' '.join(word for word,pos in subtree.leaves())
print answer
#qetag = StanfordNERTagger(path_to_model,path_to_jar)
#print qetag.tag(l)