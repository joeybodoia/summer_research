'''
'''

from chajda.tsvector import lemmatize, Config
from chajda.tsquery.__init__ import to_tsquery


def augments_gensim(lang, word, config=Config(), n=5):
    '''
    Returns n words that are "similar" to the input word in the target language.
    These words can be used to augment a search with the Query class.

    >>> to_tsquery('en', 'baby boy', augment_with=augments_gensim)
    '(baby:A | boy:B | girl:B | newborn:B | pregnant:B | mom:B) & (boy:A | girl:B | woman:B | man:B | kid:B | mother:B)'

    >>> to_tsquery('en', '"baby boy"', augment_with=augments_gensim)
    'baby:A <1> boy:A'

    >>> to_tsquery('en', '"baby boy" (school | home) !weapon', augment_with=augments_gensim)
    '(baby:A <1> boy:A) & ((school:A | college:B | campus:B | graduate:B | elementary:B | student:B) | (home:A | leave:B | rest:B | come:B)) & !(weapon:A | explosive:B | weaponry:B | gun:B | ammunition:B | device:B)'

    >>> augments_gensim('en','baby', n=5)
    ['boy', 'girl', 'newborn', 'pregnant', 'mom']

    >>> augments_gensim('en','school', n=5)
    ['college', 'campus', 'graduate', 'elementary', 'student']

    >>> augments_gensim('en','weapon', n=5)
    ['explosive', 'weaponry', 'gun', 'ammunition', 'device']
    '''

    # find the most similar words;
    try:
        topn = augments_gensim.model.most_similar(word, topn=n+1)
        print('gensim topn = ', topn)
        words = ' '.join([ word for (word,rank) in topn ])
        print('gensim words bf lemma = ', words)

    # gensim raises a KeyError when the input word is not in the vocabulary;
    # we return an empty list to indicate that there are no similar words
    except KeyError:
        return []

    # lemmatize the results so that they'll be in the search document's vocabulary
    words = lemmatize(lang, words, add_positions=False, config=config).split()
    words = list(filter(lambda w: len(w)>1 and w != word, words))[:n]

    return words


# load the model if it's not already loaded
try:
    augments_gensim.model
except AttributeError:
    import gensim.downloader
    augments_gensim.model = gensim.downloader.load("glove-wiki-gigaword-50")

#print('tsquery gensim = ', to_tsquery('en', 'baby boy', augment_with=augments_gensim))


import fasttext
import fasttext.util


def augments_fasttext(lang, word, config=Config(), n=5):
    #load the model based on lang if it's not already loaded
    try:
        augments_fasttext.model
    except AttributeError:
        fasttext.util.download_model(lang, if_exists='ignore')
        augments_fasttext.model = fasttext.load_model('cc.{0}.300.bin'.format(lang))

   # print('fasttext dimension =', augments_fasttext.model.get_dimension())

    print('fasttext similar words =', augments_fasttext.model.get_nearest_neighbors(word, k=40))
    
    #find the most similar words
    try:
        topn = augments_fasttext.model.get_nearest_neighbors(word, k=40)
       # print('fasttext topn = ', topn)
        words = ' '.join([ word for (rank, word) in topn ])
       # print('fasttext words bf lemma = ', words)
    except KeyError:
        return []

    # lemmatize the results so that they'll be in the search document's vocabulary
    words = lemmatize(lang, words, add_positions=False, config=config).split()

    #todo: figure out a better way to filter through the typo words that fasttext produces:
    words = list(filter(lambda w: len(w)>1 and w != word, words))[:n]

    
   # print('returned fasttext words = ', words)
    return words


#print('tsquery fasttext = ', to_tsquery('en', 'baby boy', augment_with=augments_fasttext))
