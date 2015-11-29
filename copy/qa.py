import sys
import os
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
path_to_model = "/Users/nishantagarwal/stanford-ner-2015-04-20/classifiers/english.muc.7class.distsim.crf.ser.gz"
stopwords = ['is','a','an','the','are','who','when','where','what','why','who','in','at','on','by','can', 'could', 'may', \
				'might', 'must', 'ought to', 'shall', 'should', 'will', 'would','am','was','were','does','do','did','has','have','had'\
				,'to','of','we','i','he','she','me','they','that','each','him','his','hers','ours','her','you',\
				'nearby','above','below','over','under','up','down','around','himself','herself','themselves','someone','as','such',\
				'anything','everything','any']
location_prep = ['in','at','near','inside','on','by','nearby','above','below','over','under','up','down','around',\
					'through','outside','between','beside','beyond','behind','within','underneath','among','along','against']

months = ['january','february','march','april','may','june','july','august','september','october','november','december']
measure = ['sq','square','feet','ft','sq-ft','inches','cms','centimeters','yard','km','meter','m','mm','millimeter','long']
cost = ['$','dollars','cost','price']
nertag = StanfordNERTagger(path_to_model,path_to_jar)
verb_match = 6
other_match = 3
clue = 3
good_clue = 4
confident = 6
slam_dunk = 20

def wherequestype(question,sentences,sentence_score):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	for i in xrange(len(sentence_score)):
		ne_tagged_sent = nertag.tag(sentences[i])
		for word in sentences[i]:
			if word in location_prep:
				sentence_score[i] += good_clue
		for word,pos in ne_tagged_sent:
			if pos == 'LOCATION':
				sentence_score[i] += confident

	max_val = -1
	index = -1

	for i in xrange(len(sentence_score)):
		if sentence_score[i] > max_val:
			max_val = sentence_score[i]
			index = i

	ne_tagged_sent = nertag.tag(sentences[index])
	#print ne_tagged_sent
	#print sentence_score
	answer = ''
	answer = ' '.join([ne_tagged_sent[j][0] for j in xrange(len(ne_tagged_sent)) if ne_tagged_sent[j][1] == 'LOCATION' \
										or (ne_tagged_sent[j][0] == ',' and ne_tagged_sent[j+1][1] == 'LOCATION')])

	print "Answer: "+comp_sentences[index]+'\n'

def whoquestype(question,sentences,sentence_score):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	ne_tagged_ques = nertag.tag(question)
	for i in xrange(len(sentence_score)):
		found_q = 0
		found_sent = 0
		found_name = 0
		ne_tagged_sent = nertag.tag(sentences[i])
		for word in sentences[i]:
			if word.lower() == 'name':
				found_name = 1
				break
		for word,pos in ne_tagged_sent:
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

	ne_tagged_sent = nertag.tag(sentences[index])
	#print ne_tagged_sent
	#print sentence_score
	answer = ''
	answer = ' '.join([ne_tagged_sent[j][0] for j in xrange(len(ne_tagged_sent)) if ne_tagged_sent[j][1] == 'PERSON'\
				or ne_tagged_sent[j][1] == 'ORGANIZATION'])

	print "Answer: "+comp_sentences[index]+'\n'

def whenquestype(question,sentences,sentence_score):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	score = dict()
	for i in xrange(len(sentence_score)):
		score[i] = 0
	for i in xrange(len(sentence_score)):
		ne_tagged_sent = nertag.tag(sentences[i])
		for word,pos in ne_tagged_sent:
			if pos == 'DATE' or word in months:
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

	ne_tagged_sent = nertag.tag(sentences[index])
	#print ne_tagged_sent
	#print sentence_score
	answer = ''
	answer = ' '.join([ne_tagged_sent[j][0] for j in xrange(len(ne_tagged_sent)) if ne_tagged_sent[j][1] == 'DATE'\
				or ne_tagged_sent[j][1] in months])

	print "Answer: "+comp_sentences[index]+'\n'

def whatquestype(question,sentences,sentence_score):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	pos_ques = nltk.pos_tag(question)
	for i in xrange(len(sentence_score)):
		ne_tagged_sent = nertag.tag(sentences[i])
		for word in question:
			if word.lower() in months and ('today' in sentences[i] or 'yesterday' in sentences[i] or 'tomorrow' in sentences[i]\
				or ('last' in sentences[i] and 'night' in sentences[i])):
				sentence_score[i] +=clue
		if 'kind' in question and ('call' in sentences[i] or 'from' in sentences[i]):
			sentence_score[i] += good_clue
		
		if 'name' in question and ('name' in sentences[i] or 'call' in sentences[i] or 'known' in sentences[i]):
			sentence_score[i] += slam_dunk

		if ('name' in question and ('of' in question or 'for' in question)):
			if 'of' in question:
				index = question.index('of')
				search = [pos_ques[j][0] for j in xrange(index,len(pos_ques)) if pos_ques[j][1] == 'NN' or pos_ques[j][1] == 'NNP']
			else:
				index = question.index('for')
				search = [pos_ques[j][0] for j in xrange(index,len(pos_ques)) if pos_ques[j][1] == 'NN' or pos_ques[j][1] == 'NNP']
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

	ne_tagged_sent = nertag.tag(sentences[index])
	#print ne_tagged_sent
	#print sentence_score
	answer = ''
	answer = ' '.join([ne_tagged_sent[j][0] for j in xrange(len(ne_tagged_sent)) if ne_tagged_sent[j][1] == 'LOCATION' \
										or (ne_tagged_sent[j][0] == ',' and ne_tagged_sent[j+1][1] == 'LOCATION')])

	print "Answer: "+comp_sentences[index]+'\n'

def whyquestype(question,sentences,sentence_score):
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
		ne_tagged_sent = nertag.tag(sentences[i])
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

	ne_tagged_sent = nertag.tag(sentences[index])
	#print ne_tagged_sent
	#print sentence_score
	answer = ''
	answer = ' '.join([ne_tagged_sent[j][0] for j in xrange(len(ne_tagged_sent)) if ne_tagged_sent[j][1] == 'LOCATION' \
										or (ne_tagged_sent[j][0] == ',' and ne_tagged_sent[j+1][1] == 'LOCATION')])

	print "Answer: "+comp_sentences[index]+'\n'

def howquestype(question,sentences,sentence_score):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	lower_question = [w.lower() for w in question]
	index_how = lower_question.index('how')
	if lower_question[index_how+1] in ['big','small','large','far','long','tall','short','many']:
		for i in xrange(len(sentence_score)):
			for word in sentences[i]:
				if word in measure :
					sentence_score[i] += slam_dunk
	for i in xrange(len(sentence_score)):
		ne_tagged_sent = nertag.tag(sentences[i])
		for word,pos in ne_tagged_sent:
			if pos == 'MONEY' and lower_question[index_how+1] == 'much':
				sentence_score[i] += confident
			if (pos == 'DATE' or pos == 'TIME') and (word in ['age','old','years','yrs']) and ('age' in question or 'old' in question):
				sentence_score[i] += confident

	max_val = -1
	index = -1

	for i in xrange(len(sentence_score)):
		if sentence_score[i] >= max_val:
			max_val = sentence_score[i]
			index = i

	print "Answer: "+comp_sentences[index]+'\n'

def wordmatch(question,sentences):
	comp_sentences = sentences
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	lower_question = [word.lower() for word in question if word.lower() not in stopwords]
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
	#sentences = [nltk.word_tokenize(sent) for sent in sentences]
	#sentences = [nltk.pos_tag(sent) for sent in sentences]
	#nertag = StanfordNERTagger(path_to_model,path_to_jar)
	#for sent in sentences:
		#namedent = nltk.ne_chunk(nltk.pos_tag(sent))
		#print namedent
		#print sentences
		
		#print nertag.tag(sent)
		#print story
	return sentences

def parsequestions(questionsfilepath,sentences):
	questionidstring = 'QuestionID: '
	questionstring = 'Question: '
	questionsfile = open(questionsfilepath)
	for line in questionsfile.readlines():
		if questionidstring in line:
			key = line.rstrip('\n')
			print key
		if questionstring in line:
			question = line[10:]
			question = nltk.word_tokenize(question)
			#question = [word.lower() for word in question]
			#print pos_question
			#question = [word for word in question if word not in stopwords]
			sentence_score = dict()
			sentence_score,sentences  = wordmatch(question,sentences)
			#print sentence_score
			if 'Where' in question or 'where' in question:
				wherequestype(question,sentences,sentence_score)

			if 'Who' in question or 'who' in question:
				whoquestype(question,sentences,sentence_score)

			if 'When' in question or 'when' in question:
				whenquestype(question,sentences,sentence_score)

			if 'What' in question or 'what' in question:
				whatquestype(question,sentences,sentence_score)

			if 'Why' in question or 'why' in question:
				whyquestype(question,sentences,sentence_score)

			if 'How' in question or 'how' in question:
				howquestype(question,sentences,sentence_score)

def parseinputfiles(lines,path):
	
	#stopwords = nltk.corpus.stopwords.words('english')
	for i in xrange(1,len(lines)):
		storyfilepath = path+lines[i]+'.story'
		questionsfilepath = path+lines[i]+'.questions'
		sentences = parsestory(storyfilepath)
		#print sentences
		parsequestions(questionsfilepath,sentences)

if __name__ == '__main__':
		file = open(sys.argv[1])
		lines = [line.rstrip('\n') for line in file]
		file.close()
		path = lines[0]
		parseinputfiles(lines,path)