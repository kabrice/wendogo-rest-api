import os
from twilio.rest import Client
from flask import  jsonify
import sys
import re

"""For similarity between two texts"""
import nltk
nltk. download( 'punkt')
import string
from sklearn. feature_extraction. text import TfidfVectorizer
stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
from stop_words import get_stop_words
stop_words = get_stop_words('fr')
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
     def f_remove_accents(old):
        """
        Removes common accent characters, lower form.
        Uses: regex.
        """
        new = old.lower()
        new = re.sub(r'[àáâãäå]', 'a', new)
        new = re.sub(r'[èéêë]', 'e', new)
        new = re.sub(r'[ìíîï]', 'i', new)
        new = re.sub(r'[òóôõö]', 'o', new)
        new = re.sub(r'[ùúûü]', 'u', new)
        return new

     def stem_tokens(text):
        return [stemmer.stem(token) for token in text]

     def normalize(text):

        return Helper.stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))
     
     @staticmethod 
     def cosine_sim( text1, text2):
        text1 = Helper.f_remove_accents(text1)
        text2 = Helper.f_remove_accents(text2)

        vectorizer = TfidfVectorizer (
            tokenizer = Helper.normalize, 
            stop_words = stop_words, 
            ngram_range=(1,1))
        tfidf = vectorizer.fit_transform([text1, text2])
        return ((tfidf * tfidf.T).A) [0,1]  
     
     def tryMe(self):               
        text1 ="licence Economie, gestion mention administration économique et sociale"
        text2="Master Droit, économie, gestion, mention Droit de l'immobilier"
        print("la similarité est :", self.cosine_sim(text1, text2))

if __name__ == "__main__":
    helper = Helper()
    helper.tryMe()

