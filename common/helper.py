import os
from twilio.rest import Client
from flask import  jsonify
import sys
import re

"""For similarity between two texts"""
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from stop_words import get_stop_words
import unicodedata 
from functools import lru_cache

nltk.download('punkt')
stemmer = nltk.stem.porter.PorterStemmer()

# Load French stop words once
stop_words = get_stop_words('fr')

# Precompute punctuation removal translation map
remove_punctuation_map = str.maketrans('', '', string.punctuation)
class Helper:
    @staticmethod
    def send_whatsapp_verification_code(phone):
        client = Client()
        verification = client.verify.v2.services(
            os.environ['TWILIO_VERIFY_SERVICE']).verifications.create(
                to=phone, channel='whatsapp')
        if verification.status != 'pending':
            return True
        return False
        
    @staticmethod
    def check_whatsapp_verification_code(phone, code):
    
        try:
            client = Client()
            verification_check = client.verify.v2.services(
                os.environ['TWILIO_VERIFY_SERVICE']).verification_checks.create(
                    to=phone, code=code
                )
            if verification_check.status != 'pending':
                return True
            return False
        except Exception as e:
            print('error'+ e)
            return False
    
    @staticmethod    
    def logError(e, db, Log, request):
        error = 'Message : {} - Error on line {} - Type :{}'.format(str(e), sys.exc_info()[-1].tb_lineno, type(e).__name__)
        print('****** 🛑 ERROR ****** '+error)
        new_log = Log(request_input= str(request.get_json())[:255], message=str(error)[:2500])
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"errorId": new_log.id, "success": False})         


    # Optimized function to remove accents using unicodedata
    @staticmethod 
    @lru_cache(maxsize=None)
    def f_remove_accents(text):
        """
        Removes accents from the text using Unicode normalization.
        """
        return ''.join(
            char for char in unicodedata.normalize('NFD', text.lower())
            if unicodedata.category(char) != 'Mn'
        )

    # Optimized tokenization, stemming, and normalization with caching
    @staticmethod 
    @lru_cache(maxsize=1000)
    def stem_tokens(tokens):
        return [stemmer.stem(token) for token in tokens]

    def normalize(text):
        text = Helper.f_remove_accents(text)
        tokens = nltk.word_tokenize(text.translate(remove_punctuation_map))
        return Helper.stem_tokens(tuple(tokens))  # Use tuple to allow caching with lru_cache

    # Preinitialize the TfidfVectorizer once and reuse it
    vectorizer = TfidfVectorizer(
        tokenizer=normalize,
        stop_words=stop_words,
        ngram_range=(1, 1)
    )

    @staticmethod 
    def cosine_sim(text1, text2):
        """
        Computes the cosine similarity between two texts.
        """
        # Remove accents and prepare texts
        text1 = Helper.f_remove_accents(text1)
        text2 = Helper.f_remove_accents(text2)
        
        # Fit the TF-IDF on the two texts
        tfidf = Helper.vectorizer.fit_transform([text1, text2])
        
        # Return cosine similarity
        return (tfidf * tfidf.T).A[0, 1]
     
#     def tryMe(self):               
#         text1 ="Droit"
#         text2="Droit privé"
#         print("la similarité est :", self.cosine_sim(text1, text2))

# if __name__ == "__main__":
#     helper = Helper()
#     helper.tryMe()

