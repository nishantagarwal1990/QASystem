import sys
import os
import nltk
jar_folder = "/Users/nishantagarwal/stanford-ner-2015-04-20/stanford-ner.jar"
os.environ['CLASSPATH']=jar_folder
import re

from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet	import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.tag import StanfordNERTagger

path_to_jar = "/Users/nishantagarwal/stanford-ner-2015-04-20/stanford-ner.jar"
path_to_model = "/Users/nishantagarwal/stanford-ner-2015-04-20/classifiers/english.muc.7class.distsim.crf.ser.gz"
stopwords = ['is','a','an','the','are']
def parsestory(storyfilepath):
	storyfile = open(storyfilepath)
	data = storyfile.read()
	s = data.find('TEXT:\n\n')
	story = data[s+6:]
	sentences = nltk.sent_tokenize(story)
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

def wherequestype(question,sentences):
	pos_question = nltk.pos_tag(question)
	qetag = StanfordNERTagger(path_to_model,path_to_jar)
	st_tag_ques = qetag.tag(question)
	#print st_tag_ques
	search = ''
	count = 0
	for word,pos in pos_question:
		if pos == 'NN' and st_tag_ques[count][1] != 'PERSON':
			search = word
			break
		if pos == 'NNP' and st_tag_ques[count][1] != 'PERSON':
			search = ' '.join([pos_question[i][0] for i in xrange(count,len(pos_question)) if pos_question[i][1] == 'NNP'])
			break
		count = count + 1
	#print search
	count = -1
	for sent in sentences:
		found = sent.lower().find(search.lower())
		count = count+1
		if found != -1:
			break
	#print count
	nertag = StanfordNERTagger(path_to_model,path_to_jar)
	answer = ''
	if count >=0 and count <= len(sentences):
		found = 0
		for i in reversed(range(max(0,count-2),count+1)):
			word_tok_sent = nltk.word_tokenize(sentences[i])
			tagged_sent = nertag.tag(word_tok_sent)
			#print tagged_sent
			if not found:
				count1 = 0
				for word,tag in tagged_sent:
					if tag == 'LOCATION':
						#print "here"
						found = 1
						answer = ' '.join([tagged_sent[j][0] for j in xrange(count1,len(tagged_sent)) if tagged_sent[j][1] == 'LOCATION' \
										or (tagged_sent[j][0] == ',' and tagged_sent[j+1][1] == 'LOCATION')])
						break
					count1 = count1 + 1
			else:
				break

		if not found :
			count1 = 0
			for i in xrange(count+1,min(count+3,len(sentences)-1)):
					word_tok_sent = nltk.word_tokenize(sentences[i])
					tagged_sent = nertag.tag(word_tok_sent)
					#print tagged_sent
					if not found:
						for word,tag in tagged_sent:
							if tag == 'LOCATION':
								found = 1
								answer = ' '.join([tagged_sent[j][0] for j in xrange(count1,len(tagged_sent)) if tagged_sent[j][1] == 'LOCATION' \
											or (tagged_sent[j][0] == ',' and tagged_sent[j+1][1] == 'LOCATION')])
								break
							count1 = count1 + 1
					else:
						break
		print "Answer:"+answer+'\n'

def whoquestype(question,sentences):
	pos_question = nltk.pos_tag(question)
	qetag = StanfordNERTagger(path_to_model,path_to_jar)
	st_tag_ques = qetag.tag(question)
	search_noun = ''
	search_verb = ''
	count = 0
	stemmer = SnowballStemmer('english')
	for word,pos in pos_question:
		if 'VB' in pos:
			search_verb = word
		if pos == 'NN' and st_tag_ques[count][1] != 'PERSON':
			search_noun = word
			break
		if pos == 'NNP' and st_tag_ques[count][1] != 'PERSON':
			search_noun = ' '.join([pos_question[i][0] for i in xrange(count,len(pos_question)) if pos_question[i][1] == 'NNP'])
			break
		count = count + 1
	#print search_verb
	#print search_noun
	
	if search_verb:
		count = -1
		found_verb = 0
		found_noun = -1
		synlist = list()
		syn = wn.synsets(search_verb)
		for s in syn:
			synlist = synlist + [name for name in s.lemma_names() if name not in synlist]
		#print synlist
		for sent in sentences:
			word_token = nltk.word_tokenize(sent) 
			pos_sent = nltk.pos_tag(word_token)
			#print pos_sent
			if not found_verb:
				count = count+1
				for word_sent,tag_sent in pos_sent:
					if 'VB' in tag_sent:
						stemmed = WordNetLemmatizer().lemmatize(word_sent,'v')
						#print stemmed
						if stemmed in synlist:
							found_noun = sent.find(search_noun)
							if found_noun != -1:
								found_verb = 1
								break
			else:
				break
		#print "verb count"+str(count)
	else:
		count = -1
		for sent in sentences:
			found = sent.lower().find(search_noun.lower())
			count = count+1
			if found != -1:
				break
		#print "noun count"+str(count)
	nertag = StanfordNERTagger(path_to_model,path_to_jar)
	answer = ''
	if count >=0 and count <= len(sentences):
		found = 0
		for i in reversed(range(max(0,count-2),count+1)):
			word_tok_sent = nltk.word_tokenize(sentences[i])
			tagged_sent = nertag.tag(word_tok_sent)
			#print tagged_sent
			if not found:
				count1 = 0
				for word,tag in tagged_sent:
					if tag == 'PERSON' or tag == 'ORGANIZATION' :
						#print "here"
						found = 1
						answer = ' '.join([tagged_sent[j][0] for j in xrange(count1,len(tagged_sent)) if tagged_sent[j][1] == 'PERSON' \
										or tagged_sent[j][1] == 'ORGANIZATION' ])
						break
				count1 = count1 + 1
			else:
				break

		if not found:
			#print "here"
			count1 = 0
			word_tok_sent = nltk.word_tokenize(sentences[count])
			pos_tag_sent = nltk.pos_tag(sentences[count])
			for word,tag in pos_tag_sent:
				if WordNetLemmatizer().lemmatize(word,'v') == stemmed:
					print "here"
					found = 1
					answer = ' '.join([pos_tag_sent[j][0] for j in xrange(count1,len(pos_tag_sent)) if (pos_tag_sent[j][1] == 'DT' \
										and pos_tag_sent[j+1][1] == 'JJ' and pos_tag[j+2][1] == 'NN') or (pos_tag_sent[j][1] == 'JJ' \
										and pos_tag[j+1][1] == 'NN') or (pos_tag_sent[j][1] == 'NN' \
										and pos_tag_sent[j+1][1] == 'CC' and pos_tag[j+2][1] == 'NN') or (pos_tag_sent[j][1] == 'CC' \
										and pos_tag[j+1][1] == 'NN') or pos_tag_sent[j][1] == 'NN'])
					break
				count1 = count1 + 1

		if not found :
			count1 = 0
			for i in xrange(count+1,min(count+3,len(sentences)-1)):
					word_tok_sent = nltk.word_tokenize(sentences[i])
					tagged_sent = nertag.tag(word_tok_sent)
					#print tagged_sent
					if not found:
						for word,tag in tagged_sent:
							if tag == 'PERSON' or tag == 'ORGANIZATION':
								found = 1
								answer = ' '.join([tagged_sent[j][0] for j in xrange(count1,len(tagged_sent)) if tagged_sent[j][1] == 'PERSON' \
											or tagged_sent[j][1] == 'ORGANIZATION'])
								break
							count1 = count1 + 1
					else:
						break
		
		print "Answer:"+answer+'\n'

def whenquestiontype(question,sentences):
	pos_question = nltk.pos_tag(question)
	qetag = StanfordNERTagger(path_to_model,path_to_jar)
	st_tag_ques = qetag.tag(question)
	#print st_tag_ques
	search = ''
	search_verb = ''
	count = 0
	for word,pos in pos_question:
		if not search:
			if pos == 'NN' :
				search = word
			if pos == 'NNP':
				search = ' '.join([pos_question[i][0] for i in xrange(count,len(pos_question)) if pos_question[i][1] == 'NNP'])
		if not search_verb:
			if 'VB' in pos:
				search_verb = word
		count = count + 1
	#print search
	count = -1
	for sent in sentences:
		found = sent.lower().find(search.lower())
		count = count+1
		if found != -1:
			break
	#print count
	nertag = StanfordNERTagger(path_to_model,path_to_jar)
	answer = ''
	if count >=0 and count <= len(sentences):
		found = 0
		for i in reversed(range(max(0,count-2),count+1)):
			word_tok_sent = nltk.word_tokenize(sentences[i])
			tagged_sent = nertag.tag(word_tok_sent)
			#print tagged_sent
			if not found:
				count1 = 0
				for word,tag in tagged_sent:
					if tag == 'LOCATION':
						#print "here"
						found = 1
						answer = ' '.join([tagged_sent[j][0] for j in xrange(count1,len(tagged_sent)) if tagged_sent[j][1] == 'LOCATION' \
										or (tagged_sent[j][0] == ',' and tagged_sent[j+1][1] == 'LOCATION')])
						break
					count1 = count1 + 1
			else:
				break

		if not found :
			count1 = 0
			for i in xrange(count+1,min(count+3,len(sentences)-1)):
					word_tok_sent = nltk.word_tokenize(sentences[i])
					tagged_sent = nertag.tag(word_tok_sent)
					#print tagged_sent
					if not found:
						for word,tag in tagged_sent:
							if tag == 'LOCATION':
								found = 1
								answer = ' '.join([tagged_sent[j][0] for j in xrange(count1,len(tagged_sent)) if tagged_sent[j][1] == 'LOCATION' \
											or (tagged_sent[j][0] == ',' and tagged_sent[j+1][1] == 'LOCATION')])
								break
							count1 = count1 + 1
					else:
						break
		print "Answer:"+answer+'\n'

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
			question = [word for word in question if word not in stopwords]
			#print question
			if 'Where' in question:
				wherequestype(question,sentences)

			if 'Who' in question:
				whoquestype(question,sentences)

			#if 'When' in question:
				#whenquestype(question,sentences)
			

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