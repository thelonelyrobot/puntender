from nltk.corpus import wordnet as wn
from string import punctuation
import numpy as np

# words to ignore if encountered
stop_words = ["a", "about", "above", "above", "across", "after", "afterwards", "again", "against", "all", "almost", "alone", "along", "already", "also","although","always","am","among", "amongst", "amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone","anything","anyway", "anywhere", "are", "around", "as",  "at", "back","be","became", "because","become","becomes", "becoming", "been", "before", "beforehand", "behind", "being", "below", "beside", "besides", "between", "beyond", "bill", "both", "bottom","but", "by", "call", "cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", "detail", "do", "done", "down", "due", "during", "each", "eg", "eight", "either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone", "everything", "everywhere", "except", "few", "fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", "formerly", "forty", "found", "four", "from", "front", "full", "further", "get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", "inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", "me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", "ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", "rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", "serious", "several", "she", "should", "show", "side", "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", "sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", "that", "the", "their", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", "thickv", "thin", "third", "this", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "top", "toward", "towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", "would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

# determined via running get_associations on the first two senses of "bar"
bar_associations = ['alcoholic', 'bar', 'barroom', 'bought', 'coke', 'counter', 'dog', 'drink',\
 'drinks', 'drowned', 'establishment', 'food', 'ginmill', 'hot', 'obtain', 'room',\
 'saloon', 'served', 'sorrows', 'taproom', 'whiskey']

obscure_word_mapping = {"measle": "measles", "comic_sans": "font", "e-flat": "flat"}

def is_wordnet_word(word):
	return len(wn.synsets(word)) > 0

# given a string, return that string but with punctuation removed
def strip_punctuation(s):
    return ''.join(c for c in s if c not in punctuation)

# return the intersection of two lists
def intersection(a, b):
    return list(set(a) & set(b))

def get_associations(word):
	if not is_wordnet_word(word):
		return []
	word_synsets = wn.synsets(word)
	all_words = []
	for sense in word_synsets:
		definition =  sense.definition()
		definition = strip_punctuation(definition)
		examples = [str(example) for example in sense.examples()]
		example_words = []
		for example in examples:
			example_words += example.split(" ")


		hypernyms = sense.hypernyms()
		hyp_names = [str(hyp.name()).split('.')[0] for hyp in hypernyms]
		lemmas = sense.lemmas()
		lem_names = [str(lem.name()).split('.')[0] for lem in lemmas]
		# print definition
		# print example_words
		# print hyp_names
		# print lem_names
		all_words += str(definition).split(" ") + example_words + hyp_names + lem_names
	all_words = [s.lower() for s in all_words]
	all_words = list(set(all_words))
	all_words.sort()
	all_words = np.setdiff1d(all_words, stop_words)
	return all_words.tolist()

# def has_direct_bar_association(keyword, keyword_associations):
# 	return (keyword in bar_associations) or "bar" in keyword_associations

# def indirect_bar_association(keyword, keyword_associations):
# 	has_association = len(intersection(bar_associations, keyword_associations)) > 0
# 	bar_connection_words = intersection(bar_associations, keyword_associations)
# 	return has_association, bar_connection_words

def has_direct_association(keyword, keyword_associations, keyword2, keyword2_associations):
	return (keyword in keyword2_associations) or keyword2 in keyword_associations

def indirect_association(keyword, keyword_associations, keyword2, keyword2_associations):
	has_association = len(intersection(keyword_associations, keyword2_associations)) > 0
	connection_words = "' and '".join(intersection(keyword_associations, keyword2_associations))
	return has_association, connection_words

def determine_connection(keyword, keyword_associations, keyword2, keyword2_associations):
	if has_direct_association(keyword, keyword_associations, keyword2, keyword2_associations):
		print ("'" + keyword + "' is directly connected to the meaning of '" + keyword2 + "'.")
		return True
	elif indirect_association(keyword, keyword_associations, keyword2, keyword2_associations)[0]:
		print ("'" + keyword + "' is connected to the meaning of '" + keyword2 + "' via '" + \
			indirect_association(keyword, keyword_associations, keyword2, keyword2_associations)[1] + "'.")
		return True
	else:
		print ("No Wordnet connection between '" + keyword + "' and '" + keyword2 + "' could be found.")
		return False


def determine_keyword(statement_keywords, customer, customer_associations):
	if len(statement_keywords) == 1:
		return statement_keywords[0]
	else:
		keyword_points = {}
		for keyword in statement_keywords:
			keyword_points[keyword] = 0
			keyword_associations = get_associations(keyword)
			if has_direct_association(keyword, keyword_associations, "bar", bar_associations):
				keyword_points[keyword] += 3
			elif indirect_association(keyword, keyword_associations, "bar", bar_associations)[0]:
				keyword_points[keyword] += 2
			if has_direct_association(keyword, keyword_associations, customer, customer_associations):
				keyword_points[keyword] += 4
			elif indirect_association(keyword, keyword_associations, customer, customer_associations)[0]:
				keyword_points[keyword] += 3
		return max(keyword_points, key=keyword_points.get)


with open('jokes.txt', 'r', encoding='UTF8') as jokes:
	for joke in jokes:
		print("")
		print(joke.strip())
		is_understandible = True
		joke = joke.lower().rstrip()

		customer = joke.split(" walk")[0].strip()
		articles = ["a", "an", "the", "another"]
		if customer.split(" ", 1)[0] in articles:
			customer = customer.split(" ", 1)[1]
		customer = customer.replace(" ", "_")
		if (not is_wordnet_word(customer)) and customer in obscure_word_mapping:
			print ("Treating '" + customer + "' as '" + obscure_word_mapping[customer] + "'...")
			customer = obscure_word_mapping[customer]
		customer_associations = get_associations(customer)

		statement = strip_punctuation(joke.split("s, \"")[1])
		statement_keywords = np.setdiff1d(statement.split(" "), stop_words)
		if len(statement_keywords) == 0:
			print ("Could not determine any word that had a pun being made on it.")
			continue

		keyword = determine_keyword(statement_keywords, customer, customer_associations)
		keyword_associations = get_associations(keyword)

		has_customer_connection = determine_connection(keyword, keyword_associations, customer, customer_associations)
		has_bar_connection = determine_connection(keyword, keyword_associations, "bar", bar_associations)

		if has_customer_connection and has_bar_connection:
			print ("The joke is funny because it makes a pun on the word '" + keyword + "'.")
		elif has_customer_connection or has_bar_connection:
			print ("The joke is probably funny because it makes a pun on the word '" + keyword + "'. However, it's uncertain.")
		else:
			print ("The joke might be funny because it makes a pun on the word '" + keyword + "'. However, no puns were found.")

		# has_bar_connection = False
		# bar_connection = ""
		
		# # check bar relation 
		# if (keyword in bar_associations) or "bar" in keyword_associations:
		# 	has_bar_connection = True
		# 	bar_connection = "directly connected to the meaning of 'bar'."
		# elif len(intersection(bar_associations, keyword_associations)) > 0:
		# 	has_bar_connection = True
		# 	bar_connection_words = intersection(bar_associations, keyword_associations)
		# 	bar_connection = "connected to the meaning of 'bar' via '" + bar_connection_words[0] + "'."



		# has_customer_connection = False
		# # customer_connection = ""
		# if is_wordnet_word(customer):
		# 	cust_associations = get_associations(customer)	
		# 	#check customer relation
		# 	if (keyword in cust_associations) or customer in keyword_associations:
		# 		has_customer_connection = True
		# 		print ("'" + keyword + "' is directly connected to the meaning of '" + customer + "'."
		# 	elif len(intersection(cust_associations, keyword_associations)) > 0:
		# 		has_customer_connection = True
		# 		customer_connection_words = intersection(cust_associations, keyword_associations)
		# 		print ("'" + keyword + "' is connected to the meaning of '" + customer + "' via '" + customer_connection_words[0] + "'."
		# 	else:
		# 		("No Wordnet connection between '" + keyword + "' and '" + customer "' could be found.")
		# else:
		# 	print ("Wordnet cannot doesn't have the word, '" + customer + "' listed in its database, so no pun connection could be found.")

		
		# print ("'" + keyword + "' is " + bar_connection)
		




		# print intersection(bar_associations, keyword_associations)
		# print intersection(cust_associations, keyword_associations)





