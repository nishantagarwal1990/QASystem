import sys
import nltk

def parsequestions(questionsfilepath,sentences,ne_tagged_sent,wherefile,whofile,whenfile,whatfile,whyfile,howfile,whichfile,whosefile,otherfile):
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
			#sentence_score,sentences  = wordmatch(question,sentences)
			#print sentence_score
			if 'Where' in question:
				wherefile.write(line)
				wherefile.write("\n")
				#wherequestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'Who' in question:
				whofile.write(line)
				whofile.write("\n")
				#whoquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'When' in question:
				whenfile.write(line)
				whenfile.write("\n")
				#whenquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'What' in question or 'what' in question:
				whatfile.write(line)
				whatfile.write("\n")
				#whatquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'Why' in question:
				whyfile.write(line)
				whyfile.write("\n")
				#whyquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'How' in question or 'how' in question:
				howfile.write(line)
				howfile.write("\n")
				#howquestype(question,sentences,sentence_score,ne_tagged_sent)

			elif 'Which' in question or 'which' in question:
				whichfile.write(line)
				whichfile.write("\n")

			elif 'Whose' in question or 'whose' in question:
				whosefile.write(line)
				whosefile.write("\n")

			else:
				otherfile.write(line)
				otherfile.write("\n")
				#print 'Answer: '+'\n'


def parseinputfiles(lines,path):
	wherefile = open("where.txt",'w')
	whofile = open("who.txt",'w')
	whenfile = open("when.txt",'w')
	whatfile = open("what.txt",'w')
	whyfile = open("why.txt",'w')
	howfile = open("how.txt",'w')
	whichfile = open("which.txt",'w')
	whosefile = open("whose.txt",'w')
	otherfile = open("other.txt",'w')
	#stopwords = nltk.corpus.stopwords.words('english')
	for i in xrange(1,len(lines)):
		#storyfilepath = path+lines[i]+'.story'
		questionsfilepath = path+lines[i]+'.questions'
		ne_tagged_sent = dict()
		sentences = dict()
		#sentences,ne_tagged_sent = parsestory(storyfilepath)
		#print sentences
		parsequestions(questionsfilepath,sentences,ne_tagged_sent,wherefile,whofile,whenfile,whatfile,whyfile,howfile,whichfile,whosefile,otherfile)
	wherefile.close()
	whofile.close()
	whenfile.close()
	whatfile.close()
	whyfile.close()
	howfile.close()
	whichfile.close()
	whosefile.close()
	otherfile.close()

if __name__ == '__main__':
		file = open(sys.argv[1])
		lines = [line.rstrip('\n') for line in file]
		file.close()
		path = lines[0]
		parseinputfiles(lines,path)