from nltk.tokenize import  word_tokenize
from nltk.corpus import stopwords
from autocorrect import Speller
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
    

stop_words = set(stopwords.words('english'))
spell = Speller(lang='en')
ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()


def w_tok(EXAMPLE_TEXT):
    tok_ex = word_tokenize(EXAMPLE_TEXT)

    filtered_sentence = []
    for w in tok_ex:
        if w not in stop_words:
            filtered_sentence.append(w)
    filtered_sentence = set(filtered_sentence)

    cor_spell = []
    for w in filtered_sentence:
        cor_spell.append( spell(w) )

    stem_words = []
    for w in cor_spell:
        stem_words.append(ps.stem(w))

    lem_words = []
    for w in stem_words:
        lem_words.append(lemmatizer.lemmatize(w))

    return lem_words

    
# def syn_word(words):
#     t_words = []
#     for w in words:
#         synonyms = []
#         for syn in wordnet.synsets(w):
#             for l in syn.lemmas():
#                 synonyms.append(l.name())
#         v = set(synonyms)
#         t_words.append(v)
#     print(t_words)
#     return t_words