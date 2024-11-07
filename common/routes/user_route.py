from flask import request, jsonify, json
from common.daos.user_dao import user_dao
from common.models import db
from common.models.user import User
from common.models.lead import Lead
from common.models.bac  import Bac
from common.models.degree import Degree
from common.models.passport import Passport
from common.models.external_degree import ExternalDegree
from common.models.lead_level_value_relation import LeadLevelValueRelation
from common.models.lead_subject_relation import LeadSubjectRelation
from common.models.external_school import ExternalSchool
from common.models.report_card import ReportCard
from common.models.report_card_subject_relation import ReportCardSubjectRelation
from common.models.subject import Subject
from common.models.external_subject import ExternalSubject
from common.models.school_year import SchoolYear
from common.models.award import Award
from common.models.work_experience import WorkExperience
from common.models.traveling import Traveling
from common.models.course import Course
from common.models.course_level_relation import CourseLevelRelation
from common.models.course_subject_relation import CourseSubjectRelation
from common.models.visa_criteria import VisaCriteria
from common.models.criteria_type import CriteriaType
from common.models.visa_criteria_lead_relation import VisaCriteriaLeadRelation
from common.models.json_input import JsonInput
from common.models.log import Log
from common.helper import Helper
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from functools import lru_cache
import re
import time
from typing import Dict, Any, Optional, List, Set, Tuple
from contextlib import contextmanager
import json
from dataclasses import dataclass
import random
#from typing import Dict, List, Optional, Set, Tuple


@contextmanager
def db_transaction():
    """Context manager for database transactions with error handling"""
    try:
        yield
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise DatabaseError(f"Database transaction failed: {str(e)}")
    except Exception as e:
        db.session.rollback()
        raise
class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


def init_routes(app):
    @app.route('/users', methods=['GET'])
    def get_user():
        users = user_dao.get_all()
        #users = users_schema.dump(data)
        return jsonify(users)
    
    @app.route('/user/add', methods=['POST'])
    def add_user():
        _json = request.json
        phone = _json.get('phone')
        user = User.query.filter_by(phone = phone).first()
        if user is not None:
            _json['phone'] = phone+1
        new_user = User()
        for key in _json:
            setattr(new_user, key, _json[key] if (key in _json) else '')
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": True, "message": "user has been added"})



    @app.route('/user/<phone>', methods=['GET'])
    def user_byphone(phone):
        user = User.query.filter_by(phone = phone).first()
        #data = user_schema.dump(user)
        return jsonify(user.as_dict())

    @app.route('/user/delete/<id>', methods=['POST'])
    def delete_user(id):
        user = User.query.get(id)
        if user is None:
            return jsonify(f"Error: user doesn't exist")
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "user has been deleted"})

    @app.route('/user/edit', methods=['PATCH'])
    def edit_user():
        _json = request.json
        phone = _json.get('phone')
        user = User.query.filter_by(id=_json.get('userId')).first() 
        if not user:
            user = User.query.filter_by(phone = phone).first()
        if user is None:
            return jsonify ({"error": "the user doesn't exist", "status": False})
        for key in _json:
            setattr(user, key, _json[key])
        # user.name = _json['name']
        # user.firstname = _json['firstname']
        # user.lastname = _json['lastname']
        # user.salutation = _json['salutation']
        # user.city = _json['city']
        # user.email = _json['email']
        # user.phone = _json['phone']
        # user.occupation = _json['occupation']
        # user.description = _json['description']
        db.session.commit()
        return jsonify({"status": True, "message": "user has been edited"})

    @app.route('/user/add/verification', methods=['POST'])
    def verify_whatsapp_and_add_user():
        try:
            _json = request.get_json()
            firstname = _json['firstname'].title()
            lastname = _json['lastname'].title()
            phone = _json.get('phone')
            country = _json.get('country')
            userMaybe = User.query.filter_by(phone = phone).first()
            is_code_has_been_sent = False
            #return jsonify({"user": 'new_user.as_dict()', "sent": False, "success": True})
            #print ('<==== userMaybe ', Helper.rows_as_dicts(userMaybe))
            if userMaybe is None : # user doesn't exist, we send a verification code and we create a new user
                print('########## user doesn\'t exist')
                new_user = User(firstname=firstname, lastname=lastname, salutation='', city='', email='', phone=phone, occupation='', description='', country=country)
                new_user.subscription_step = '/verification' #Step 1 => Go to  Verification Code Page
                db.session.add(new_user)
                db.session.commit()
                if phone is not None:
                    print('########## user does exist and has been verified')
                    is_code_has_been_sent = Helper.send_whatsapp_verification_code(phone)
                return jsonify({"user": new_user.as_dict(), "sent": is_code_has_been_sent,  "success": True})
            elif userMaybe.has_whatsapp : # user does exist and has been verified, we'll suggest to user to edit occupation/description
                print('########## user does exist and has been verified')
                return jsonify({"user": userMaybe.as_dict(), "sent": is_code_has_been_sent, "success": True})
            elif not userMaybe.has_whatsapp: # user does exist and hasn't been verified, we sent a verification once again
                print('########## user does exist and hasn\'t been verified')
                Helper.send_whatsapp_verification_code(phone)
                return jsonify({"user": userMaybe.as_dict(), "sent": is_code_has_been_sent, "success": True})
            
        except Exception as e:
            print('========error', e)
            Helper.logError(e, db, Log, request)    

    @app.route('/user/verificationCheck', methods=['POST'])
    def check_whatsapp_phone():   
        try:
            _json = request.get_json()
            phone = _json.get('phone')
            code = _json.get('code')
            is_number_verify = Helper.check_whatsapp_verification_code(phone, code) 
            user = User.query.filter_by(phone = phone).first()
            user.whatsapp_verification_attempt = user.whatsapp_verification_attempt+1
            if is_number_verify:
                user.has_whatsapp = True
                user.subscription_step = '/credentialstart' #Step 2 => Go to  Credential 1 Page
            db.session.commit()
            return jsonify({"user": user.as_dict(), "verify": is_number_verify, "success": True})
        except Exception as e:
            Helper.logError(e, db, Log, request) 
        
    @app.route('/user/update/credentials', methods=['POST'])
    def update_credentials():  
        try:
            _json = request.get_json()
            phone = _json.get('phone')
            user = User.query.filter_by(phone = phone).first()
            print('user', _json.get('birthdate'))
            if _json.get('firstname') and _json.get('lastname') and _json.get('salutation') and _json.get('birthdate'):
                user.firstname = _json.get('firstname').title()
                user.lastname = _json.get('lastname').title()
                user.birthdate = datetime.strptime( _json.get('birthdate'), '%Y-%m-%d')
                user.salutation = _json.get('salutation')
                user.email = _json.get('email') if not _json.get('doesntHaveEmail') else ''
                user.subscription_step = '/credentialend'  #Step 3 => Go to  Credential 2 Page
            elif _json.get('country') and _json.get('city') and _json.get('occupation') and _json.get('description'):
                user.country = _json.get('country').title()
                user.city = _json.get('city').title()
                user.occupation = _json.get('occupation')
                user.description = _json.get('description')
                user.subscription_step = '/congratulation' #Step 4 => Go to  Congratulation Page
            db.session.commit()
            return jsonify({"user": user.as_dict(), "success": True})
        except Exception as e:
            Helper.logError(e, db, Log, request) 

    @app.route('/user/update/subscriptionStep', methods=['PUT'])
    def update_subscription_step():  
        try:
            _json = request.get_json()
            phone = _json.get('phone')
            user = User.query.filter_by(phone = phone).first()
            if _json.get('subscriptionStep'):
                user.subscription_step = _json.get('subscriptionStep')  
            db.session.commit()
            return jsonify({"user": user.as_dict(), "success": True})
        except Exception as e:
            Helper.logError(e, db, Log, request) 

    @app.route('/countries/cities/<country_iso2>', methods=['GET'])
    def get_countries(country_iso2):
        try:    
            country_res = db.session.execute(text("SELECT translations, iso2, capital, id, most_popular_spoken_language_id FROM countries"))
            data_country, data_city, data_city_new = [], [], []
            selectedCountryCapital = ''

            for row in country_res:
                json_object = row[0]
                json_object = json.loads(json_object)
                #country_local = json_object['fr']
                if "fr" in json_object: 
                    if row[1].lower() == country_iso2.lower():
                        selectedCountryCapital = row[2]
                    data_country.append({'id': row[3], 'name': str(json_object["fr"]), 'iso2': row[1], 'most_popular_spoken_language_id': row[4],'default':row[1] == country_iso2})

            city_res = db.session.execute(text("SELECT id, name, country_id FROM cities WHERE country_code = '"+country_iso2+"'"))

            for row in city_res:
                data_city.append({'value': row[1], 'selected': Helper.f_remove_accents(row[1]) == Helper.f_remove_accents(selectedCountryCapital)}) 
                data_city_new.append({'id': row[0], 'name': row[1], 'country_id':  row[2], 'default': Helper.f_remove_accents(row[1]) == Helper.f_remove_accents(selectedCountryCapital)})
            return {"countries": data_country, "cities_new": data_city_new, "cities": data_city, "success": True}  #cities_new is for the new design, cities is for the old design (credentialend)
        except Exception as e:
            Helper.logError(e, db, Log, request)   


    @app.route('/user/generate/courses', methods=['PUT'])
    def update_user_and_insert_lead_reports_and_generate_courses():
        user_payload = request.json
    
        user_payload = request.json

        user = User.query.filter_by(phone=user_payload.get('phone')).first()
        if not user:
            user = User.query.filter_by(id=user_payload.get('userId')).first()
        if not user:
            return jsonify({"error": "User not found", "status": False}), 404

        try:
            """I - Insert or update user and related data"""
            update_user(user, user_payload)
            lead = update_or_create_lead(user.id, user_payload)
            delete_and_create_json_input(lead.id, user_payload)
            delete_and_create_passport(user.id, user_payload)
            external_degree = update_or_create_external_degree(user_payload)
            if user_payload.get('programDomainObj', {}) is not None:
                if user_payload.get('programDomainObj', {}).get('id') :
                    delete_and_create_lead_level_relation(lead.id, user_payload, external_degree.id)
            delete_and_create_lead_subject_relations(lead.id, user_payload)
            
            delete_all_report_cards_and_report_card_subject_relations(lead.id)
            create_report_card(user_payload, lead.id, level=3)
            create_report_card(user_payload, lead.id, level=2)
            create_report_card(user_payload, lead.id, level=1)
            delete_and_create_award(user_payload, lead.id)
            delete_and_create_work_experience(user_payload, lead.id)
            delete_and_create_traveling(user_payload, lead.id)

            """II - Process to generate courses"""
            course_results = generate_courses(lead)
            course_results['user_id'] = user.id
            return jsonify(course_results)
        except SQLAlchemyError as e:
            db.session.rollback()
            print('Database error:', e)
            return Helper.logError(e, db, Log, request)

    """Helper functions"""
    
    #def get_list_of_courses_by_lead_level_value(level_value_id):
    #   return Course.query.filter_by(level_value_id=level_value_id).all()

    def update_user(user, payload):
        user.firstname = payload.get('firstname')
        user.lastname = payload.get('lastname')
        user.phone = payload.get('phoneNumberFormatted', {}).get('name')
        user.country = payload.get('selectedCountry', {}).get('iso2')
        user.email = payload.get('email')
        user.birthdate = parse_date(payload.get('birthDate', {}).get('date'))
        user.address = payload.get('address', {}).get('name')
        user.salutation = payload.get('salutation')
        user.nationality_id = payload.get('nationality', {}).get('id')
        user.is_disabled = payload.get('disable')
        user.french_travel_start_date = parse_date(payload.get('frenchTravelDate', {}).get('startDate'))
        user.french_travel_end_date = parse_date(payload.get('frenchTravelDate', {}).get('endDate'))
        db.session.commit()

    def update_or_create_lead(user_id, payload):
        # Retrieve the existing lead or create a new one if not found
        lead = Lead.query.filter_by(user_id=user_id).first()
        nonlocal blank_year_1_time, blank_year_2_times_and_more
        if not lead:
            # Retrieve the highest existing ID for Lead and increment it
            last_lead = Lead.query.order_by(Lead.id.desc()).first()
            new_lead_id = (last_lead.id + 1) if last_lead else 1

            lead = Lead(id=new_lead_id, user_id=user_id)

        # Update lead attributes based on payload
        lead.visa_id = payload.get('visaTypeSelectedId')
        hs_level_selected = payload.get('hsLevelSelected')
        lead.degree_id = hs_level_selected
        
        if hs_level_selected in ['deg00003', 'deg00002']:
            lead.bac_id = f'bac0000{hs_level_selected[-1]}'
        else:
            lead.bac_id = payload.get('universityLevelSelected', {}).get('id')
            lead.degree_id = payload.get('degreeSelected', {}).get('id')
        
        lead.can_finance = payload.get('couldPayTuition')
        lead.french_level = get_french_level(payload.get('selectedFrenchLevel'))
        lead.can_prove_french_level = payload.get('haveDoneFrenchTest')
        lead.english_level = get_english_level(payload.get('selectedEnglishLevel'))
        lead.can_prove_english_level = payload.get('canJustifyEnglishLevel')
        if(payload.get('selectedOtherSpokenLanguage', {}).get('id') != "none"):
            lead.other_spoken_language_id = payload.get('selectedOtherSpokenLanguage', {}).get('id')
        lead.other_spoken_language_level = get_language_level(payload.get('selectedOtherLanguageLevel'))
        lead.can_prove_spoken_language_level = payload.get('canJustifyOtherLanguage')
        lead.number_of_repeats_n_3 = payload.get('classRepetitionNumber')
        lead.number_of_blank_years = payload.get('blankYearRepetitionNumber')

        if payload.get('blankYearRepetitionNumber') == 1:
            blank_year_1_time = True
        if payload.get('blankYearRepetitionNumber') >= 2:
            blank_year_2_times_and_more = True
        
        db.session.add(lead)
        db.session.commit()
        
        return lead

    def delete_and_create_json_input(lead_id: str, payload: Dict[str, Any]) -> JsonInput:
        """
        Delete existing JSON input for a lead and create a new one.
        
        Args:
            lead_id: The ID of the lead
            payload: The JSON payload to store
            
        Returns:
            JsonInput: The newly created JSON input record
            
        Raises:
            DatabaseError: If database operations fail
            ValueError: If input validation fails
        """
        try:
            # Input validation
            if not lead_id or not payload:
                raise ValueError("Lead ID and payload are required")

            with db_transaction():
                # Get next ID using database sequence if available
                # Or use the current implementation
                next_id = get_next_json_input_id()
                
                # Delete existing records and create new one in a single transaction
                JsonInput.query.filter_by(lead_id=lead_id).delete()
                
                # Create new JSON input with minified payload
                new_json_input = JsonInput(
                    id=next_id,
                    lead_id=lead_id,
                    content=json.dumps(payload, separators=(',', ':'))
                )
                
                db.session.add(new_json_input)
                return new_json_input
                
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON payload")
        except ValueError as e:
            raise ValueError(f"Validation error: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Failed to update JSON input: {str(e)}")

    def get_next_json_input_id() -> str:
        """Get the next available JSON input ID"""
        try:
            # Using a database sequence would be better, but if not available:
            last_record = JsonInput.query\
                .with_entities(JsonInput.id)\
                .order_by(JsonInput.id.desc())\
                .first()
            
            return str(int(last_record.id) + 1) if last_record else "1"
        except Exception as e:
            raise DatabaseError(f"Failed to generate next ID: {str(e)}")

    def delete_all_report_cards_and_report_card_subject_relations(lead_id):
        # Delete all report card subject relations in one go
        report_card_ids = [rc.id for rc in ReportCard.query.filter_by(lead_id=lead_id).all()]
        if report_card_ids:
            ReportCardSubjectRelation.query.filter(ReportCardSubjectRelation.report_card_id.in_(report_card_ids)).delete(synchronize_session=False)
        
        # Delete all report cards in one go
        ReportCard.query.filter_by(lead_id=lead_id).delete(synchronize_session=False)
        
        # Commit the changes
        db.session.commit()



    class PassportError(Exception):
        """Custom exception for passport-related errors"""
        pass

    def parse_date(date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date string in format YYYY-MM-DD
            
        Returns:
            datetime object or None if invalid date
        """
        if not date_str:
            return None
            
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise PassportError(f"Invalid date format: {date_str}. Expected format: YYYY-MM-DD")

    def validate_passport_details(details: Dict) -> None:
        """Validate passport details"""
        if not details:
            raise PassportError("Passport details are required")
            
        required_fields = ['startDate', 'endDate']
        missing_fields = [field for field in required_fields if not details.get(field)]
        
        if missing_fields:
            raise PassportError(f"Missing required fields: {', '.join(missing_fields)}")
            
        start_date = parse_date(details.get('startDate'))
        end_date = parse_date(details.get('endDate'))
        
        if start_date and end_date and start_date > end_date:
            raise PassportError("Delivery date cannot be after expiration date")

    def get_next_passport_id() -> int:
        """Get next available passport ID"""
        try:
            last_passport = Passport.query\
                .with_entities(Passport.id)\
                .order_by(Passport.id.desc())\
                .first()
            return (last_passport.id + 1) if last_passport else 1
        except Exception as e:
            raise DatabaseError(f"Failed to generate next ID: {str(e)}")

    def delete_and_create_passport(user_id: str, payload: Dict) -> Optional[Passport]:
        """
        Delete existing passport for a user and create a new one if details provided.
        
        Args:
            user_id: User ID
            payload: Dictionary containing passport details
            
        Returns:
            New Passport object or None if no passport details provided
            
        Raises:
            DatabaseError: If database operations fail
            PassportError: If passport validation fails
            ValueError: If input validation fails
        """
        try:
            if not user_id:
                raise ValueError("User ID is required")

            passport_details = payload.get('passportDetails')
            if not passport_details:
                # If no passport details, just delete existing passport
                with db_transaction():
                    Passport.query.filter_by(user_id=user_id).delete()
                return None

            # Validate passport details
            validate_passport_details(passport_details)

            with db_transaction():
                # Delete existing passport and create new one in single transaction
                Passport.query.filter_by(user_id=user_id).delete()
                
                new_passport = Passport(
                    id=get_next_passport_id(),
                    user_id=user_id,
                    delivery_date=parse_date(passport_details['startDate']),
                    valid_until=parse_date(passport_details['endDate'])
                )
                
                db.session.add(new_passport)
                return new_passport

        except (ValueError, PassportError) as e:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to update passport: {str(e)}")


    class DegreeError(Exception):
        """Custom exception for degree-related errors"""
        pass 

    def validate_degree_name(name: str) -> str:
        """
        Validate and clean degree name.
        
        Args:
            name: The degree name to validate
            
        Returns:
            Cleaned degree name
            
        Raises:
            DegreeError: If name is invalid
        """
        if not name:
            raise DegreeError("Degree name is required")
            
        cleaned_name = name.strip()
        if len(cleaned_name) < 2:
            raise DegreeError("Degree name is too short")
        
        if len(cleaned_name) > 1024:  # Adjust max length as needed
            raise DegreeError("Degree name is too long")
            
        return cleaned_name

    def get_next_degree_id() -> int:
        """Get next available degree ID"""
        try:
            last_degree = ExternalDegree.query\
                .with_entities(ExternalDegree.id)\
                .order_by(ExternalDegree.id.desc())\
                .first()
            return (last_degree.id + 1) if last_degree else 1
        except Exception as e:
            raise DegreeError(f"Failed to generate next ID: {str(e)}")

    def find_existing_degree(name: str) -> Optional[ExternalDegree]:
        """Find existing degree by name (case insensitive)"""
        try:
            return ExternalDegree.query\
                .filter(ExternalDegree.name.ilike(name))\
                .first()
        except SQLAlchemyError as e:
            raise DegreeError(f"Error searching for existing degree: {str(e)}")

    def update_or_create_external_degree(payload: dict) -> ExternalDegree:
        """
        Update existing degree or create new one.
        
        Args:
            payload: Dictionary containing degree details
            
        Returns:
            ExternalDegree: Updated or created degree
            
        Raises:
            DegreeError: If operation fails
        """
        try:
            # Extract and validate degree name
            raw_name = payload.get('degreeExactNameValue', '')
            degree_name = validate_degree_name(raw_name)
            
            # Check for existing degree
            existing_degree = find_existing_degree(degree_name)
            if existing_degree:
                return existing_degree
                
            # Create new degree
            with db_transaction():
                new_degree = ExternalDegree(
                    id=get_next_degree_id(),
                    name=degree_name
                )
                db.session.add(new_degree)
                return new_degree
                
        except DegreeError:
            raise
        except Exception as e:
            raise DegreeError(f"Unexpected error: line - {str(e.__traceback__.tb_lineno)}: {str(e)}")


    class RelationError(Exception):
        """Custom exception for lead-level relation errors"""
        pass

    def validate_relation_data(
        lead_id: str,
        payload: Dict,
        external_degree_id: str
    ) -> None:
        """Validate input data for relation creation"""
        if not lead_id:
            raise RelationError("Lead ID is required")
            
        if not external_degree_id:
            raise RelationError("External degree ID is required")
            
        if not payload.get('programDomainObj', {}).get('id'):
            raise RelationError("Program domain ID is required")
            
        if not payload.get('selectedSchoolYear3', {}).get('name'):
            raise RelationError("School year is required")

    def get_next_relation_llvr_id() -> int:
        """Get next available relation ID"""
        try:
            last_relation = LeadLevelValueRelation.query\
                .with_entities(LeadLevelValueRelation.id)\
                .order_by(LeadLevelValueRelation.id.desc())\
                .first()
            return (last_relation.id + 1) if last_relation else 1
        except Exception as e:
            raise RelationError(f"Failed to generate next ID: {str(e)}") 
        
    def get_next_relation_lsr_id() -> int:
        """Get next available relation ID"""
        try:
            last_relation = LeadSubjectRelation.query\
                .with_entities(LeadSubjectRelation.id)\
                .order_by(LeadSubjectRelation.id.desc())\
                .first()
            return (last_relation.id + 1) if last_relation else 1
        except Exception as e:
            raise SubjectRelationError(f"Failed to generate next ID: {str(e)}")

    def get_school_year_id(year_name: str) -> Optional[int]:
        """Get school year ID from year name"""
        try:
            if not year_name:
                return None
                
            # Your existing get_school_year_id implementation
            # Add appropriate error handling
            return get_school_year_id(year_name)
            
        except Exception as e:
            raise RelationError(f"Failed to get school year ID: {str(e)}")

    def create_relation(
        lead_id: str,
        payload: Dict,
        external_degree_id: str
    ) -> LeadLevelValueRelation:
        """Create new lead level relation"""
        school_year_name = payload.get('selectedSchoolYear3', {}).get('name')
        current_year = str(datetime.now().year)
        
        return LeadLevelValueRelation(
            id=get_next_relation_llvr_id(),
            lead_id=lead_id,
            level_value_id=payload.get('programDomainObj', {}).get('id'),
            external_degree_id=external_degree_id,
            school_year_id=get_school_year_id(school_year_name),
            is_current_year=(school_year_name == current_year)
        )

    def delete_and_create_lead_level_relation(
        lead_id: str,
        payload: Dict,
        external_degree_id: str
    ) -> LeadLevelValueRelation:
        """
        Delete existing lead level relations and create a new one.
        
        Args:
            lead_id: Lead ID
            payload: Data payload
            external_degree_id: External degree ID
            
        Returns:
            LeadLevelValueRelation: Newly created relation
            
        Raises:
            RelationError: If operation fails
        """
        try:
            # Validate input data
            validate_relation_data(lead_id, payload, external_degree_id)
            
            with db_transaction():
                # Delete existing relations
                LeadLevelValueRelation.query.filter_by(lead_id=lead_id).delete()
                #print('deleted payload 😘 ', str(payload))
                # Create and add new relation
                new_relation = create_relation(
                    lead_id=lead_id,
                    payload=payload,
                    external_degree_id=external_degree_id
                )
                
                db.session.add(new_relation)
                return new_relation
                
        except RelationError:
            raise
        except Exception as e:
            raise RelationError(f"Unexpected error: line - {str(e.__traceback__.tb_lineno)}: {str(e)}")


    class SubjectRelationError(Exception):
        """Custom exception for lead-subject relation errors"""
        pass 

    def validate_subject_data(subject: Dict) -> None:
        """
        Validate individual subject data
        
        Args:
            subject: Subject data dictionary
            
        Raises:
            SubjectRelationError: If validation fails
        """
        if not subject.get('id'):
            raise SubjectRelationError("Subject ID is required")
            
        if not isinstance(subject.get('priority'), (int, float)):
            raise SubjectRelationError("Valid priority value is required")

    def validate_payload(lead_id: str, payload: Dict) -> None:
        """
        Validate input payload
        
        Args:
            lead_id: Lead ID
            payload: Input payload
            
        Raises:
            SubjectRelationError: If validation fails
        """
        if not lead_id:
            raise SubjectRelationError("Lead ID is required")
            
        subjects = payload.get('mainSubjects', [])
        if not isinstance(subjects, list):
            raise SubjectRelationError("Main subjects must be a list")
            
        for subject in subjects:
            validate_subject_data(subject)

    def create_subject_relation(
        relation_id: int,
        lead_id: str,
        subject: Dict
    ) -> LeadSubjectRelation:
        """Create a single subject relation"""
        return LeadSubjectRelation(
            id=relation_id,
            lead_id=lead_id,
            subject_id=subject.get('id'),
            priority=subject.get('priority')
        )

    def delete_and_create_lead_subject_relations(
        lead_id: str,
        payload: Dict
    ) -> List[LeadSubjectRelation]:
        """
        Delete existing subject relations and create new ones.
        
        Args:
            lead_id: Lead ID
            payload: Data payload containing subject relations
            
        Returns:
            List[LeadSubjectRelation]: List of newly created relations
            
        Raises:
            SubjectRelationError: If operation fails
        """
        try:
            # Validate input data
            validate_payload(lead_id, payload)
            
            subjects = payload.get('mainSubjects', [])
            if not subjects:
                # If no subjects provided, just delete existing relations
                with db_transaction():
                    LeadSubjectRelation.query.filter_by(lead_id=lead_id).delete()
                return []

            with db_transaction():
                # Delete existing relations
                LeadSubjectRelation.query.filter_by(lead_id=lead_id).delete()
                
                # Create new relations
                next_id = get_next_relation_lsr_id()
                new_relations = []
                
                for subject in subjects:
                    relation = create_subject_relation(
                        relation_id=next_id,
                        lead_id=lead_id,
                        subject=subject
                    )
                    db.session.add(relation)
                    new_relations.append(relation)
                    next_id += 1
                    
                return new_relations
                
        except SubjectRelationError:
            raise
        except Exception as e:
            raise SubjectRelationError(f"Unexpected error: line - {str(e.__traceback__.tb_lineno)}: {str(e)}")

    class ReportCardError(Exception):
        """Custom exception for report card operations"""
        pass

    @dataclass
    class SchoolData:
        name: str
        city_id: int
        educational_language_id: int

    @dataclass
    class ReportCardData:
        lead_id: str
        bac_id: str
        country_id: int
        school_year_id: int
        city_id: int
        external_school_id: int
        spoken_language_id: int
        academic_year_organization_id: int
        mark_system_id: int
        subject_weight_system_id: int

    class ReportCardCreator:
        def __init__(self, payload: Dict, lead_id: str, level: int):
            self.payload = payload
            self.lead_id = lead_id
            self.level = level
            self.validate_input()

        def validate_input(self) -> None:
            """Validate input data"""
            if not self.lead_id:
                raise ReportCardError("Lead ID is required")
                
            if not self.payload.get(f'isResult{self.level}Available'):
                raise ReportCardError(f"Results for level {self.level} are not available")
                
            head_details = self.payload.get(f'academicYearHeadDetails{self.level}')
            if not head_details:
                raise ReportCardError(f"Academic year head details for level {self.level} are missing")

        def get_next_id(self, model_class) -> int:
            """Get next available ID for a model"""
            last_record = model_class.query\
                .with_entities(model_class.id)\
                .order_by(model_class.id.desc())\
                .first()
            return (last_record.id + 1) if last_record else 1

        def handle_external_school(self) -> ExternalSchool:
            """Create or get existing external school"""
            head_details = self.payload[f'academicYearHeadDetails{self.level}']
            school_name = head_details['schoolName']

            # Check existing school
            external_school = ExternalSchool.query.filter_by(name=school_name).first()
            if external_school:
                return external_school

            # Create new school
            school_data = SchoolData(
                name=school_name,
                city_id=head_details['city']['id'],
                educational_language_id=head_details['spokenLanguage']['id']
            )

            with db_transaction():
                new_school = ExternalSchool(
                    id=self.get_next_id(ExternalSchool),
                    name=school_data.name,
                    city_id=school_data.city_id,
                    educational_language_id=school_data.educational_language_id
                )
                db.session.add(new_school)
                return new_school

        def determine_bac_id(self) -> str:
            """Determine BAC ID based on level"""
            most_recent_bac_id = get_most_recent_bac_id(self.payload)
            if self.level == 3:
                return most_recent_bac_id
                
            bac_number = int(most_recent_bac_id[-1]) - (3 - self.level)
            return f'bac0000{bac_number}'

        def create_report_card_data(self, external_school: ExternalSchool) -> ReportCardData:
            """Prepare report card data"""
            head_details = self.payload[f'academicYearHeadDetails{self.level}']
            
            return ReportCardData(
                lead_id=self.lead_id,
                bac_id=self.determine_bac_id(),
                country_id=head_details['country']['id'],
                school_year_id=get_school_year_id(
                    self.payload[f'selectedSchoolYear{self.level}']['name']
                ),
                city_id=head_details['city']['id'],
                external_school_id=external_school.id,
                spoken_language_id=head_details['spokenLanguage']['id'],
                academic_year_organization_id=head_details['academicYearOrganization']['id'],
                mark_system_id=head_details['markSystem']['id'],
                subject_weight_system_id=head_details['subjectWeightSystem']['id']
            )

        def create(self) -> ReportCard:
            """Create report card and related records"""
            try:
                # Handle external school
                external_school = self.handle_external_school()
                
                # Prepare report card data
                report_card_data = self.create_report_card_data(external_school)
                
                # Create report card
                with db_transaction():
                    report_card = ReportCard(
                        id=self.get_next_id(ReportCard),
                        **report_card_data.__dict__
                    )
                    db.session.add(report_card)
                
                # Create subject relations
                create_report_card_subject_relations(
                    report_card.id,
                    self.payload,
                    self.level
                )
                
                return report_card
                
            except ReportCardError:
                raise
            except Exception as e:
                raise ReportCardError(f"Failed to create report card: line - {str(e.__traceback__.tb_lineno)}: {str(e)}")

    def create_report_card(payload: Dict, lead_id: str, level: int) -> Optional[ReportCard]:
        """
        Create a new report card with associated records.
        
        Args:
            payload: Input data dictionary
            lead_id: Lead ID
            level: Academic level
            
        Returns:
            ReportCard: Created report card or None if not applicable
            
        Raises:
            ReportCardError: If creation fails
        """
        try:
            if not payload.get(f'isResult{level}Available') or \
            not payload.get(f'academicYearHeadDetails{level}'):
                return None
                
            creator = ReportCardCreator(payload, lead_id, level)
            return creator.create()
            
        except ReportCardError as e:
            raise
        except Exception as e:
            raise ReportCardError(f"Unexpected error: line - {str(e.__traceback__.tb_lineno)}: {str(e)}")

    def get_most_recent_bac_id(payload):
        hs_level_selected = payload.get('hsLevelSelected')
        if hs_level_selected in ['deg00003', 'deg00002']:
            return f'bac0000{hs_level_selected[-1]}'
        return payload.get('universityLevelSelected', {}).get('id')

    def create_report_card_subject_relations(report_card_id, payload, level):
        # Extract labels and subjects
        label_values = [subject['label']['value'] for subjects in payload[f'reportCard{level}'] for subject in subjects]
        existing_subjects = Subject.query.filter(or_(*[Subject.name.ilike(label) for label in label_values])).all()
        existing_subjects_map = {subject.name: subject.id for subject in existing_subjects}
        new_subjects = set(label_values) - set(existing_subjects_map.keys())
        external_subjects_map = {}
        total_weighted_marks = 0
        total_weights = 0
        total_ranks = 0
        rank_count = 0

        school_term_marks = {1: [], 2: [], 3: [], 4: []}
        school_term_ranks = {1: [], 2: [], 3: []}
        baccalaureat_marks = []

        # Get the highest existing IDs for ExternalSubject and ReportCardSubjectRelation
        last_external_subject = ExternalSubject.query.order_by(ExternalSubject.id.desc()).first()
        new_external_subject_id = (last_external_subject.id + 1) if last_external_subject else 1

        last_relation = ReportCardSubjectRelation.query.order_by(ReportCardSubjectRelation.id.desc()).first()
        new_relation_id = (last_relation.id + 1) if last_relation else 1

        for new_subject in new_subjects:
            capitalized_subject = new_subject.capitalize()
            external_subject = ExternalSubject.query.filter_by(name=capitalized_subject).first()

            if not external_subject:
                external_subject = ExternalSubject(id=new_external_subject_id, name=capitalized_subject)
                db.session.add(external_subject)
                db.session.commit()
                external_subjects_map[new_subject] = new_external_subject_id
                new_external_subject_id += 1
            else:
                external_subjects_map[new_subject] = external_subject.id

        for subjects in payload[f'reportCard{level}']:
            for subject in subjects:
                school_term = payload[f'reportCard{level}'].index(subjects) + 1
                is_baccalaureat = subject['isBaccalaureat']
                weight = int(subject['weight']['value'])
                mark_in_20 = float(subject['mark']['valueIn20']) if subject['mark']['valueIn20'] is not None else float(subject['mark']['value'])
                
                total_weighted_marks += weight * mark_in_20
                total_weights += weight

                if not is_baccalaureat:
                    school_term_marks[school_term].append(mark_in_20)
                else:
                    baccalaureat_marks.append(mark_in_20)

                rank = subject.get('rank', {}).get('value', None)
                if not rank:
                    school_term_ranks[school_term] = []
                    break
                rank = int(rank)
                total_ranks += rank
                rank_count += 1
                if not is_baccalaureat:
                    school_term_ranks[school_term].append(rank)

                relation = ReportCardSubjectRelation(
                    id=new_relation_id,
                    report_card_id=report_card_id,
                    school_term=school_term,
                    external_subject_id=external_subjects_map.get(subject['label']['value']),
                    subject_id=existing_subjects_map.get(subject['label']['value']),
                    is_baccalaureat=is_baccalaureat,
                    is_pratical_subject=subject['isPracticalWork'],
                    weight=weight,
                    mark=subject['mark']['value'],
                    mark_in_20=mark_in_20,
                    rank=rank
                )
                db.session.add(relation)
                new_relation_id += 1
            
        report_card = ReportCard.query.get(report_card_id)

        for term in range(1, 5):
            if school_term_marks[term]:
                setattr(report_card, f'school_term{term}_average_mark_in_20', round(sum(school_term_marks[term]) / len(school_term_marks[term]), 2))

        if baccalaureat_marks:
            report_card.baccalaureat_average_mark_in_20 = round(sum(baccalaureat_marks) / len(baccalaureat_marks), 2)

        if total_weights > 0:
            average_mark_in_20 = sum([getattr(report_card, f'school_term{term}_average_mark_in_20') for term in range(1, 4) if getattr(report_card, f'school_term{term}_average_mark_in_20') is not None]) / len([term for term in range(1, 4) if getattr(report_card, f'school_term{term}_average_mark_in_20') is not None])
            report_card.average_mark_in_20 = round(average_mark_in_20, 2)

        for term in range(1, 4):
            if len(school_term_ranks[term]) == len([subject for subjects in payload[f'reportCard{level}'] for subject in subjects if payload[f'reportCard{level}'].index(subjects) + 1 == term and not subject['isBaccalaureat']]):
                if len(school_term_ranks[term]) > 0:
                    setattr(report_card, f'school_term{term}_overall_rank', sum(school_term_ranks[term]) / len(school_term_ranks[term]))

        if rank_count == len([subject for subjects in payload[f'reportCard{level}'] for subject in subjects]):
            overall_ranks = [getattr(report_card, f'school_term{term}_overall_rank') for term in range(1, 4) if getattr(report_card, f'school_term{term}_overall_rank') is not None]
            if overall_ranks:
                overall_rank = sum(overall_ranks) / len(overall_ranks)
                report_card.overall_rank = overall_rank

        db.session.add(report_card)
        db.session.commit()

    def delete_and_create_award(payload, lead_id):
        # Delete existing awards for the lead
        Award.query.filter_by(lead_id=lead_id).delete()

        award_data = payload.get('award')
        if award_data:
            # Get the highest ID currently in the Award table
            last_award = Award.query.order_by(Award.id.desc()).first()
            new_id = (last_award.id + 1) if last_award else 1  # Increment the ID or start at 1 if no awards exist

            # Create the new award
            award = Award(id=new_id, lead_id=lead_id)
            award.name = award_data.get('awardName')
            award.school_year_id = award_data.get('year', {}).get('id')
            award.country_id = award_data.get('country', {}).get('id')
            award.city_id = award_data.get('city', {}).get('id')
            award.spoken_language_id = award_data.get('spokenLanguage', {}).get('id')
            award.honour_type = award_data.get('honourType', {}).get('name')
            award.rank = award_data.get('rank')

            # Add and commit the new award to the database
            db.session.add(award)
            db.session.commit()


    def delete_and_create_work_experience(payload, lead_id):
        WorkExperience.query.filter_by(lead_id=lead_id).delete()
        work_experience_data = payload.get('workExperience')
        if work_experience_data:
            
            last_work_experience = WorkExperience.query.order_by(WorkExperience.id.desc()).first()
            new_id = (last_work_experience.id + 1) if last_work_experience else 1

            work_experience = WorkExperience(id=new_id, lead_id=lead_id)
            work_experience.description = work_experience_data.get('description')
            work_experience.start_date = parse_date(work_experience_data.get('startDate'))
            work_experience.end_date = parse_date(work_experience_data.get('endDate')) if work_experience_data.get('endDate') != 'None' else None
            work_experience.can_prove = payload.get('canProveWorkExperience')
            db.session.add(work_experience)
            db.session.commit()

    def delete_and_create_traveling(payload, lead_id):
        Traveling.query.filter_by(lead_id=lead_id).delete()
        traveling_data = payload.get('alreadyTraveledToFrance')
        if traveling_data:
            last_traveling = Traveling.query.order_by(Traveling.id.desc()).first()
            new_id = (last_traveling.id + 1) if last_traveling else 1

            traveling = Traveling(id=new_id, lead_id=lead_id)
            traveling.start_date = parse_date(payload.get('frenchTravelDate', {}).get('startDate'))
            traveling.end_date = parse_date(payload.get('frenchTravelDate', {}).get('endDate'))
            traveling.country_id = '75' # country_id for France
            db.session.add(traveling)
            db.session.commit()

    def get_school_year_id(name):
        school_year = SchoolYear.query.filter_by(name=name).first()
        if school_year:
            return school_year.id
        return None
    
    bac_validation_map = {
        'bac00010': (['bac00010', 'bac00009', 'bac00008'], 'bac00008', 'bac00010'), # The first element in the tuple is the list of bac_ids to validate, 
        'bac00009': (['bac00009', 'bac00008', 'bac00007'], 'bac00007', 'bac00009'), # the second element is the start_bac_id, and the third element is the end_bac_id 
        'bac00008': (['bac00008', 'bac00007', 'bac00006'], 'bac00006', 'bac00008'),
        'bac00007': (['bac00007', 'bac00006', 'bac00005'], 'bac00005', 'bac00007'),
        'bac00006': (['bac00006', 'bac00005', 'bac00004'], 'bac00004', 'bac00006'),
        'bac00005': (['bac00005', 'bac00004'], 'bac00003', 'bac00005'),
        'bac00004': (['bac00004'], 'bac00002', 'bac00004'),
        'bac00003': ([], 'bac00001', 'bac00003')
    }
    mark_has_progressed_for_2_years_with_no_redoublement = False # This is a global variable to check if the mark has progressed for 2 years with no redoublement
    mark_has_progressed_for_3_years_with_no_redoublement = False # This is a global variable to check if the mark has progressed for 3 years with no redoublement
    has_work_experience_of_3_months = False # This is a global variable to check if the lead has a work experience of 3 months
    has_work_experience_of_6_months = False # This is a global variable to check if the lead has a work experience of 6 months
    has_work_experience_of_more_than_12_months = False # This is a global variable to check if the lead has a work experience of more than 12 months
    mark_no_progression_for_2_years = False
    mark_no_progression_for_3_years = False
    rank_MP_top_10 = False
    rank_no_progression_for_2_years = False
    blank_year_1_time = False
    blank_year_2_times_and_more = False
    repeat_1_time = False
    repeat_2_times = False
    TP_subjects_validated = False 
    TP_subjects_insufficient_mark = False
    no_working_experience = False
    no_working_experience_proof = False
    def generate_courses(lead):
        lead_id = lead.id    
        report_cards = ReportCard.query.filter_by(lead_id=lead_id).all()
        report_card_subject_relation = ReportCardSubjectRelation.query.filter(ReportCardSubjectRelation.report_card_id.in_([report_card.id for report_card in report_cards])).all()
        inegible_reasons = check_inegibility_lead(lead, report_cards, report_card_subject_relation)
        #print('==HAH report_card_subject_relation len 🎀🎀 '+str(len(report_card_subject_relation)))
        if inegible_reasons:
            return {'inegible_reasons': inegible_reasons}
        else:

            valid_courses, invalid_courses = get_courses(lead, report_cards, report_card_subject_relation)
            candidate_profile_conditions = get_candidate_profile_conditions(lead, report_cards, report_card_subject_relation)
            visa_evaluation, best_conditions, worst_conditions = None, {}, {}
            if len(candidate_profile_conditions) > 0:
                visa_evaluation, best_conditions, worst_conditions = evaluation_score(lead, candidate_profile_conditions)
            #print('==HAH Avalid_courses len 🎀🎀 '+str(len(valid_courses)))
            return {'valid_courses': list(valid_courses), 'invalid_courses': list(invalid_courses), 'visa_evaluation': visa_evaluation, 'best_conditions': best_conditions, 'worst_conditions': worst_conditions}
        
    
    def check_inegibility_lead(lead, report_cards, report_card_subject_relation):
        lead_id = lead.id
        inegible_reasons = []
        nonlocal repeat_1_time, repeat_2_times 
        def validate_credits(bac_ids):
            for bac_id in bac_ids:
                validation_result = check_if_lead_has_validated_all_credits_on_complete_term(report_cards, report_card_subject_relation, bac_id)
                if validation_result:
                    inegible_reasons.append(validation_result)

        def validate_cumulative_mark(start_bac_id, end_bac_id):
            if cumulative_mark_for_the_completed_years(report_cards, start_bac_id, end_bac_id) < 10.5:
                if end_bac_id == 'bac00003':
                    inegible_reasons.append({'id': 'reas0000', 'reason': "Votre moyenne cumulée en Terminale est inférieure au seuil de 10"})
                else: 
                    bac_year_11 = get_bac_year(end_bac_id) + 11 # to not get the same reason id used in validate_credits
                    inegible_reasons.append({'id': f'reas000{bac_year_11-3}', 'reason': f'Votre moyenne cumulée jusqu\'au bac+{bac_year_11-3} est inférieure au seuil de 10'})
        if lead.bac_id in bac_validation_map:
            bac_ids, start_bac_id, end_bac_id = bac_validation_map[lead.bac_id]
            if bac_ids:
                validate_credits(bac_ids)
            validate_cumulative_mark(start_bac_id, end_bac_id)

        if has_less_than_12_in_baccalaureat(report_card_subject_relation, lead_id) and lead.bac_id <= 'bac00004':
            inegible_reasons.append({'id': 'reas0008', 'reason': "Vous avez obtenu mention Passable au baccalauréat ou alors le baccalauréat est inexistant"})

        if int(lead.number_of_repeats_n_3) > 2:
            inegible_reasons.append({'id': 'reas0009', 'reason': "Vous avez plus de 2 redoublements durant vos 3 dernières années d'étude"})
        elif int(lead.number_of_repeats_n_3) == 1:
            repeat_1_time = True
        elif int(lead.number_of_repeats_n_3) == 2:
            repeat_2_times = True
        return inegible_reasons
    
    def get_criteria():
        """Fetch all visa criteria from the database."""
        return VisaCriteria.query.all()

    def get_critieria_type_weights():
        """Fetch all criteria weights from the database."""
        critieria_type = CriteriaType.query.all()
        # Create a dictionary for quick access to weights by criteria type ID.
        return {criterion.id: criterion.weight for criterion in critieria_type}

    def evaluation_score(lead, candidate_profiles):
        # Fetch all conditions and weights.
        conditions = {criteria.id: criteria for criteria in get_criteria()}
        critieria_type_weights = get_critieria_type_weights()

        applicable_scores = []
        total_weight = 0
        weighted_sum = 0
        best_conditions = {}
        worst_conditions = {}

        # Iterate through the candidate's conditions (as a list of IDs).
        for condition_id in candidate_profiles:
            condition = conditions.get(condition_id)
            if condition:
                score = condition.score
                criteria_type_id = condition_id[:6]  # Extracting criteria type ID (e.g., "cri001")

                # Immediate return if a critical failure is detected.
                if score == 0:
                    return 0, {}, {}

                # Weighting criteria types (if needed) for a more realistic scoring.
                weight = critieria_type_weights.get(criteria_type_id, 1.0)  # Default weight is 1 if not specified.

                weighted_sum += score * weight
                total_weight += weight
                applicable_scores.append(score)

                # Track best and worst conditions for each criteria type.
                if score >= 2.5:
                    if criteria_type_id not in best_conditions or score > best_conditions[criteria_type_id].score:
                        best_conditions[criteria_type_id] = condition.as_dict()
                else:
                    if criteria_type_id not in worst_conditions or score < worst_conditions[criteria_type_id].score:
                        worst_conditions[criteria_type_id] = condition.as_dict()

        # Reorganize best_conditions and worst_conditions by score
        best_conditions = dict(sorted(best_conditions.items(), key=lambda item: item[1]['score'], reverse=True))  # High to low
        worst_conditions = dict(sorted(worst_conditions.items(), key=lambda item: item[1]['score']))  # Low to high

        # Limit best_conditions to top 5 with highest scores
        if len(best_conditions) > 5:
            best_conditions = dict(list(best_conditions.items())[:5])

        # Limit worst_conditions to top 5 with lowest scores
        if len(worst_conditions) > 5:
            worst_conditions = dict(list(worst_conditions.items())[:5])

        # If no applicable scores are found, assume a default score (e.g., 5).
        if not applicable_scores:
            return 5, best_conditions, worst_conditions

        # Calculate the final score using a weighted average.
        final_score = weighted_sum / total_weight
        lead.evaluation_score = round(final_score, 2)
        db.session.commit()

        return round(final_score, 2), best_conditions, worst_conditions

    
    def get_candidate_profile_conditions(lead, report_cards, report_card_subject_relation):

        """Todo : Changements de filière"""
        candidate_profile_conditions = []
         # I-Moyenne générale récente
        most_recent_report_card = get_most_recent_report_card(get_bac_year(lead.bac_id), report_cards)
        most_recent_average_mark = most_recent_report_card.average_mark_in_20
        if most_recent_average_mark >10.5 and most_recent_average_mark < 11:
            candidate_profile_conditions.append('co0010') # Moyenne générale < 11/20
        elif most_recent_average_mark < 12:
            candidate_profile_conditions.append('co0014') # Moyenne générale 11-12
        elif most_recent_average_mark < 13:
            candidate_profile_conditions.append('co0018') # Moyenne générale 12-13
        elif most_recent_average_mark < 14:
            candidate_profile_conditions.append('co0021') # Moyenne générale 13-14
        elif most_recent_average_mark < 15:
            candidate_profile_conditions.append('co0027') # Moyenne générale 14-15
        elif most_recent_average_mark < 16:
            candidate_profile_conditions.append('co0036') # Moyenne générale 15-16
        elif most_recent_average_mark < 17:
            candidate_profile_conditions.append('co0040')   # Moyenne générale 16-17
        elif most_recent_average_mark < 18:
            candidate_profile_conditions.append('co0047')   # Moyenne générale 17-18
        elif most_recent_average_mark < 20:
            candidate_profile_conditions.append('co0051')   # Moyenne générale > 18
        # II-Moyenne générale sur 3 ans
        if lead.bac_id in bac_validation_map:
            _, start_bac_id, end_bac_id = bac_validation_map[lead.bac_id]
            cumulative_mark = cumulative_mark_for_the_completed_years(report_cards, start_bac_id, end_bac_id)
            if cumulative_mark < 11:
                candidate_profile_conditions.append('co0011')
            elif cumulative_mark < 12:
                candidate_profile_conditions.append('co0015')
            elif cumulative_mark < 13:
                candidate_profile_conditions.append('co0019')
            elif cumulative_mark < 14:
                candidate_profile_conditions.append('co0022')
            elif cumulative_mark < 15:
                candidate_profile_conditions.append('co0028')
            elif cumulative_mark < 16:
                candidate_profile_conditions.append('co0037')
            elif cumulative_mark < 17:
                candidate_profile_conditions.append('co0041')
            elif cumulative_mark < 18:
                candidate_profile_conditions.append('co0048')
            elif cumulative_mark < 20:
                candidate_profile_conditions.append('co0052')
        # III-Moyenne matières principales
        if len(report_cards) > 1:
            average_mark_most_weighted_subjects = get_mark_most_weighted_subjects(report_cards, report_card_subject_relation)
            if average_mark_most_weighted_subjects < 11:
                candidate_profile_conditions.append('co0012')
            elif average_mark_most_weighted_subjects < 12:
                candidate_profile_conditions.append('co0016')
            elif average_mark_most_weighted_subjects < 13:
                candidate_profile_conditions.append('co0020')
            elif average_mark_most_weighted_subjects < 14:
                candidate_profile_conditions.append('co0023')
            elif average_mark_most_weighted_subjects < 15:
                candidate_profile_conditions.append('co0029')
            elif average_mark_most_weighted_subjects < 16:
                candidate_profile_conditions.append('co0038')
            elif average_mark_most_weighted_subjects < 17:
                candidate_profile_conditions.append('co0042')
            elif average_mark_most_weighted_subjects < 18:
                candidate_profile_conditions.append('co0049')
            elif average_mark_most_weighted_subjects < 20:
                candidate_profile_conditions.append('co0053')
        # IV-Performances stables sur 2 ans/3 ans
        if len(report_cards) > 1 and average_mark_most_weighted_subjects< 14:
            if not mark_has_progressed_for_3_years_with_no_redoublement:
                candidate_profile_conditions.append('co0017')
            elif len(report_cards) > 2 and not mark_has_progressed_for_2_years_with_no_redoublement:
                candidate_profile_conditions.append('co0013')
                
        # V-Progression continue sur 3 ans
        if len(report_cards) > 2:
            if mark_has_progressed_for_3_years_with_no_redoublement and most_recent_average_mark < 14:
                candidate_profile_conditions.append('co0024')
            elif mark_has_progressed_for_3_years_with_no_redoublement and most_recent_average_mark < 15:
                candidate_profile_conditions.append('co0030')
            elif mark_has_progressed_for_3_years_with_no_redoublement and most_recent_average_mark < 16:
                candidate_profile_conditions.append('co0039')
            elif mark_has_progressed_for_3_years_with_no_redoublement and most_recent_average_mark < 17:
                candidate_profile_conditions.append('co0043')
            elif mark_has_progressed_for_3_years_with_no_redoublement and most_recent_average_mark < 18:
                candidate_profile_conditions.append('co0049')
            elif mark_has_progressed_for_3_years_with_no_redoublement and most_recent_average_mark < 20:
                candidate_profile_conditions.append('co0050')
        # VI-Niveau de français
        if lead.french_level:
            if lead.french_level == 'B2':
                candidate_profile_conditions.append('co0025')
            elif lead.french_level >= 'C1':
                candidate_profile_conditions.append('co0032')
        # VII-Expérience professionnelle

        if has_work_experience_of_more_than_12_months:
            candidate_profile_conditions.append('co0045')
        elif has_work_experience_of_6_months:
            candidate_profile_conditions.append('co0035')    
        elif has_work_experience_of_3_months:
            candidate_profile_conditions.append('co0026')  

        # VIII-Distinction dans les matières principales
        award = Award.query.filter_by(lead_id=lead.id).first()
        if award:
            candidate_profile_conditions.append('co0046')
        # IX-Séjours en France/Schengen
        travaling = Traveling.query.filter_by(lead_id=lead.id).first()
        if travaling:
            candidate_profile_conditions.append('co0033')
        # X-Niveau d'anglais
        if lead.english_level and lead.english_level > 'B1' :
            candidate_profile_conditions.append('co0034')

        # XI-Classement
        most_recent_available_report_card_second = get_most_recent_report_card(get_bac_year(most_recent_report_card.bac_id) - 1, report_cards) if most_recent_report_card else None

        if len(report_cards) > 1:
            if most_recent_report_card.overall_rank and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank):
                if most_recent_report_card.overall_rank > 20 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank > 20):
                    candidate_profile_conditions.append('co0055')
                elif most_recent_report_card.overall_rank > 15 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank > 15):
                    candidate_profile_conditions.append('co0056')
                elif most_recent_report_card.overall_rank > 10 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank > 10):
                    candidate_profile_conditions.append('co0057')
                elif most_recent_report_card.overall_rank > 5 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank > 5):
                    candidate_profile_conditions.append('co0058')
                elif most_recent_report_card.overall_rank > 3 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank > 3):
                    candidate_profile_conditions.append('co0059')
                elif most_recent_report_card.overall_rank == 3 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank == 3):
                    candidate_profile_conditions.append('co0060')
                elif most_recent_report_card.overall_rank == 2 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank == 2):
                    candidate_profile_conditions.append('co0061')
                elif most_recent_report_card.overall_rank == 1 and (most_recent_available_report_card_second is None or most_recent_available_report_card_second.overall_rank == 1):
                    candidate_profile_conditions.append('co0062')
        # XII-Mention au baccalauréat
        baccalaureat_report_card = next((rc for rc in report_cards if rc.baccalaureat_average_mark_in_20 and rc.baccalaureat_average_mark_in_20 > 0), None)
        baccalaureat_average_mark = None
        if baccalaureat_report_card:
            baccalaureat_average_mark = baccalaureat_report_card.baccalaureat_average_mark_in_20
        if baccalaureat_average_mark :
            if baccalaureat_average_mark >= 17:
                candidate_profile_conditions.append('co0054') 
            elif baccalaureat_average_mark >= 16  :
                candidate_profile_conditions.append('co0044')
            elif baccalaureat_average_mark >= 14:
                candidate_profile_conditions.append('co0031')

        # XIII- Extra conditions 
        if mark_no_progression_for_3_years:
            if cumulative_mark<13.5:
                candidate_profile_conditions.append('co0063')
            elif cumulative_mark<14:
                candidate_profile_conditions.append('co0078')
            elif cumulative_mark<15:
                candidate_profile_conditions.append('co0077')
            elif cumulative_mark<16:
                candidate_profile_conditions.append('co0076')
            elif cumulative_mark<=20:
                candidate_profile_conditions.append('co0075')
        elif mark_no_progression_for_2_years:
            if cumulative_mark<16:
                candidate_profile_conditions.append('co0063')
            else:
                candidate_profile_conditions.append('co0079')
            candidate_profile_conditions.append('co0064')
        if rank_MP_top_10:
            candidate_profile_conditions.append('co0065')
        if rank_no_progression_for_2_years:
            if cumulative_mark<16:
                candidate_profile_conditions.append('co0066')
            else:
                candidate_profile_conditions.append('co0080')
        if blank_year_2_times_and_more:
            candidate_profile_conditions.append('co0068')
        elif blank_year_1_time:
            candidate_profile_conditions.append('co0067')
        if repeat_2_times:
            candidate_profile_conditions.append('co0070')
        elif repeat_1_time:
            candidate_profile_conditions.append('co0069')
        if TP_subjects_validated:
            candidate_profile_conditions.append('co0071')
        elif TP_subjects_insufficient_mark:
            candidate_profile_conditions.append('co0072')
        if no_working_experience:
            candidate_profile_conditions.append('co0073')
        elif no_working_experience_proof:
            candidate_profile_conditions.append('co0074')

        return candidate_profile_conditions
      
    def get_mark_most_weighted_subjects(report_cards, report_card_subject_relation):
        """Get the general average mark of the 3 most weighted subjects per year of the last 2 available years"""
        most_weighted_subjects = []
        for report_card in report_cards:
            report_card_subjects = [subject for subject in report_card_subject_relation if subject.report_card_id == report_card.id and not subject.is_baccalaureat]
            if not report_card_subjects:
                continue
            most_weighted_subjects += sorted(report_card_subjects, key=lambda subject: subject.weight, reverse=True)[:3]
        total_weight = sum(subject.weight for subject in most_weighted_subjects)
        total_mark = sum(subject.mark_in_20 * subject.weight for subject in most_weighted_subjects)
        return total_mark / total_weight if total_weight > 0 else 0
    

    def get_bac_year(bac_id):
        return int(bac_id[-2:])
    
    def check_if_lead_has_validated_all_credits_on_complete_term(report_cards, report_card_subject_relation, bac_id):     
        if university_term_is_complete(report_cards, bac_id) and hasnt_validated_all_credits(report_cards, report_card_subject_relation, bac_id):
                bac_year = get_bac_year(bac_id)
                return {'id': f'reas000{bac_year-3}', 'reason': f'Vous avez une ou plusieurs dettes de crédit en bac+{bac_year-3}'}
        return None
      
    def hasnt_validated_all_credits(report_cards, report_card_subject_relation, bac_id):
        report_card = next((rc for rc in report_cards if rc.bac_id == bac_id), None)
        if not report_card:
            return False  # If no report card exists, assume credits are not validated

        report_card_subjects = [subject for subject in report_card_subject_relation if subject.report_card_id == report_card.id and not subject.is_baccalaureat]
        if not report_card_subjects:
            return False  # If no subjects exist, assume credits are not validated

        total_weight = sum(subject.weight for subject in report_card_subjects if subject.mark_in_20 >= 10)
        return total_weight < 60
    
    def university_term_is_complete(report_cards,  bac_id):
        number_of_valid_terms = 2
        report_card = next((rc for rc in report_cards if rc.bac_id == bac_id), None)
        if not report_card:
            return False
        valid_term_count = sum(1 for term in range(1, 4) if getattr(report_card, f'school_term{term}_average_mark_in_20') is not None)
        #print('==HAH valid_term_count 🎀🎀 '+str(valid_term_count))
        return valid_term_count >= number_of_valid_terms
    
    def has_less_than_12_in_baccalaureat(report_card_subject_relation, lead_id):
        baccalaureat_subjects = [subject for subject in report_card_subject_relation if subject.report_card.lead_id == lead_id and subject.is_baccalaureat]
        if not baccalaureat_subjects:
            return False
        total_marks = sum(subject.mark_in_20 for subject in baccalaureat_subjects)
        average_mark = total_marks / len(baccalaureat_subjects)
        return average_mark < 12

    def cumulative_mark_for_the_completed_years(report_cards_all, start_bac_id, end_bac_id):
        report_cards = [rc for rc in report_cards_all if start_bac_id <= rc.bac_id <= end_bac_id]
        total_marks = sum(report_card.average_mark_in_20 for report_card in report_cards)
        return total_marks / len(report_cards) if report_cards else 0
    
    def get_most_recent_report_card( bac_year,report_cards):
        for year_offset in range(3):
            bac_id = f'bac0000{bac_year - year_offset}'
            report_card = next((rc for rc in report_cards if rc.bac_id == bac_id), None)
            if report_card:
                return report_card
        return None
    
    def get_courses(lead, report_cards, report_card_subjects):
        lead_id = lead.id
        bac_id = lead.bac_id
        initial_courses = set()
        valid_courses = set()
        invalid_courses = []

        # Determine initial courses based on BAC level
        level_filter = Course.level_id >= 'lev0013' if bac_id > 'bac00005' or (bac_id == 'bac00006' and university_term_is_complete(lead_id, bac_id)) else Course.level_id < 'lev0013'
        initial_courses = Course.query.filter(
            level_filter,
            Course.id.isnot(None),
            Course.id != ""
        ).all()
        #start_time = time.time()

        # Your existing code here

        #loading_time = time.time() - start_time
        #print(f"Loading time: {loading_time:.2f} seconds")
        # Get the most recent BAC and report card details
        most_recent_bac_id = max(rc.bac_id for rc in report_cards)
        most_recent_bac_year = get_bac_year(most_recent_bac_id)
        most_recent_available_report_card_first = get_most_recent_report_card(most_recent_bac_year, report_cards)
        most_recent_available_report_card_second = get_most_recent_report_card(get_bac_year(most_recent_available_report_card_first.bac_id) - 1, report_cards) if most_recent_available_report_card_first else None

        #loading_time = time.time() - start_time
        #print(f"Loading time most_recent_report_card: {loading_time:.2f} seconds")
        # Fetch lead and course-related data
        lead_level_value_relation = LeadLevelValueRelation.query.filter_by(lead_id=lead_id).first()
        lead_subject_relation = LeadSubjectRelation.query.filter_by(lead_id=lead_id).all()
        course_subject_relation = CourseSubjectRelation.query.filter(
            CourseSubjectRelation.course_id.in_([course.id for course in initial_courses])
        ).all()

        # Update valid courses based on criteria if BAC level is higher than a threshold
        if bac_id > 'bac00003':
            valid_courses.update(get_courses_where_course_names_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses))
            course_level_value_relation = CourseLevelRelation.query.filter(
                CourseLevelRelation.course_id.in_([course.id for course in valid_courses])
            ).all()
            valid_courses.update(get_courses_where_level_values_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses, course_level_value_relation))
        #loading_time = time.time() - start_time
        #print(f"Loading time get_courses_where_level_values_are_similar_to_lead_degree_name: {loading_time:.2f} seconds")

        valid_courses.update(get_all_courses_from_lead_subject_relation(lead_subject_relation, course_subject_relation))
        #loading_time = time.time() - start_time
        # Remove course_subject_relation records in course_subject_relation where csr.course_id is in valid_courses
        course_subject_relation = [csr for csr in course_subject_relation if csr.course_id not in valid_courses]

        #print(f"Loading time get_all_courses_from_lead_subject_relation: {loading_time:.2f} seconds")
        valid_courses.update(get_courses_where_subjects_are_similar_to_lead_external_subjects(
            report_card_subjects, valid_courses, most_recent_available_report_card_first,
            most_recent_available_report_card_second, course_subject_relation
        ))
        #loading_time = time.time() - start_time
        #print(f"Loading time get_courses_where_subjects_are_similar_to_lead_external_subjects: {loading_time:.2f} seconds")
        # Filter course_subject_relation by valid courses to optimize subsequent operations
        valid_course_ids = {course.id for course in valid_courses}
        course_subject_relation = [csr for csr in course_subject_relation if csr.course_id in valid_course_ids]

        # Additional queries and processes if BAC level is lower than or equal to the threshold
        if bac_id <= 'bac00003':
            course_level_value_relation = CourseLevelRelation.query.filter(
                CourseLevelRelation.course_id.in_(valid_course_ids)
            ).all()

        work_experience = WorkExperience.query.filter_by(lead_id=lead_id).first()

        # Apply exclusion and purging criteria
        exclude_courses_from_course_criteria(lead, work_experience, valid_courses, invalid_courses, report_cards)
        course_level_value_relation = CourseLevelRelation.query.filter(
            CourseLevelRelation.course_id.in_(valid_course_ids)
        ).all()
        # make sure that in invalid_courses, for each reason, we have maximum 5 courses
        
        purge_courses_from_course_level_value_relation(lead, report_cards, valid_courses, invalid_courses, course_level_value_relation, lead_level_value_relation)
        purge_courses_from_course_subject_relation(report_cards, report_card_subjects, valid_courses, invalid_courses, course_subject_relation)

        valid_courses = reorder_valid_courses_by_priority(valid_courses, lead_level_value_relation, lead_subject_relation, course_level_value_relation, course_subject_relation, report_card_subjects)
        #loading_time = time.time() - start_time
        #print(f"Loading time reorder_valid_courses_by_priority: {loading_time:.2f} seconds")
        # Remove invalid_courses items with empty courses
        invalid_courses = [item for item in invalid_courses if item['courses']]
        invalid_courses = limit_courses_per_reason(invalid_courses)
        # Convert courses in invalid_courses to dictionary format
        for invalid_course in invalid_courses:
            invalid_course['courses'] = [course.as_dict() for course in invalid_course['courses']]

        return [course.as_dict() for course in valid_courses], invalid_courses[:5]

          
    def get_courses_where_course_names_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses):
        """
        Find courses where course names or titles are similar to the lead's degree name.
        """
        target_name = lead_level_value_relation.external_degree.name

        # Use list comprehension with early filtering
        return get_similar_courses(
            initial_courses,
            target_name,
            lambda course: course.name if course.name else course.title
        )

    def get_courses_where_level_values_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses, course_level_value_relation):
        print('get_courses_where_level_values_are_similar_to_lead_degree_name xxx 🎀 '+str(len(course_level_value_relation))+' '+str(len(initial_courses)))
        """
        Find courses where the course's level values are similar to the lead's degree name.
        """
        target_name = lead_level_value_relation.external_degree.name
        course_relation_map = {
            relation.course_id: relation.level_value.name for relation in course_level_value_relation
        }

        # Lambda function uses precomputed map for faster access
        return get_similar_courses(
            initial_courses,
            target_name,
            lambda course: course_relation_map.get(course.id)
        )

    def get_similar_courses(courses, target_name, attribute_func):
        """
        Calculate similarities between courses and the target name, and return top 50 courses.
        """
        similarity_cache = {}

        # Filter courses that have valid attributes and cache similarities
        keywords_to_remove = [
            'licence', 'master', 'doctorat', 'professionnelle', 'bac', 'baccalauréat', 'BTS', 'brevet', 'ingénieur', 
            'DUT', 'DEUG', 'CAP', 'BEP', 'DAEU', 'prépa', 'formation', 'diplôme', 'mention', 'universitaire', 'école', 
            'académique', 'spécialité', 'option', 'filière', 'cycle', 'certificat', 'licence pro', 'master pro', 'maîtrise',
            'DEA', 'DESS', 'grande école', 'post-doctorat', 'post-bac', 'post-master', 'CNAM', 'ENS', 'ENSA', 'HEC', 'IEP', 
            'IUT', 'ENAC', 'ENSTA', 'ENA', 'attestation', 'supérieur', 'professionnel', 'technologie', 'études', 'générales',
            'aptitude', 'professionnelles', 'accès', 'universitaires', 'approfondies', 'supérieures', 'spécialisées', 'sciences',
            'technicien', 'institut', 'hautes', 'normale', 'supérieure', 'nationale', 'architecture', 'science',
            'conservatoire', 'arts', 'métiers', 'civile', 'techniques', 'avancées',
        ]

        symbols_to_remove = ["'", '"', '$', '.', ',', '!', '?', ':', ';']
        single_characters_to_remove = list("abcdefghijklmnopqrstuvwxyz")

        def remove_keywords(text):
            for keyword in keywords_to_remove:
             text = re.sub(re.escape(keyword), '', text, flags=re.IGNORECASE)
            for symbol in symbols_to_remove:
             text = text.replace(symbol, ' ')
            for char in single_characters_to_remove:
             text = re.sub(r'\b' + re.escape(char) + r'\b', '', text, flags=re.IGNORECASE)
            return text.strip()

        similarities = [
            (course, similarity_cache.setdefault(course, Helper.cosine_sim(remove_keywords(attr), remove_keywords(target_name))))
            for course in courses if (attr := attribute_func(course)) is not None and Helper.cosine_sim(remove_keywords(attr), remove_keywords(target_name)) > 0.15
        ]
        # for course, similarity in similarities:
        #     print(f"xxxx course.id: {course.id},  attr: {remove_keywords(attribute_func(course))},😎😎 target_name: {remove_keywords(target_name)} similarity: {similarity}")
        #print('xxxx similarities:', [(course.id, sim) for course, sim in similarities])
        #print('xxxx target_name:', target_name)
        #print('xxxx attribute values:', [attribute_func(course) for course in courses if attribute_func(course) is not None])
        # Sort by similarity in descending order and return the top 50 courses
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [course for course, _ in similarities[:50]]

    def get_all_courses_from_lead_subject_relation(lead_subject_relation, course_subject_relations):
        # Use a set for faster lookups
        subject_ids = {relation.subject_id for relation in lead_subject_relation if relation.subject_id}

        # Filter the matching courses using the set
        matching_courses = [
            course_relation.course for course_relation in course_subject_relations
            if course_relation.subject_id in subject_ids
        ]

        return matching_courses

    def get_courses_where_subjects_are_similar_to_lead_external_subjects(
            report_card_subjects, initial_courses, 
            most_recent_available_report_card_first, 
            most_recent_available_report_card_second, 
            course_subject_relation):
        #print('xxx initial_courses 🤷‍♂️ '+str(len(initial_courses))+' - '+str(len(course_subject_relation)))
        # Step 1: Create a set of target subject names with weights (top 3 weights)
        target_subject_names_with_weight = []

        def add_target_subject_names(report_card):
            if report_card:
                # Get subjects and weights from the report card, filtering valid ones
                report_card_subject_relation = [
                    (relation.subject.name, relation.weight) for relation in report_card_subjects 
                    if relation.report_card_id == report_card.id and relation.subject_id and relation.subject.name
                ] + [
                    (relation.external_subject.name, relation.weight) for relation in report_card_subjects 
                    if relation.report_card_id == report_card.id and relation.external_subject_id and relation.external_subject.name
                ]
                
                # Sort by weight (desc) and take the top 3
                top_subjects = sorted(report_card_subject_relation, key=lambda x: x[1], reverse=True)[:3]
                
                # Add the top subject names with weights to target_subject_names_with_weight
                target_subject_names_with_weight.extend([{'name': name, 'weight': weight} for name, weight in top_subjects])

        # Add subjects from both report cards
        add_target_subject_names(most_recent_available_report_card_first)
        #print('most_recent_available_report_card_first 🎀 '+str(most_recent_available_report_card_first.bac_id))
        #print('most_recent_available_report_card_second 🎀 '+str(most_recent_available_report_card_second.bac_id))
        #if not (most_recent_available_report_card_first.bac_id> 'bac00003' and most_recent_available_report_card_second.bac_id<= 'bac00003'):
        add_target_subject_names(most_recent_available_report_card_second)
        #print('target_subject_names_with_weight 🎀', target_subject_names_with_weight)
        # Step 2: Build course_subject_groups from course_subject_relation
        course_subject_groups = defaultdict(list)

        for course_relation in course_subject_relation:
            course_id = course_relation.course_id
            subject = course_relation.subject
            if subject and subject.name and not subject.is_tech:
                course_subject_groups[course_id].append(subject.name)

        # Step 3: Compute similarity between courses and target subjects
        course_similarities = {}

        for course_id, course_subjects in course_subject_groups.items():
            total_similarity = 0
            for target_subject in target_subject_names_with_weight:
                target_name = target_subject['name']
                target_weight = target_subject['weight']
                for course_subject in course_subjects:
                    # Compute cosine similarity between the course subject and target subject
                    #if course_id == 'crs0335':
                    #    print(f'<========> 🥵 {course_id} == course_subject: {course_subject} -- target_name: {target_name}')
                    similarity = Helper.cosine_sim(course_subject, target_name)
                    if similarity > 0:
                        # Add weighted similarity
                        total_similarity += similarity * target_weight
            
            # Store total similarity for each course
            if total_similarity > 0:
                course_similarities[course_id] = total_similarity

        # Step 4: Sort courses by similarity (highest first)
        sorted_courses_by_similarity = sorted(course_similarities.items(), key=lambda x: x[1], reverse=True)

        # Step 5: Retrieve the actual top courses based on sorted similarity
        top_courses = [course for course in initial_courses if course.id in dict(sorted_courses_by_similarity).keys()]
        print('xxx top_courses 🤷‍♂️ '+str(len(top_courses)))
        # Return only the first 20 top courses
        return top_courses[:20]

    def limit_courses_per_reason(invalid_courses, max_courses=5):
        limited_courses = []
        
        for category in invalid_courses:
            # Create a new dictionary with the same reason
            limited_category = {
                'reason': category['reason'],
                'courses': category['courses'][:max_courses]  # Take only first 5 courses
            }
            limited_courses.append(limited_category)
        
        return limited_courses
    
    def add_invalid_course_reason(reason, invalid_courses):
        invalid_courses_by_reason = next((item for item in invalid_courses if item['reason'] == reason), None)
        if not invalid_courses_by_reason:
            invalid_courses_by_reason = {'reason': reason, 'courses': []}
            invalid_courses.append(invalid_courses_by_reason)
        return invalid_courses_by_reason
    
    def exclude_courses_from_course_criteria(lead, work_experience, valid_courses, invalid_courses, report_cards):
        lead_id = lead.id
        nonlocal no_working_experience

        def remove_invalid_courses(valid_courses, invalid_courses_by_reason, levels):
            nonlocal no_working_experience, no_working_experience_proof

            # Ensure valid_courses is iterable, if not return early
            if not isinstance(valid_courses, (list, set, tuple)):
                return

            # Find invalid courses that match the levels and remove them from valid_courses
            invalid_courses = {course for course in valid_courses if course.professional_experience_requirement_level in levels}

            # Update flags based on professional experience requirement levels
            no_working_experience = any(course.professional_experience_requirement_level == 1 for course in invalid_courses)
            no_working_experience_proof = any(course.professional_experience_requirement_level == 0.5 for course in invalid_courses)

            # Add invalid courses to invalid_courses_by_reason
            invalid_courses_by_reason['courses'].extend(invalid_courses)

            # Remove invalid courses from valid_courses
            valid_courses -= invalid_courses  # Use set difference to remove invalid courses from the set

            # Reset no_working_experience if no_working_experience_proof is set
            if no_working_experience_proof:
                no_working_experience = False


        def add_invalid_course_reason(reason, invalid_courses):
            invalid_courses_by_reason = next((item for item in invalid_courses if item['reason'] == reason), None)
            if not invalid_courses_by_reason:
                invalid_courses_by_reason = {'reason': reason, 'courses': []}
                invalid_courses.append(invalid_courses_by_reason)
            return invalid_courses_by_reason

        def check_work_experience():
            nonlocal has_work_experience_of_3_months, has_work_experience_of_6_months, has_work_experience_of_more_than_12_months
            if work_experience and not work_experience.can_prove:
                reason = 'Vous n\'avez pas pu justifier votre expérience professionnelle'
                #no_working_experience_proof = True
                invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                remove_invalid_courses(valid_courses, invalid_courses_by_reason, [1])

            if not work_experience:
                reason = 'Ces formations nécessitent une expérience professionnelle'
                #no_working_experience = True
                invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                remove_invalid_courses(valid_courses, invalid_courses_by_reason, [0.5, 1])
            elif work_experience and work_experience.start_date: 
                if work_experience.end_date is not None:
                    experience_duration = (work_experience.end_date - work_experience.start_date).days / 30  # Convert days to months
                    if experience_duration >= 3:
                        has_work_experience_of_3_months = True
                    if experience_duration >= 6:
                        has_work_experience_of_6_months = True
                    if experience_duration > 12:
                        has_work_experience_of_more_than_12_months = True
                else: 
                    has_work_experience_of_more_than_12_months = True

        def check_language_requirements():
            language_requirements = [
                ('french_level', 'Votre niveau de français est insuffisant pour ces formations'),
                ('english_level', 'Votre niveau d\'anglais est insuffisant pour ces formations'),
                ('other_spoken_language_level', 'Votre niveau de la langue étrangère est insuffisant pour ces formations')
            ]

            for attr, reason in language_requirements:
                level = getattr(lead, attr, None)
                if level:
                    invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                    for course in list(valid_courses):
                        course_level = getattr(course, attr, None)
                        if course_level and course_level.strip() and level < course_level:
                            valid_courses.remove(course)
                            invalid_courses_by_reason['courses'].append(course)

        def check_progression():
            nonlocal mark_has_progressed_for_2_years_with_no_redoublement, mark_has_progressed_for_3_years_with_no_redoublement, mark_no_progression_for_2_years
            nonlocal mark_no_progression_for_3_years, rank_no_progression_for_2_years, repeat_1_time, repeat_2_times
            bac_map = {
                'bac00010': ['bac00010', 'bac00009', 'bac00008'],
                'bac00009': ['bac00009', 'bac00008', 'bac00007'],
                'bac00008': ['bac00008', 'bac00007', 'bac00006'],
                'bac00007': ['bac00007', 'bac00006', 'bac00005'],
                'bac00006': ['bac00006', 'bac00005', 'bac00004'],
                'bac00005': ['bac00005', 'bac00004', 'bac00003'],
                'bac00004': ['bac00004', 'bac00003', 'bac00002'],
                'bac00003': ['bac00003', 'bac00002', 'bac00001']
            }

            def has_progressed_for_years(years):
                if lead.bac_id in bac_map:
                    bac_ids = bac_map[lead.bac_id]
                    for i in range((len(bac_ids)+1) - years):
                        current_report_card = next((rc for rc in report_cards if rc.bac_id == lead.bac_id), None)
                        previous_report_card = next((rc for rc in report_cards if rc.bac_id == bac_ids[i + 1]), None)
                        if years == 2:
                            if current_report_card and previous_report_card:
                                if (current_report_card.average_mark_in_20 > previous_report_card.average_mark_in_20 and
                                    current_report_card.average_mark_in_20 > 10 and previous_report_card.average_mark_in_20 > 10):
                                    return True
                        elif years == 3:
                            earlier_report_card = next((rc for rc in report_cards if rc.bac_id == bac_ids[i + 2]), None)
                            if current_report_card and previous_report_card and earlier_report_card:
                                if (current_report_card.average_mark_in_20 > previous_report_card.average_mark_in_20 and
                                    previous_report_card.average_mark_in_20 > earlier_report_card.average_mark_in_20 and
                                    current_report_card.average_mark_in_20 > 10 and previous_report_card.average_mark_in_20 > 10 and
                                    earlier_report_card.average_mark_in_20 > 10):
                                    return True
                return False

            mark_has_progressed_for_2_years = has_progressed_for_years(2)
            mark_has_progressed_for_3_years = has_progressed_for_years(3)

            reason = 'Vous n\'avez pas progressé entre deux années consécutives'
            if mark_has_progressed_for_2_years and lead.number_of_repeats_n_3 > 0:
                if lead.number_of_repeats_n_3 > 1:
                    reason = "Malgré une progression de vos notes, vous avez redoublé trop de fois pour pouvoir intégrer ces formations"
                    repeat_2_times = True
                    mark_has_progressed_for_2_years = False
                elif lead.number_of_repeats_n_3 == 1:
                    repeat_1_time = True
            if mark_has_progressed_for_2_years and lead.number_of_repeats_n_3 == 0:
                mark_has_progressed_for_2_years_with_no_redoublement = True
            if mark_has_progressed_for_3_years and lead.number_of_repeats_n_3 == 0:
                mark_has_progressed_for_3_years_with_no_redoublement = True

            if not mark_has_progressed_for_2_years:
                mark_no_progression_for_2_years = True
                invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                for course in list(valid_courses):
                    if course.is_progression_mandatory:
                        valid_courses.remove(course)
                        invalid_courses_by_reason['courses'].append(course)

            if not mark_has_progressed_for_3_years:
                reason = 'Vous n\'avez pas progressé entre trois années consécutives'
                mark_no_progression_for_2_years = False
                mark_no_progression_for_3_years = True
                invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                for course in list(valid_courses):
                    if course.check_grade_since_n3:
                        valid_courses.remove(course)
                        invalid_courses_by_reason['courses'].append(course)

        def check_ranking():
            nonlocal rank_no_progression_for_2_years
            bac_map = {
                'bac00010': ['bac00010', 'bac00009', 'bac00008'],
                'bac00009': ['bac00009', 'bac00008', 'bac00007'],
                'bac00008': ['bac00008', 'bac00007', 'bac00006'],
                'bac00007': ['bac00007', 'bac00006', 'bac00005'],
                'bac00006': ['bac00006', 'bac00005', 'bac00004'],
                'bac00005': ['bac00005', 'bac00004', 'bac00003'],
                'bac00004': ['bac00004', 'bac00003', 'bac00002'],
                'bac00003': ['bac00003', 'bac00002', 'bac00001']
            }

            def has_rank_progressed_for_years(years):
                if lead.bac_id in bac_map:
                    bac_ids = bac_map[lead.bac_id]
                    for i in range(len(bac_ids) - years):
                        current_report_card = next((rc for rc in report_cards if rc.bac_id == bac_ids[i]), None)
                        previous_report_card = next((rc for rc in report_cards if rc.bac_id == bac_ids[i + 1]), None)
                        if current_report_card and previous_report_card:
                            if current_report_card.overall_rank and previous_report_card.overall_rank:
                                if current_report_card.overall_rank <= 10 and previous_report_card.overall_rank <= 10:
                                    if current_report_card.overall_rank < previous_report_card.overall_rank:
                                        return True
                return False

            rank_has_progressed_for_2_years = has_rank_progressed_for_years(2)

            if not rank_has_progressed_for_2_years:
                reason = 'Votre rang n\'a pas évolué entre deux années consécutives'
                rank_no_progression_for_2_years = True
                invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                for course in list(valid_courses):
                    if course.is_ranking_mandatory:
                        valid_courses.remove(course)
                        invalid_courses_by_reason['courses'].append(course)

        check_work_experience()
        check_language_requirements()
        check_progression()
        check_ranking()

        return valid_courses, invalid_courses

    def purge_courses_from_course_level_value_relation(lead, report_cards, valid_courses, invalid_courses, course_level_value_relation, lead_level_relation):
        most_recent_available_report_card = get_most_recent_report_card(get_bac_year(lead.bac_id), report_cards)

        def get_average_mark(bac_id):
            report_card = next((rc for rc in report_cards if rc.bac_id == bac_id), None)
            return report_card.average_mark_in_20 if report_card and report_card.average_mark_in_20 is not None else 0

        recent_mark = most_recent_available_report_card.average_mark_in_20 if most_recent_available_report_card else 0
        invalid_courses_by_reason = add_invalid_course_reason("Votre moyenne récente est inférieure au score minimum requis.", invalid_courses)

        for course_level_value in course_level_value_relation:
            if course_level_value.minimum_score:
                if lead_level_relation is not None:
                    level_value_similarity = Helper.cosine_sim(course_level_value.level_value.name, lead_level_relation.level_value.name)
                    if course_level_value.level_value_id == lead_level_relation.level_value_id or level_value_similarity >= 0.25:
                        if recent_mark < course_level_value.minimum_score:
                            if (
                                (course_level_value.is_L1 and get_average_mark('bac00004') < course_level_value.minimum_score) or
                                (course_level_value.is_L2 and get_average_mark('bac00005') < course_level_value.minimum_score) or
                                (course_level_value.is_L3 and get_average_mark('bac00006') < course_level_value.minimum_score)
                            ):
                                valid_courses = [course for course in valid_courses if course.id != course_level_value.course_id]
                                invalid_courses_by_reason['courses'].append(course_level_value.course)

        return valid_courses, invalid_courses

    def purge_courses_from_course_subject_relation(report_cards, report_card_subjects, valid_courses, invalid_courses, course_subject_relation):
        #invalid_courses_by_reason = {'reason': "Votre note dans certaines matières est inférieure au score minimum requis.", 'courses': []}

        # Create a dictionary for quick lookup of report card subjects by subject_id
        report_card_subject_dict = {rel.subject_id: rel for rel in report_card_subjects}

        for subject_relation in course_subject_relation:
            if subject_relation.minimum_score and not subject_relation.subject.is_tech:
                report_card_subject = report_card_subject_dict.get(subject_relation.subject_id)
                if report_card_subject and report_card_subject.mark_in_20 < subject_relation.minimum_score:
                    course = next((course for course in list(valid_courses) if course.id == subject_relation.course_id), None)
                    if course:
                        valid_courses.remove(course)
                        reason = f"Votre note en {(report_card_subject.subject_id and report_card_subject.subject.name.lower()) or (report_card_subject.external_subject_id and report_card_subject.external_subject.name.lower())} est inférieure au minimum requis pour cette formation."
                        invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                        invalid_courses_by_reason['courses'].append(course)

        new_course_subject_relations = [relation for relation in course_subject_relation if relation.course_id in [course.id for course in list(valid_courses)] and relation.subject.is_tech]
        nonlocal rank_MP_top_10, TP_subjects_insufficient_mark, TP_subjects_validated
        for new_subject_relation in new_course_subject_relations:
            if new_subject_relation.subject_id == 'suj0212':  # MP
                for report_card in report_cards:
                    top_subjects = sorted(
                        [rel for rel in report_card_subjects if rel.report_card_id == report_card.id],
                        key=lambda x: x.weight, reverse=True
                    )[:4]
                    if any(subject.mark_in_20 < 14 for subject in top_subjects) and not all(
                            top_subjects[i].mark_in_20 > top_subjects[i + 1].mark_in_20 for i in range(len(top_subjects) - 1)
                    ):                      
                        if new_subject_relation.course_id and new_subject_relation.course in valid_courses:
                            reason = "Votre performance dans les matières principales n'est pas suffisante."
                            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                            valid_courses.remove(new_subject_relation.course)
                            invalid_courses_by_reason['courses'].append(new_subject_relation.course)

            if new_subject_relation.subject_id == 'suj0382':  # Moyenne baccalaureat < 13
                baccalaureat_subjects = [subject for subject in report_card_subjects if subject.is_baccalaureat]
                average_mark = sum(subject.mark_in_20 for subject in baccalaureat_subjects) / len(baccalaureat_subjects)
                if average_mark < 13:
                    if new_subject_relation.course_id and new_subject_relation.course in valid_courses:
                        reason = "Votre moyenne au baccalauréat est inférieure à 13."
                        invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                        valid_courses.remove(new_subject_relation.course)
                        invalid_courses_by_reason['courses'].append(new_subject_relation.course)

            if new_subject_relation.subject_id == 'suj0403':  # Moyenne generale
                average_subject_mark_in_20_per_term = {1: 0, 2: 0, 3: 0}
                term_counts = {1: 0, 2: 0, 3: 0}
                for rel in report_card_subjects:
                    for term in range(1, 4):
                        if rel.school_term == term and (
                                rel.subject_id == new_subject_relation.subject_id or
                                (rel.subject_id and new_subject_relation.subject_id and Helper.cosine_sim(new_subject_relation.subject.name, rel.subject.name) >= 0.25)
                        ):
                            average_subject_mark_in_20_per_term[term] += rel.mark_in_20 * rel.weight
                            term_counts[term] += rel.weight
                for term in range(1, 4):
                    if term_counts[term] > 0:
                        average_subject_mark_in_20_per_term[term] /= term_counts[term]
                        if average_subject_mark_in_20_per_term[term] < 12:
                            if new_subject_relation.course_id and new_subject_relation.course in valid_courses:
                                reason = f"Votre moyenne dans les matières principales au cours du {new_subject_relation.report_card.academic_year_organization.name} {term} de {new_subject_relation.report_card.school_year.name} est inférieure à 12."
                                invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                                valid_courses.remove(new_subject_relation.course)
                                invalid_courses_by_reason['courses'].append(new_subject_relation.course)

            if new_subject_relation.subject_id == 'suj0405':  # Top 10
                for report_card_subject_relation in report_card_subjects:
                    if (
                            report_card_subject_relation.subject_id == new_subject_relation.subject_id or
                            Helper.cosine_sim(new_subject_relation.subject.name, report_card_subject_relation.subject.name) >= 0.25
                    ) and report_card_subject_relation.rank > 10:
                        if new_subject_relation.course_id and new_subject_relation.course in valid_courses:
                            reason = "Votre rang dans les matières principales est supérieur à 10."
                            rank_MP_top_10 = True
                            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                            valid_courses.remove(new_subject_relation.course)
                            invalid_courses_by_reason['courses'].append(new_subject_relation.course)

        practical_subjects = [subject for subject in report_card_subjects if subject.is_pratical_subject]
        if practical_subjects:
            average_mark = sum(subject.mark_in_20 for subject in practical_subjects) / len(practical_subjects)
            if average_mark < 12:
                TP_subjects_insufficient_mark = True
            else:
                TP_subjects_validated = True

        if not practical_subjects:
            for course in list(valid_courses)[:]:
                if course.check_practical_work_experience:
                    valid_courses.remove(course)
                    reason = "Ces formations nécessitent de faire des travaux pratiques."
                    invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                    invalid_courses_by_reason['courses'].append(course)

        return valid_courses, invalid_courses
    
 

    def reorder_valid_courses_by_priority(valid_courses, lead_level_value_relation, lead_subject_relation_all, 
                                        course_level_value_relation_all, course_subject_relation_all, report_card_subjects):
        # Precompute values for efficient access
        lead_level_value_name = None if lead_level_value_relation is None else lead_level_value_relation.level_value.name
        lead_external_degree_name = None if lead_level_value_relation is None else lead_level_value_relation.external_degree.name
        lead_subject_names = {lsr.subject.name for lsr in lead_subject_relation_all if lsr.subject_id}
        report_card_subject_names = {rcs.subject.name for rcs in report_card_subjects if rcs.subject_id}
        report_card_external_subject_names = {rcs.external_subject.name for rcs in report_card_subjects if rcs.external_subject_id}
        
        # Cache for cosine similarity to avoid recalculating the same comparisons
        @lru_cache(maxsize=None)
        def cached_cosine_sim(value1, value2):
            return Helper.cosine_sim(value1, value2)

        # Preprocess all course-level values and subject relations for efficient lookups
        course_level_value_map = {
            clr.course_id: clr for clr in course_level_value_relation_all
        }
        course_subject_map = {}
        for csr in course_subject_relation_all:
            course_subject_map.setdefault(csr.course_id, []).append(csr)

        # Helper function to calculate similarity and priority
        def calculate_priority(course):
            level_value_priorities, subject_priorities = [], []

            # Course-level similarity calculations
            clr = course_level_value_map.get(course.id)
            if clr and clr.level_value_id:
                level_value_name = clr.level_value.name
                sim_with_lead_level = cached_cosine_sim(level_value_name, lead_level_value_name) if lead_level_value_name else 0
                sim_with_external_degree = cached_cosine_sim(level_value_name, lead_external_degree_name) if lead_external_degree_name else 0
                avg_similarity = (sim_with_lead_level + sim_with_external_degree) / 2
                level_value_priorities.append((avg_similarity, clr.priority if clr.priority else 1))
            
            max_sim_report_card, max_sim_external_subject = 0, 0
            # Course-subject similarity calculations
            for csr in course_subject_map.get(course.id, []):
                subject_name = csr.subject.name if csr.subject_id else None
                if subject_name:
                    # Calculate similarities with report card and external subjects
                    # print('+++subject_name 🎀 '+str(subject_name)+' '+str(len(report_card_subject_names)))
                    # for rcs_name in report_card_subject_names:
                    #     print('+++rcs.subject.name 🎀 '+str(rcs_name))
                    
                    if report_card_subject_names:    
                        max_sim_report_card = max(
                            cached_cosine_sim(subject_name, rcs_name) for rcs_name in report_card_subject_names
                        )
                    if report_card_external_subject_names:
                        max_sim_external_subject = max(
                            cached_cosine_sim(subject_name, ext_name) for ext_name in report_card_external_subject_names
                        )
                    
                    avg_similarity = (max_sim_report_card + max_sim_external_subject) / 2
                   # print('+++max_sim_report_card 🎀 '+str(csr.priority)+' '+str(avg_similarity))
                    subject_priorities.append((avg_similarity, csr.priority))

                    # Calculate similarity with lead subjects
                    max_sim_lead_subject = max(
                        cached_cosine_sim(subject_name, lsr_name) for lsr_name in lead_subject_names
                    )
                    subject_priorities.append((max_sim_lead_subject, csr.priority if csr.priority else 1))
            # print('+++level_value_priorities 😡 '+str(level_value_priorities))
            # Weighted averages for level value and subject priorities
            avg_level_value_priority = (
                sum(similarity * priority for similarity, priority in level_value_priorities) /
                sum(priority for _, priority in level_value_priorities)
                if level_value_priorities else 0
            )
            #print('+++subject_priorities 😷 '+str(subject_priorities))
            avg_subject_priority = (
                sum(similarity * priority for similarity, priority in subject_priorities) /
                sum(priority for _, priority in subject_priorities)
                if subject_priorities else 0
            )
            #print('+++avg_level_value_priority avg_subject_priority 🥶 '+str(avg_level_value_priority)+' '+str(avg_subject_priority))
            return (avg_level_value_priority + avg_subject_priority) / 2

        #Convert valid_courses to a list and cache the priorities
        valid_courses_list = list(valid_courses)



        course_priority_cache = {course.id: calculate_priority(course) for course in valid_courses_list}

        # Filter and sort courses based on the cached priorities
        valid_courses_list = [
            course for course in valid_courses_list if course_priority_cache[course.id] > 0.1
        ]
        #for course in valid_courses_list: 
        #    print(f"Course ID: {course.id}, Total calculate_priority: {calculate_priority(course)}")
        valid_courses_list.sort(
            key=lambda course: course_priority_cache[course.id],
            reverse=True
        )
        random.shuffle(valid_courses_list)
        return valid_courses_list[:20] 

    def parse_date(date_str):
        if date_str:
            return datetime.strptime(date_str, '%d/%m/%Y')
        return None

    def get_french_level(value):
        return get_level(value, {0: "A1", 20: "A2", 40: "B1", 60: "B2", 80: "C1", 100: "C2"})

    def get_english_level(value):
        return get_level(value, {0: "A1", 20: "A2", 40: "B1", 60: "B2", 80: "C1", 100: "C2"})

    def get_language_level(value):
        return get_level(value, {0: "A1", 20: "A2", 40: "B1", 60: "B2", 80: "C1", 100: "C2"})

    def get_level(value, level_map):
        return level_map.get(value, None)
        

        
    @app.route('/user/update/create', methods=['PUT'])
    def update_or_create_user():
        _json = request.json
        phone = _json.get('phone')
        
        # Attempt to find user by phone or user ID
        user = User.query.filter_by(phone=phone).first() or User.query.filter_by(id=_json.get('userId')).first()
        print('🎀 user 🎀 '+str(phone))
        # If user doesn't exist, create a new instance
        if user is None:
            user = User(phone=phone)

        # Update common fields
        user.firstname = _json.get('firstname')
        user.lastname = _json.get('lastname')
        user.country = _json.get('countryIso2')
        user.phone = phone

        # Map the type to the appropriate description field
        description_field_mapping = {
            'FLIGHT': 'description',
            'VISA_CANDA': 'work_description',
            'TOURISM': 'tourism_description',
            'FAMILY': 'family_description'
        }
        # Set the description field based on the type
        description_field = description_field_mapping.get(_json.get('typeRequest'))
        if description_field:
            setattr(user, description_field, _json.get('situationDescription'))

        # Add or update the user in the session and commit changes
        db.session.add(user)
        db.session.commit()

        return jsonify(user.as_dict())

    
    
        

    
    
    