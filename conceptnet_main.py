import requests as r
import re
import time

punctuation = '!?.(),'

from nltk.corpus import stopwords

CONCEPTNET_URL = 'http://api.conceptnet.io/related/c/en/{}?filter=/c/en/{}'

CONTEXT_WORDS = {
	"bar": ["bar", "drink", "alcohol", "bartender"],
}

REGEX = {
	"bar": re.compile('^(.+) (walks|walk) into a bar. The (barman|bartender) (says|asks|shouts), "(.+)"$'),
}

# Minimum relationship before we consider that significant
CUTOFF_WEIGHT = 0.02

def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)

def match_jokes(joketype, joke):
	subject, _, _, _, quote = REGEX[joketype].match(joke).groups()
	return subject, quote

def edge_weight(word1, word2):
	word1 = word1.lower().replace(' ', '_')
	word2 = word2.lower().replace(' ', '_')

	weight = 0.

	url = CONCEPTNET_URL.format(word1, word2)
	obj = r.get(url).json()
	time.sleep(1.001)
	
	related = obj.get('related')
	if related:
		weight = related[0].get('weight')

	url = CONCEPTNET_URL.format(word2, word1)
	obj = r.get(url).json()
	time.sleep(1.001)
	
	related = obj.get('related')
	if related:
		if weight != 0.:
			weight = (weight + related[0].get('weight')) / 2.
		else:
			weight = related[0].get('weight')

	return weight

def get_weights(list1, list2):
	sorted_weights = []
	for word1 in list1:
		for word2 in list2:
			sorted_weights.append( (edge_weight(word1, word2), (word1, word2,), ) )
	sorted_weights.sort()
	avg_weight = sum([x for x, _ in sorted_weights]) / len(sorted_weights)
	return sorted_weights, avg_weight

def softmax(x, y, z):
	import math
	sumexp = math.exp(x) + math.exp(y) + math.exp(z)
	return math.exp(x) / sumexp, math.exp(y) / sumexp, math.exp(z) / sumexp


STOPWORDS = list(stopwords.words('english'))

def tokenize(sentence):
	sentence = strip_punctuation(sentence)
	
	st = sentence.split(' ')
	newst = []
	for word in st:
		if word.lower() not in STOPWORDS:
			newst.append(word.lower())
		else:
			pass
	newst = [strip_punctuation(w.lstrip().rstrip()) for w in newst if (w and (w != ' '))]
	return newst


if __name__ == '__main__':
	with open('jokes.txt', 'r', encoding='UTF8') as jokes:
		for joke in jokes:
			print (joke)

			try:
				subject, quote = match_jokes('bar', joke)
				print (subject, quote)
				print (tokenize(subject), tokenize(quote))

				subject_set, quote_set = tokenize(subject), tokenize(quote)

				subject_set_weights, _1 = get_weights(subject_set, CONTEXT_WORDS["bar"])
				quote_set_weights, _2 = get_weights(quote_set, CONTEXT_WORDS["bar"])
				interset_weights, _3 = get_weights(subject_set, quote_set)

				# print(subject_set_weights, quote_set_weights, interset_weights)
				print(_1, _2, _3)

				x, y, z = softmax(_1, _2, _3)
				print ("There is a pun involving: ")
				if _1> CUTOFF_WEIGHT:
					m, n = subject_set_weights[-1][1]
					print('{} and {}'.format(m, n))
				if _2 > CUTOFF_WEIGHT:
					m, n = quote_set_weights[-1][1]
					print('{} and {}'.format(m, n))
				if _3 > CUTOFF_WEIGHT:
					m, n = interset_weights[-1][1]
					print('{} and {}'.format(m, n))

			except:
				print ("Failed to analyze joke!")
			
