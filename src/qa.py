import sys
import os
import string
import nltk
jar_folder = "/Users/nishantagarwal/stanford-ner-2015-04-20/stanford-ner.jar"
os.environ['CLASSPATH']=jar_folder
#nltk.data.path.append('/home/nishanta/nltk_data')
import re

from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet	import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.tag import StanfordNERTagger

path_to_jar = "/Users/nishantagarwal/stanford-ner-2015-04-20/stanford-ner.jar"
path_to_model = "/Users/nishantagarwal/stanford-ner-2015-04-20/classifiers/english.all.3class.distsim.crf.ser.gz"
stopwords = ['is','a','an','the','are','who','when','where','what','why','who','in','at','on','by','can', 'could', 'may', \
				'might', 'must', 'ought to', 'shall', 'should', 'will', 'would','am','was','were','does','do','did','has','have','had'\
				,'to','of','we','i','he','she','me','they','that','each','him','his','hers','ours','her','you',\
				'nearby','above','below','over','under','up','down','around','himself','herself','themselves','someone','as','such',\
				'anything','everything','any','The','A','An']
#location_prep = ['in','at','near','inside','on','by','nearby','above','below','over','under','up','down','around',\
					#'through','outside','between','beside','beyond','behind','within','underneath','among','along','against']

months = ['january','february','march','april','may','june','july','august','september','october','november','december','jan','feb'\
			,'mar','apr','jun','jul','aug','sept','oct','nov','dec']

location_prep = [line.strip() for line in open("location_prep.txt", 'r')]
time = [line.strip() for line in open("time.txt", 'r')]
prep = [line.strip() for line in open("prep.txt", 'r')]
measure = ['sq','square','feet','ft','sq-ft','inches','cms','centimeters','yard','km','meter','m','mm','millimeter','long']
cost = ['$','dollars','cost','price','cent','euro','million','nickle','penny','quarter','dime']
nertag = StanfordNERTagger(path_to_model,path_to_jar)
verb_match = 6
other_match = 3
clue = 3
good_clue = 4
confident = 6
slam_dunk = 20
punctuation = list(string.punctuation) + ["''","...","``",'""']
punctuation.remove("$")


def printanswer(sentence,question):
	tok_sent = nltk.word_tokenize(sentence)
	filt_sent = list()
	for w in tok_sent:
		if (w.lower() not in stopwords) and (w not in punctuation) and (w not in question):
			filt_sent.append(w)
	
	print("Answer: " + ' '.join(filt_sent)+'\n' )

def wherequestype(question,sentences,sentence_score,ne_tagged_sent):
	found_phrase = 0
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	for i in xrange(len(sentence_score)):
		for word in sentences[i]:
			if word in location_prep:
				sentence_score[i] += good_clue
				break
		for word,pos in ne_tagged_sent[i]:
			if pos == 'LOCATION':
				sentence_score[i] += confident
				break

	max_val = -1
	index = -1

	for i in xrange(len(sentence_score)):
		if sentence_score[i] > max_val:
			max_val = sentence_score[i]
			index = i

	
	answer = ''	
	if not found_phrase:
		grammar = """NP: {(<LOCATION><O>)?<LOCATION>+}"""
		cp = nltk.RegexpParser(grammar)
		tre = cp.parse(ne_tagged_sent[index])
		for subtree in tre.subtrees():
			if subtree.label() == 'NP':
				found_phrase = 1
				break
		
		if not found_phrase:
			for m in xrange(max(0,index-2), index):
				tre = cp.parse(ne_tagged_sent[m])
				for subtree in tre.subtrees():
					if subtree.label() == 'NP':
						found_phrase = 1
						break
				if found_phrase:
					break
		
		if found_phrase:
			answer = ' '.join(word for word,pos in subtree.leaves())

	if not found_phrase:
		grammar = """
					NP: {<IN>+<DT>+<JJ>*<NN><POS>?<NN>+}"""
		#l = nltk.word_tokenize(comp_sentences[index])
		tagged =  nltk.pos_tag(sentences[index])
		cp = nltk.RegexpParser(grammar)
		tre = cp.parse(tagged)
		for subtree in tre.subtrees():
			if subtree.label() == 'NP':
				found_phrase = 1
				break
		if found_phrase:
			answer = ' '.join(word for word,pos in subtree.leaves())


	if not answer:
		print ("Answer: "+comp_sentences[index]+'\n')

	else:
		print ("Answer: "+answer+'\n')

def whoquestype(question,sentences,sentence_score,ne_tagged_sent):
	found_phrase = 0
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	ne_tagged_ques = nertag.tag(question)
	for i in xrange(len(sentence_score)):
		found_q = 0
		found_sent = 0
		found_name = 0
		for word in sentences[i]:
			if word.lower() == 'name':
				found_name = 1
				break
		for word,pos in ne_tagged_sent[i]:
			if pos == 'PERSON':
				found_sent = 1
				break
		for word,pos in ne_tagged_ques:
			if pos == 'PERSON':
				found_q = 1
				break

		if not found_q and found_sent:
			sentence_score[i] += confident

		if not found_q and found_name:
			sentence_score[i] += good_clue

		if found_sent:
			sentence_score[i] += good_clue

	max_val = -1
	index = -1

	for i in xrange(len(sentence_score)):
		if sentence_score[i] > max_val:
			max_val = sentence_score[i]
			index = i
	
	answer = ''
	if not found_phrase:
		grammar = """
					NP: {(<PERSON><O>+)?(<PERSON>|<ORGANIZATION>)+}"""
		cp = nltk.RegexpParser(grammar)
		tre = cp.parse(ne_tagged_sent[index])
		for subtree in tre.subtrees():
			if subtree.label() == 'NP':
				found_phrase = 1
				break
		if found_phrase:
			answer = ' '.join(word for word,pos in subtree.leaves())


	if not answer:
		print ("Answer: "+comp_sentences[index]+'\n')

	else:
		print ("Answer: "+answer+'\n')
	

def whenquestype(question,sentences,sentence_score,ne_tagged_sent):
	found_phrase = 0
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	score = dict()
	for i in xrange(len(sentence_score)):
		score[i] = 0
	for i in xrange(len(sentence_score)):
		for word,pos in ne_tagged_sent[i]:
			if word in time:
				score[i] += sentence_score[i]
				score[i] += good_clue
				break
		for word in sentences[i]:
			if word in ['first','last','since','ago'] and 'the' in question and 'last' in question:
				score[i] += slam_dunk
				break
		for word in sentences[i]:
			if ('start' in question or 'begin' in question) and word in ['start','begin','since','year']:
				score[i] += slam_dunk
				break

	max_val = -1
	index = -1

	for i in xrange(len(score)):
		if score[i] > max_val:
			max_val = score[i]
			index = i

	answer = ''
	if not found_phrase:
		grammar = """
					NP: {(<CD>?<TO>?<CD>?|<IN>?<DT><NN>)}"""
		cp = nltk.RegexpParser(grammar)
		tagged =  nltk.pos_tag(sentences[index])
		tre = cp.parse(tagged)
		for subtree in tre.subtrees():
			if subtree.label() == 'NP':
				found_phrase = 1
				break
		if found_phrase:
			answer = ' '.join(word for word,pos in subtree.leaves())

	#print ("Answer: "+comp_sentences[index]+'\n')
	if not answer:
		print ("Answer: "+comp_sentences[index]+'\n')

	else:
		print ("Answer: "+answer+'\n')

def whatquestype(question,sentences,sentence_score,ne_tagged_sent):
	found_phrase = 0
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	pos_ques = nltk.pos_tag(question)


	for i in xrange(len(sentence_score)):
		for word in question:
			if word.lower() in months and ('today' in sentences[i] or 'yesterday' in sentences[i] or 'tomorrow' in sentences[i]\
				or ('last' in sentences[i] and 'night' in sentences[i])):
				sentence_score[i] +=clue
		if 'kind' in question and ('call' in sentences[i] or 'from' in sentences[i]):
			sentence_score[i] += good_clue
		
		if 'name' in question and ('name' in sentences[i] or 'call' in sentences[i] or 'known' in sentences[i]):
			sentence_score[i] += slam_dunk

		if ('name' in question and any(w in prep for w in question) and any(w[0].isupper() for w in sentences[i] if w not in stopwords)):#('of' in question or 'for' in question)):
			index = question.index('name')
			search = [pos_ques[j][0] for j in xrange(index+2,len(pos_ques)) if pos_ques[j][1] == 'NN' or pos_ques[j][1] == 'NNP']
			for s in search:
				if s in sentences[i]:
					sentence_score[i] += slam_dunk
					break

	max_val = -1
	index = -1

	for i in xrange(len(sentence_score)):
		if sentence_score[i] > max_val:
			max_val = sentence_score[i]
			index = i

	#ne_tagged_sent = nertag.tag(sentences[index])
	#print ne_tagged_sent
	#print sentence_score
	#answer = ''
	#answer = ' '.join([ne_tagged_sent[j][0] for j in xrange(len(ne_tagged_sent)) if ne_tagged_sent[j][1] == 'LOCATION' \
										#or (ne_tagged_sent[j][0] == ',' and ne_tagged_sent[j+1][1] == 'LOCATION')])

	#print ("Answer: "+comp_sentences[index]+'\n')
	printanswer(comp_sentences[index],question)

def whyquestype(question,sentences,sentence_score,ne_tagged_sent):
	#print "here5"
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	best = list()
	score = dict()
	max_score = -1
	min_score = 999
	for i in xrange(len(sentence_score)):
		if sentence_score[i] > max_score:
			max_score = sentence_score[i]
		if sentence_score[i] < min_score:
			min_score = sentence_score[i]

	mid_score = (max_score+min_score)/2
	for i in xrange(len(sentence_score)):
		if sentence_score[i] > mid_score:
			best.append(i)

	for i in xrange(len(sentence_score)):
		score[i] = 0

	for i in xrange(len(sentence_score)):
		if i in best:
			score[i] += clue
		if i+1 in best:
			score[i] += clue
		if i-1 in best:
			score[i] += good_clue
		if 'want' in sentences[i]:
			score[i] += good_clue
		if 'so' in sentences[i] or 'because' in sentences[i]:
			score[i] += good_clue

	max_val = -1
	index = -1

	for i in xrange(len(sentence_score)):
		if score[i] >= max_val:
			max_val = score[i]
			index = i

	#ne_tagged_sent = nertag.tag(sentences[index])
	#print ne_tagged_sent
	#print sentence_score
	#answer = ''
	#answer = ' '.join([ne_tagged_sent[j][0] for j in xrange(len(ne_tagged_sent)) if ne_tagged_sent[j][1] == 'LOCATION' \
										#or (ne_tagged_sent[j][0] == ',' and ne_tagged_sent[j+1][1] == 'LOCATION')])

	#print ("Answer: "+comp_sentences[index]+'\n')
	printanswer(comp_sentences[index],question)

def howquestype(question,sentences,sentence_score,ne_tagged_sent):
	#print "here6"
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	lower_question = [w.lower() for w in question]
	index_how = lower_question.index('how')
	if lower_question[index_how+1] in ['big','small','large','far','long','tall','short']:
		for i in xrange(len(sentence_score)):
			for word in sentences[i]:
				if word in measure :
					sentence_score[i] += slam_dunk
					break
	for i in xrange(len(sentence_score)):
		for word,pos in ne_tagged_sent[i]:
			if lower_question[index_how+1] == 'much' or (lower_question[index_how+1] == 'many' and lower_question[index_how+2] in cost):
				if word in cost or (word.isdigit() and any(w in sentences[i] for w in cost)):
					sentence_score[i] += confident
					break
			if (word in ['age','old','years','yrs']) and ('age' in question or 'old' in question):
				sentence_score[i] += confident
				break
			if lower_question[index_how+1] == 'many' and word.isdigit() and (word not in time or word not in cost) and \
				lower_question[index_how+2] in sentences[i]:
				#print word
				#print ne_tagged_sent[i]
				sentence_score[i] += slam_dunk
				break


	max_val = -1
	index = -1

	for i in xrange(len(sentence_score)):
		if sentence_score[i] >= max_val:
			max_val = sentence_score[i]
			index = i

	#print ("Answer: "+comp_sentences[index]+'\n')
	printanswer(comp_sentences[index],question)

def whichquestype(question,sentences,sentence_score,ne_tagged_sent):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	lower_question = [w.lower() for w in question]
	'''
	index_how = lower_question.index('how')
	if lower_question[index_how+1] in ['big','small','large','far','long','tall','short']:
		for i in xrange(len(sentence_score)):
			for word in sentences[i]:
				if word in measure :
					sentence_score[i] += slam_dunk
					break
	for i in xrange(len(sentence_score)):
		for word,pos in ne_tagged_sent[i]:
			if lower_question[index_how+1] == 'much' or (lower_question[index_how+1] == 'many' and lower_question[index_how+2] in cost):
				if word in cost or (word.isdigit() and any(w in sentences[i] for w in cost)):
					sentence_score[i] += confident
					break
			if (word in ['age','old','years','yrs']) and ('age' in question or 'old' in question):
				sentence_score[i] += confident
				break
			if lower_question[index_how+1] == 'many' and word.isdigit() and (word not in time or word not in cost) and \
				lower_question[index_how+2] in sentences[i]:
				#print word
				#print ne_tagged_sent[i]
				sentence_score[i] += slam_dunk
				break

	'''
	max_val = -1
	index = -1
	
	for i in xrange(len(sentence_score)):
		if sentence_score[i] >= max_val:
			max_val = sentence_score[i]
			index = i

	#print ("Answer: "+comp_sentences[index]+'\n')
	printanswer(comp_sentences[index],question)

def wordmatch(question,sentences):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	lower_question = [word.lower() for word in question if word.lower() not in stopwords]
	#print lower_question
	pos_question = nltk.pos_tag(lower_question)
	lemmatized_sent = dict()
	count = -1

	for sent in sentences:
			count +=1
			lemmatized_sent[count] = [WordNetLemmatizer().lemmatize(w.lower()) for w in sent if w.lower() not in stopwords]

	sentence_score = dict()
	for i in xrange(len(lemmatized_sent)):
		sentence_score[i] = 0

	for word,pos in pos_question:
		for i in xrange(len(lemmatized_sent)):
			if WordNetLemmatizer().lemmatize(word) in lemmatized_sent[i]:
				if 'VB' in pos:
					sentence_score[i] += verb_match
				else:
					sentence_score[i] += other_match

	return sentence_score,comp_sentences

def parsestory(storyfilepath):
	storyfile = open(storyfilepath)
	data = storyfile.read()
	s = data.find('TEXT:\n\n')
	story = data[s+6:]
	sentences = nltk.sent_tokenize(story)
	sentences = [sent.replace('\n',' ') for sent in sentences]
	word_sent = [nltk.word_tokenize(sent) for sent in sentences]
	ne_tagged_sent = list()
	for sent in word_sent:
		ne_tagged_sent.append(nertag.tag(sent))
	#nertag = StanfordNERTagger(path_to_model,path_to_jar)
	#for sent in sentences:
		#namedent = nltk.ne_chunk(nltk.pos_tag(sent))
		#print namedent
		#print sentences
		
		#print nertag.tag(sent)
		#print story
	return sentences,ne_tagged_sent

def parsequestions(questionsfilepath,sentences,ne_tagged_sent):
	questionidstring = 'QuestionID: '
	questionstring = 'Question: '
	questionsfile = open(questionsfilepath)
	for line in questionsfile.readlines():
		line = line.rstrip('\n')
		if questionidstring in line:
			key = line.rstrip('\n')
			print (key)
		if questionstring in line:
			question = line[10:]
			question = nltk.word_tokenize(question)
			#question = [word.lower() for word in question]
			#print pos_question
			#question = [word for word in question if word not in stopwords]
			sentence_score = dict()
			sentence_score,sentences  = wordmatch(question,sentences)
			#print sentence_score
			if 'Where' in question:
				wherequestype(question,sentences,sentence_score,ne_tagged_sent)
			
			elif 'Who' in question:
				whoquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'When' in question:
				whenquestype(question,sentences,sentence_score,ne_tagged_sent)
			
			elif 'What' in question or 'what' in question:
				whatquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'Why' in question:
				whyquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'How' in question or 'how' in question:
				howquestype(question,sentences,sentence_score,ne_tagged_sent)
			
			elif 'Which' in question or 'which' in question:
				whichquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'Whose' in question or 'whose' in question:
				whoquestype(question,sentences,sentence_score,ne_tagged_sent)

			else:
				print 'Answer: '+'\n'
			

def parseinputfiles(lines,path):
	
	#stopwords = nltk.corpus.stopwords.words('english')
	for i in xrange(1,len(lines)):
		storyfilepath = path+lines[i]+'.story'
		questionsfilepath = path+lines[i]+'.questions'
		sentences,ne_tagged_sent = parsestory(storyfilepath)
		#print sentences
		parsequestions(questionsfilepath,sentences,ne_tagged_sent)

if __name__ == '__main__':
		file = open(sys.argv[1])
		lines = [line.rstrip('\n') for line in file]
		file.close()
		path = lines[0]
		parseinputfiles(lines,path)
