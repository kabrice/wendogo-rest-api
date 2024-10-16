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
from sklearn.metrics.pairwise import cosine_similarity

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


    @staticmethod 
    @lru_cache(maxsize=None)
    def f_remove_accents(text):
        """
        Removes accents from text using Unicode normalization.
        """
        return ''.join(
            char for char in unicodedata.normalize('NFD', text.lower())
            if unicodedata.category(char) != 'Mn'
        )

    @staticmethod 
    def custom_tokenizer(text):
        """
        Custom tokenizer that removes punctuation, accents, stop words,
        and applies stemming.
        """
        # Remove accents and punctuation, split words by whitespace
        text = Helper.f_remove_accents(text).translate(remove_punctuation_map)
        tokens = re.split(r'\W+', text)

        # Filter stop words and apply stemming
        return [stemmer.stem(token) for token in tokens if token and token not in stop_words]

    # Preinitialize TfidfVectorizer for reuse
    vectorizer = TfidfVectorizer(
        tokenizer=custom_tokenizer,
        lowercase=True,  # Lowercase handled by `f_remove_accents`
        ngram_range=(1, 1)
    )

    @staticmethod 
    def cosine_sim(text1, text2):
        """
        Computes the cosine similarity between two texts using preinitialized TfidfVectorizer.
        """
        # Transform texts into TF-IDF vectors
        tfidf_matrix = Helper.vectorizer.fit_transform([text1, text2])
        
        # Compute cosine similarity directly using sklearn's optimized function
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
     
#     def tryMe(self):               
#         text1 ="Droit"
#         text2="Droit privé"
#         print("la similarité est :", self.cosine_sim(text1, text2))

# if __name__ == "__main__":
#     helper = Helper()
#     helper.tryMe()

