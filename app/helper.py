import os
from twilio.rest import Client
from flask import  jsonify
import sys
import re


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
        print('****** ERROR ******'+error)
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
