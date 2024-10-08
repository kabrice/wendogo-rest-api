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
from common.models.log import Log
from common.helper import Helper
from sqlalchemy import text
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError


def init_routes(app):
        @app.route('/user/generate/courses', methods=['PUT'])
    def generate_courses():
        user_payload = request.json
    
        user_payload = request.json

        user = User.query.filter_by(phone=user_payload.get('phone')).first()
        if not user:
            return jsonify({"error": "User not found", "status": False}), 404

        try:
            """I - Insert or update user and related data"""
            update_user(user, user_payload)
            lead = update_or_create_lead(user.id, user_payload)
            update_or_create_passport(user.id, user_payload)
            external_degree = update_or_create_external_degree(user_payload)
            if user_payload.get('programDomainObj', {}).get('id'):
                update_or_create_lead_level_relation(lead.id, user_payload, external_degree.id)
            update_or_create_lead_subject_relations(lead.id, user_payload)
            update_or_create_report_card(user_payload, lead.id, level=3)
            update_or_create_report_card(user_payload, lead.id, level=2)
            update_or_create_report_card(user_payload, lead.id, level=1)
            update_or_create_award(user_payload, lead.id)
            update_or_create_work_experience(user_payload, lead.id)
            update_or_create_traveling(user_payload, lead.id)

            """II - Process to generate courses"""
            results = generate_courses(lead)
            return jsonify(results)
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
        lead = Lead.query.filter_by(user_id=user_id).first() or Lead(user_id=user_id)
        lead.visa_id = payload.get('visaTypeSelectedId')
        hs_level_selected = payload.get('hsLevelSelected')
        lead.degree_id = hs_level_selected
        if hs_level_selected == 'deg00003':
            lead.bac_id = 'bac00003'
            lead.degree_id = hs_level_selected
        elif hs_level_selected == 'deg00002':
            lead.bac_id = 'bac00002'
            lead.degree_id = hs_level_selected
        else:
            lead.bac_id = payload.get('universityLevelSelected', {}).get('id')
            lead.degree_id = payload.get('degreeSelected', {}).get('id')
        lead.can_finance = payload.get('couldPayTuition')
        lead.french_level = get_french_level(payload.get('selectedFrenchLevel'))
        lead.can_prove_french_level = payload.get('haveDoneFrenchTest')
        lead.english_level = get_english_level(payload.get('selectedEnglishLevel'))
        lead.can_prove_english_level = payload.get('canJustifyEnglishLevel')
        lead.other_spoken_language_id = payload.get('selectedOtherSpokenLanguage', {}).get('id')
        lead.other_spoken_language_level = get_language_level(payload.get('selectedOtherLanguageLevel'))
        lead.can_prove_spoken_language_level = payload.get('canJustifyOtherLanguage')
        lead.number_of_repeats_n_3 = payload.get('classRepetitionNumber')
        lead.number_of_blank_years = payload.get('blankYearRepetitionNumber')
        db.session.add(lead)
        db.session.commit()
        return lead

    def update_or_create_passport(user_id, payload):
        passport = Passport.query.filter_by(user_id=user_id).first() or Passport(user_id=user_id)
        passport.delivery_date = parse_date(payload.get('passportDetails', {}).get('startDate'))
        passport.valid_until = parse_date(payload.get('passportDetails', {}).get('endDate'))
        db.session.add(passport)
        db.session.commit()

    def update_or_create_external_degree(payload):
        degree_name = payload.get('degreeExactNameValue', '').strip()
        existing_degree = ExternalDegree.query.filter(or_(ExternalDegree.name.ilike(degree_name)) ).first()
        if not existing_degree:
            external_degree = ExternalDegree(name=degree_name)
            db.session.add(external_degree)
            db.session.commit()
            return external_degree
        return existing_degree

    def update_or_create_lead_level_relation(lead_id, payload, external_degree_id):
        relation = LeadLevelValueRelation.query.filter_by(lead_id=lead_id).first() or LeadLevelValueRelation(lead_id=lead_id)
        relation.level_value_id = payload.get('programDomainObj', {}).get('id')
        relation.external_degree_id = external_degree_id
        school_year_name = payload.get('selectedSchoolYear3', {}).get('name') 
        relation.school_year_id = get_school_year_id(school_year_name)
        relation.is_current_year = school_year_name == str(datetime.now().year)
        db.session.add(relation)
        db.session.commit()
        return relation

    def update_or_create_lead_subject_relations(lead_id, payload):
        LeadSubjectRelation.query.filter_by(lead_id=lead_id).delete()
        inserted_relations = []
        for subject in payload.get('mainSubjects', []):
            lead_subject_relation = LeadSubjectRelation(
                lead_id=lead_id,
                subject_id=subject.get('id'),
                priority=subject.get('priority')
            )
            db.session.add(lead_subject_relation)
            inserted_relations.append(lead_subject_relation)
        db.session.commit()
        return inserted_relations

    def update_or_create_report_card(payload, lead_id, level):  

        if payload.get(f'isResult{level}Available') and payload.get(f'academicYearHeadDetails{level}'):
            
        #if f'isResult{level}Available' in payload and f'academicYearHeadDetails{level}' in payload:
            school_name = payload[f'academicYearHeadDetails{level}']['schoolName']
            external_school = ExternalSchool.query.filter_by(name=school_name).first() or ExternalSchool(
                name=school_name,
                city_id=payload[f'academicYearHeadDetails{level}']['city']['id'],
                educational_language_id=payload[f'academicYearHeadDetails{level}']['spokenLanguage']['id']
            )
            db.session.add(external_school)
            db.session.commit()
           
            most_recent_bac_id = get_most_recent_bac_id(payload)
            bac_id = None
            if level == 3:
                bac_id = most_recent_bac_id
            else:
                if level == 2:
                    bac_id = f'bac0000{int(most_recent_bac_id[-1]) - 1}'
                elif level == 1:
                    bac_id= f'bac0000{int(most_recent_bac_id[-1]) - 2}'
            
            # if bac_id not in bac_validation_map[most_recent_bac_id][0]:
            #     return jsonify({"error": "Invalid BAC ID", "status": False}),
            #print('==HAHA 🎀 '+bac_id)
            report_card = ReportCard.query.filter_by(lead_id=lead_id, bac_id=bac_id).first() or ReportCard(
                lead_id=lead_id
            ) 
            
            report_card.bac_id = bac_id                   
            report_card.country_id = payload[f'academicYearHeadDetails{level}']['country']['id']
            report_card.school_year_id = get_school_year_id(payload[f'selectedSchoolYear{level}']['name'])
            report_card.city_id = payload[f'academicYearHeadDetails{level}']['city']['id']
            report_card.external_school_id = external_school.id
            report_card.spoken_language_id = payload[f'academicYearHeadDetails{level}']['spokenLanguage']['id']
            report_card.academic_year_organization_id = payload[f'academicYearHeadDetails{level}']['academicYearOrganization']['id']
            report_card.mark_system_id = payload[f'academicYearHeadDetails{level}']['markSystem']['id']
            report_card.subject_weight_system_id = payload[f'academicYearHeadDetails{level}']['subjectWeightSystem']['id']

            db.session.add(report_card)
            db.session.commit()

            update_or_create_report_card_subject_relations(report_card.id, payload, level)
    
    def get_most_recent_bac_id(payload):
        hs_level_selected = payload.get('hsLevelSelected')
        if hs_level_selected == 'deg00003':
            return 'bac00003'
        elif hs_level_selected == 'deg00002':
            return 'bac00002'
        else:
            return payload.get('universityLevelSelected', {}).get('id')

    def update_or_create_report_card_subject_relations(report_card_id, payload, level):
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

        for new_subject in new_subjects:
            capitalized_subject = new_subject.capitalize()
            external_subject = ExternalSubject.query.filter_by(name=capitalized_subject).first() or ExternalSubject(name=capitalized_subject)
            db.session.add(external_subject)
            db.session.commit()
            external_subjects_map[new_subject] = external_subject.id

        for subjects in payload[f'reportCard{level}']:         
            for subject in subjects:
                school_term = payload[f'reportCard{level}'].index(subjects) + 1
                is_baccalaureat = subject['is_baccalaureat']
                weight = int(subject['weight']['value'])
                mark_in_20 = float(subject['mark']['valueIn20'])
                
                total_weighted_marks += weight * mark_in_20
                total_weights += weight

                if not is_baccalaureat:
                    school_term_marks[school_term].append(mark_in_20)
                else:
                    baccalaureat_marks.append(mark_in_20)

                rank = subject.get('rank', {}).get('value', None)
                if not rank:
                    # Cancel the process for the whole term if any rank is None
                    school_term_ranks[school_term] = []
                    break
                #print('==HAHA 🎀 '+rank+ ' - '+rank)
                rank = int(rank)
                total_ranks += rank
                rank_count += 1
                if not is_baccalaureat:
                    school_term_ranks[school_term].append(rank)

                relation = ReportCardSubjectRelation(
                    report_card_id=report_card_id,
                    school_term=school_term,
                    external_subject_id=external_subjects_map.get(subject['label']['value']),
                    subject_id=existing_subjects_map.get(subject['label']['value']),
                    is_baccalaureat=is_baccalaureat,
                    is_pratical_subject=subject['is_practical_work'],
                    weight=weight,
                    mark=subject['mark']['value'],
                    mark_in_20=mark_in_20,
                    rank=rank
                )
                db.session.add(relation)
        
        report_card = ReportCard.query.get(report_card_id)

        for term in range(1, 5):
            if school_term_marks[term]:
                setattr(report_card, f'school_term{term}_average_mark_in_20', sum(school_term_marks[term]) / len(school_term_marks[term]))

        if baccalaureat_marks:
            report_card.baccalaureat_average_mark_in_20 = sum(baccalaureat_marks) / len(baccalaureat_marks)

        if total_weights > 0:
            average_mark_in_20 = sum([getattr(report_card, f'school_term{term}_average_mark_in_20') for term in range(1, 4) if getattr(report_card, f'school_term{term}_average_mark_in_20') is not None]) / len([term for term in range(1, 4) if getattr(report_card, f'school_term{term}_average_mark_in_20') is not None])
            report_card.average_mark_in_20 = average_mark_in_20

        for term in range(1, 4):
            if len(school_term_ranks[term]) == len([subject for subjects in payload[f'reportCard{level}'] for subject in subjects if payload[f'reportCard{level}'].index(subjects) + 1 == term and not subject['is_baccalaureat']]):
                if len(school_term_ranks[term]) > 0:
                    setattr(report_card, f'school_term{term}_overall_rank', sum(school_term_ranks[term]) / len(school_term_ranks[term]))

        if rank_count == len([subject for subjects in payload[f'reportCard{level}'] for subject in subjects]):
            overall_ranks = [getattr(report_card, f'school_term{term}_overall_rank') for term in range(1, 4) if getattr(report_card, f'school_term{term}_overall_rank') is not None]
            if overall_ranks:
                overall_rank = sum(overall_ranks) / len(overall_ranks)
                report_card.overall_rank = overall_rank

        db.session.add(report_card)
        db.session.commit()

    def update_or_create_award(payload, lead_id):
        award_data = payload.get('award')
        if award_data:

            award = Award.query.filter_by(lead_id=lead_id).first() or Award(lead_id=lead_id)
            award.name = award_data.get('awardName')
            award.school_year_id = award_data.get('year', {}).get('id')
            award.country_id = award_data.get('country', {}).get('id')
            award.city_id = award_data.get('city', {}).get('id')
            award.spoken_language_id = award_data.get('spokenLanguage', {}).get('id')
            award.honour_type = award_data.get('honourType', {}).get('name')
            award.rank = award_data.get('rank')
            db.session.add(award)
            db.session.commit()

    def update_or_create_work_experience(payload, lead_id):
        work_experience_data = payload.get('workExperience')
        if work_experience_data:
            work_experience = WorkExperience.query.filter_by(lead_id=lead_id).first() or WorkExperience(lead_id=lead_id)
            work_experience.description = work_experience_data.get('description')
            work_experience.start_date = parse_date(work_experience_data.get('startDate'))
            work_experience.end_date = parse_date(work_experience_data.get('endDate')) if work_experience_data.get('endDate') != 'None' else None
            work_experience.can_prove = payload.get('canProveWorkExperience')
            db.session.add(work_experience)
            db.session.commit()

    def update_or_create_traveling(payload, lead_id):
        traveling_data = payload.get('alreadyTraveledToFrance')
        if traveling_data:
            traveling = Traveling.query.filter_by(lead_id=lead_id).first() or Traveling(lead_id=lead_id)
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

    def generate_courses(lead):
        lead_id = lead.id    
        report_cards = ReportCard.query.filter_by(lead_id=lead_id).all()
        report_card_subject_relation = ReportCardSubjectRelation.query.filter(ReportCardSubjectRelation.report_card_id.in_([report_card.id for report_card in report_cards])).all()
        inegible_reasons = check_inegibility_lead(lead, report_cards, report_card_subject_relation)
        if inegible_reasons:
            return {'valid_courses': [], 'invalid_courses': inegible_reasons}
        else:
            valid_courses, invalid_courses = get_courses(lead, report_cards, report_card_subject_relation)
            return {'inegible_reasons': inegible_reasons, 'valid_courses': list(valid_courses), 'invalid_courses': list(invalid_courses)}
        
    
    def check_inegibility_lead(lead, report_cards, report_card_subject_relation):
        lead_id = lead.id
        inegible_reasons = []
        def validate_credits(bac_ids):
            for bac_id in bac_ids:
                validation_result = check_if_lead_has_validated_all_credits_on_complete_term(report_cards, bac_id)
                if validation_result:
                    inegible_reasons.append(validation_result)

        def validate_cumulative_mark(start_bac_id, end_bac_id):
            if cumulative_mark_for_the_completed_years(report_cards, start_bac_id, end_bac_id) < 10:
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

        if lead.number_of_repeats_n_3 > 2:
            inegible_reasons.append({'id': 'reas0009', 'reason': "Vous avez plus de 2 redoublements durant les 3 dernières années"})

        return inegible_reasons

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

        total_weight = sum(subject.weight for subject in report_card_subjects if subject.mark >= 10)
        return total_weight < 60
    
    def university_term_is_complete(report_cards,  bac_id):
        number_of_valid_terms = 2
        report_card = next((rc for rc in report_cards if rc.bac_id == bac_id), None)
        if not report_card:
            return False
        valid_term_count = sum(1 for term in range(1, 5) if getattr(report_card, f'school_term{term}_average_mark_in_20') is not None)
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

        if lead.bac_id <= 'bac00005' or (lead.bac_id == 'bac00006' and not university_term_is_complete(lead_id, bac_id)):
            initial_courses = Course.query.filter(Course.level_id <= 'lev0014').all()
        else:
            initial_courses = Course.query.filter(Course.level_id > 'lev0014').all()

        most_recent_bac_id = max(report_card.bac_id for report_card in report_cards)
        most_recent_bac_year = get_bac_year(most_recent_bac_id)

        most_recent_available_report_card_first = get_most_recent_report_card(most_recent_bac_year, report_cards)

        if most_recent_available_report_card_first:
            most_recent_available_report_card_second = get_most_recent_report_card(get_bac_year(most_recent_available_report_card_first.bac_id) - 1, report_cards)

        lead_level_value_relation = LeadLevelValueRelation.query.filter_by(lead_id=lead_id).first()  
        lead_subject_relation = LeadSubjectRelation.query.filter_by(lead_id=lead_id).all()
        course_subject_relation = CourseSubjectRelation.query.filter(CourseSubjectRelation.course_id.in_([course.id for course in initial_courses])).all()
        valid_courses.update(get_courses_where_course_names_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses))
        print('==HAHA 🎀 1 '+str(len(valid_courses)))
        course_level_value_relation = CourseLevelRelation.query.filter(CourseLevelRelation.course_id.in_([course.id for course in list(valid_courses)])).all()
        valid_courses.update(get_courses_where_level_values_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses, course_level_value_relation))
        print('==HAHA 🎀 2 '+str(len(valid_courses)))
        valid_courses.update(get_courses_where_subjects_are_similar_to_lead_external_subjects(report_card_subjects, initial_courses, most_recent_available_report_card_first, 
                                                                                              most_recent_available_report_card_second, course_subject_relation))
        
        print('==HAHA 🎀 3 '+str(len(valid_courses)))
        work_experience = WorkExperience.query.filter_by(lead_id=lead_id).first()

        exclude_courses_from_course_criteria(lead, work_experience, valid_courses, invalid_courses, report_cards, report_card_subjects)

        course_level_value_relation = CourseLevelRelation.query.filter(CourseLevelRelation.course_id.in_([course.id for course in list(valid_courses)])).all()
 
        purge_courses_from_course_level_value_relation(lead, report_cards, valid_courses, invalid_courses, course_level_value_relation, lead_level_value_relation)

        purge_courses_from_course_subject_relation(report_cards, report_card_subjects, valid_courses, invalid_courses, course_subject_relation)
        
        reorder_valid_courses_by_priority(valid_courses, lead_level_value_relation, lead_subject_relation, course_level_value_relation, course_subject_relation, report_card_subjects)

        return valid_courses, invalid_courses
             
    def get_courses_where_course_names_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses):
        return get_similar_courses(
            initial_courses,
            lead_level_value_relation.external_degree.name,
            lambda course: course.name if course.name else course.title
        )

    def get_courses_where_level_values_are_similar_to_lead_degree_name(lead_level_value_relation, initial_courses, course_level_value_relation):
        return get_similar_courses(
            initial_courses,
            lead_level_value_relation.external_degree.name,
            lambda course: next(
                (relation.level_value.name for relation in course_level_value_relation if relation.course_id == course.id),
                None  # Return None if no match is found
        )
        )

    def get_similar_courses(courses, target_name, attribute_func):
        similarities = [
            (course, sim) for course in courses 
            if (attr := attribute_func(course)) and (sim := Helper.cosine_sim(attr, target_name)) > 0
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [course for course, _ in similarities[:50]]
    
    def get_courses_where_subjects_are_similar_to_lead_external_subjects(report_card_subjects, initial_courses, most_recent_available_report_card_first, most_recent_available_report_card_second, course_subject_relation):
        target_subject_names = set()
        def add_target_subject_names(report_card):
            if report_card:
                report_card_subject_relation = [relation for relation in report_card_subjects if relation.report_card_id == report_card.id]
                target_subject_names.update([relation.subject.name for relation in report_card_subject_relation if relation.subject is not None])
                target_subject_names.update([relation.external_subject.name for relation in report_card_subject_relation if relation.external_subject is not None])

        add_target_subject_names(most_recent_available_report_card_first)
        add_target_subject_names(most_recent_available_report_card_second)

        course_similarities = {}

        for course_relation in course_subject_relation:
            course_id = course_relation.course_id
            subject = course_relation.subject
            if not subject.is_tech:
                subject_name = subject.name

            if course_id not in course_similarities:
                course_similarities[course_id] = []

            for target_subject_name in target_subject_names:
                if subject_name and target_subject_name:
                    #print('==HAHA 🎀 '+subject_name+' - '+target_subject_name)
                    similarity = Helper.cosine_sim(subject_name, target_subject_name)
                    course_similarities[course_id].append(similarity)

        # Calculate the average similarity for each course
        average_similarities = [
            (course_id, sum(similarities) / len(similarities))
            for course_id, similarities in course_similarities.items()
            if sum(similarities) > 0
        ]

        # Sort courses by average similarity in descending order
        average_similarities.sort(key=lambda x: x[1], reverse=True)

        # Retrieve the top 20 courses
        top_courses = [course for course in initial_courses if course.id in [course_id for course_id, _ in average_similarities[:25]]]

        return top_courses
    
    def add_invalid_course_reason(reason, invalid_courses):
        invalid_courses_by_reason = next((item for item in invalid_courses if item['reason'] == reason), None)
        if not invalid_courses_by_reason:
            invalid_courses_by_reason = {'reason': reason, 'courses': []}
            invalid_courses.append(invalid_courses_by_reason)
        return invalid_courses_by_reason
    
    def exclude_courses_from_course_criteria(lead, work_experience, valid_courses, invalid_courses, report_cards, report_card_subjects):

        # Exclude courses that require work experience if the lead has no work experience
        lead_id = lead.id

        def remove_invalid_courses(valid_courses, invalid_courses_by_reason, levels):
            for course in list(valid_courses)[:]:
                if course.professional_experience_requirement_level in levels:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)

        if work_experience and not work_experience.can_prove:
            reason = 'Vous n\'avez pas pu justifier votre expérience professionnelle'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            remove_invalid_courses(valid_courses, invalid_courses_by_reason, [1])

        if not work_experience:
            reason = 'Ces formations nécessitent une expérience professionnelle'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            remove_invalid_courses(valid_courses, invalid_courses_by_reason, [0.5, 1])

        # Exclude courses that require a specific level of French if the lead does not meet the requirement
        if lead.french_level:
            reason = 'Votre niveau de français est insuffisant pour ces formations'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            for course in list(valid_courses)[:]:
                if course.french_level and lead.french_level < course.french_level:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)

        # Exclude courses that require a specific level of english if the lead does not meet the requirement 
        if lead.english_level:
            reason = 'Votre niveau d\'anglais est insuffisant pour ces formations'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            for course in list(valid_courses)[:]:
                if course.english_level and lead.english_level < course.english_level:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)

        # Exclude courses that require a specific level of other spoken language if the lead does not meet the requirement
        if lead.other_spoken_language_level:
            reason = 'Votre niveau de la langue étrangère est insuffisant pour ces formations'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            for course in list(valid_courses)[:]:
                if course.another_language_level and lead.other_spoken_language_level < course.other_spoken_language_level:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)

        
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

        # Manage courses where is_progression_mandatory
        mark_has_progressed_for_2_years = False
        mark_has_progressed_for_3_year = False

        if lead.bac_id in bac_validation_map:
            bac_ids = bac_map[lead.bac_id]
            for i in range(len(bac_ids) - 1):
                current_bac_id = bac_ids[i]
                previous_bac_id = bac_ids[i + 1]
                current_report_card = next((rc for rc in report_cards if rc.bac_id == current_bac_id), None)
                previous_report_card = next((rc for rc in report_cards if rc.bac_id == previous_bac_id), None)
                if current_report_card and previous_report_card:
                    if (current_report_card.average_mark_in_20 > previous_report_card.average_mark_in_20 and
                        current_report_card.average_mark_in_20 > 10 and previous_report_card.average_mark_in_20 > 10):
                        mark_has_progressed_for_2_years = True
                        break
                
            for i in range(len(bac_ids) - 2):
                current_bac_id = bac_ids[i]
                previous_bac_id = bac_ids[i + 1]
                earlier_bac_id = bac_ids[i + 2]
                current_report_card = next((rc for rc in report_cards if rc.bac_id == current_bac_id), None)
                previous_report_card = next((rc for rc in report_cards if rc.bac_id == previous_bac_id), None)
                earlier_report_card = next((rc for rc in report_cards if rc.bac_id == earlier_bac_id), None)
                if current_report_card and previous_report_card and earlier_report_card:
                    if (current_report_card.average_mark_in_20 > previous_report_card.average_mark_in_20 and
                        previous_report_card.average_mark_in_20 > earlier_report_card.average_mark_in_20 and
                        current_report_card.average_mark_in_20 > 10 and previous_report_card.average_mark_in_20 > 10 and
                        earlier_report_card.average_mark_in_20 > 10):
                        mark_has_progressed_for_3_year = True
                        break

        if mark_has_progressed_for_2_years and lead.number_of_repeats_n_3 > 1:
            mark_has_progressed_for_2_years = False

        if not mark_has_progressed_for_2_years:
            reason = 'Vous n\'avez pas progressé entre deux années consécutives'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            for course in list(valid_courses)[:]:
                if course.is_progression_mandatory:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)

        if not mark_has_progressed_for_3_year:
            reason = 'Vous n\'avez pas progressé entre trois années consécutives'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            for course in list(valid_courses)[:]:
                if course.check_grade_since_n3:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)


        # Manage courses where is_ranking_mandatory 
        rank_has_progressed_for_2_year = False

        if lead.bac_id in bac_validation_map:
            bac_ids = bac_map[lead.bac_id]
            for i in range(len(bac_ids) - 1):
                current_bac_id = bac_ids[i]
                previous_bac_id = bac_ids[i + 1]
                current_report_card = next((rc for rc in report_cards if rc.bac_id == current_bac_id), None)
                previous_report_card = next((rc for rc in report_cards if rc.bac_id == previous_bac_id), None)
                if current_report_card and previous_report_card: 
                    if current_report_card.overall_rank  and previous_report_card.overall_rank :
                        if current_report_card.overall_rank <= 10 and previous_report_card.overall_rank <= 10:
                            if current_report_card.overall_rank < previous_report_card.overall_rank:
                                rank_has_progressed_for_2_year = True
                                break
                    
        if not rank_has_progressed_for_2_year:
            reason = 'Votre rang n\'a pas progressé entre deux années consécutives'
            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
            for course in list(valid_courses)[:]:
                if course.is_ranking_mandatory:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)        
                       
        return valid_courses, invalid_courses

    def purge_courses_from_course_level_value_relation(lead, report_cards, valid_courses, invalid_courses, course_level_value_relation, lead_level_relation):
        
        #invalid_courses_by_reason = {'reason': "Votre moyenne récente est inférieure au score minimum requis.", 'courses': []}
        # Get the most recent available report card
        most_recent_available_report_card = get_most_recent_report_card(get_bac_year(lead.bac_id), report_cards)

        def get_average_mark(bac_id):
            """Helper function to retrieve the average mark for a specific bac level."""
            report_card = next((rc for rc in report_cards if rc.bac_id == bac_id), None)
            return report_card.average_mark_in_20 if report_card and report_card.average_mark_in_20 is not None else 0
        # Loop through course level values and apply the filtering conditions
        for course_level_value in course_level_value_relation:
            
            # Check if level_value matches and minimum_score exists
            if course_level_value.minimum_score:
            
                # Compare level_value similarity or exact match
                if (
                    course_level_value.level_value_id == lead_level_relation.level_value_id or
                    Helper.cosine_sim(course_level_value.level_value.name, lead_level_relation.level_value.name) >= 0.25
                ):
                    
                    # Get the most recent available mark
                    recent_mark = most_recent_available_report_card.average_mark_in_20 if most_recent_available_report_card else 0

                    # If recent mark is less than minimum score, proceed with checks
                    if recent_mark < course_level_value.minimum_score:
                    
                        # Check for specific course level conditions (L1, L2, L3)
                        if (
                            (course_level_value.is_L1 and get_average_mark('bac00004') < course_level_value.minimum_score) or
                            (course_level_value.is_L2 and get_average_mark('bac00005') < course_level_value.minimum_score) or
                            (course_level_value.is_L3 and get_average_mark('bac00006') < course_level_value.minimum_score)
                        ):
                            # Filter out invalid courses and add reason
                            valid_courses = [course for course in list(valid_courses) if course.id != course_level_value.course_id]
                            reason = "Votre moyenne récente est inférieure au score minimum requis."
                            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                            invalid_courses_by_reason['courses'].add(course_level_value.course)

        return valid_courses, invalid_courses

    def purge_courses_from_course_subject_relation(report_cards, report_card_subjects, valid_courses, invalid_courses, course_subject_relation):
        invalid_courses_by_reason = {'reason': "Votre note dans certaines matières est inférieure au score minimum requis.", 'courses': []}

        for subject_relation in course_subject_relation:
            if subject_relation.minimum_score and not subject_relation.subject.is_tech:
                for report_card_subject_relation in report_card_subjects:
                    #print('==HIHI 🎀 '+str(subject_relation.subject.name)+' - '+str(report_card_subject_relation.subject.name))
                    if (report_card_subject_relation.subject_id == subject_relation.subject_id or (report_card_subject_relation.subject_id and subject_relation.subject_id and Helper.cosine_sim(subject_relation.subject.name, report_card_subject_relation.subject.name) >= 0.25)) and report_card_subject_relation.mark_in_20 < subject_relation.minimum_score:
                        course = next((course for course in list(valid_courses) if course.id == subject_relation.course_id), None)
                        if course:
                            valid_courses.remove(course)
                            reason = "Votre note dans certaines matières est inférieure au score minimum requis."
                            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                            invalid_courses_by_reason['courses'].append(course)

        new_course_subject_relations = [relation for relation in course_subject_relation if relation.course_id in [course.id for course in list(valid_courses)] and relation.subject.is_tech]

        for new_subject_relation in new_course_subject_relations:
            if new_subject_relation.subject_id == 'suj0212': #MP
                for report_card in report_cards:
                    top_subjects = sorted(
                                        [rel for rel in report_card_subject_relation if rel.report_card_id == report_card.id],
                                        key=lambda x: x.weight, reverse=True
                                    )[:4]
                    if any(subject.mark < 14 for subject in top_subjects) and not all(
                            top_subjects[i].mark > top_subjects[i + 1].mark for i in range(len(top_subjects) - 1)
                            ):
                        reason = "Votre performance dans les matières techniques n'est pas suffisante."
                        invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                        valid_courses.remove(new_subject_relation.course)
                        invalid_courses_by_reason['courses'].add(new_subject_relation.course)

            if new_subject_relation.subject_id == 'suj0382': # Moyenne baccalaureat < 13
                baccalaureat_subjects = [subject for subject in report_card_subject_relation if subject.is_baccalaureat]
                average_mark = sum(subject.mark_in_20 for subject in baccalaureat_subjects) / len(baccalaureat_subjects)
                if average_mark < 13:
                    reason = "Votre moyenne au baccalauréat est inférieure à 13."
                    invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                    valid_courses.remove(new_subject_relation.course)
                    invalid_courses_by_reason['courses'].add(new_subject_relation.course)

            if new_subject_relation.subject_id == 'suj0403': #Moyenne generale
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
                            reason = f"Votre moyenne dans les matières techniques pour le terme {term} est inférieure à 12."
                            invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                            valid_courses.remove(new_subject_relation.course)
                            invalid_courses_by_reason['courses'].append(new_subject_relation.course)

            if new_subject_relation.subject_id == 'suj0405': #Top 10
                for report_card_subject_relation in report_card_subject_relation:
                    if (
                        report_card_subject_relation.subject_id == new_subject_relation.subject_id or
                        Helper.cosine_sim(new_subject_relation.subject.name, report_card_subject_relation.subject.name) >= 0.25
                        ) and report_card_subject_relation.rank > 10:
                        reason = "Votre rang dans les matières techniques est supérieur à 10."
                        invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                        valid_courses.remove(new_subject_relation.course)
                        invalid_courses_by_reason['courses'].add(new_subject_relation.course)
            
        #for report_cart_subject in report_card_subject_relation, if no report_cart_subject has report_cart_subject.is_pratical_subject = true, then remove every courses where course.check_practical_work_experience = true

        if not any(report_card_subject.is_pratical_subject for report_card_subject in report_card_subjects):
            for course in list(valid_courses)[:]:
                if course.check_practical_work_experience:
                    valid_courses.remove(course)
                    invalid_courses_by_reason['courses'].append(course)
                    reason = "Ces formations nécessitent de faire des travaux pratiques."
                    invalid_courses_by_reason = add_invalid_course_reason(reason, invalid_courses)
                    
                    
        return valid_courses, invalid_courses

    def reorder_valid_courses_by_priority(valid_courses, lead_level_value_relation, lead_subject_relation_all, course_level_value_relation_all, course_subject_relation_all, report_card_subjects):
        def calculate_priority(course, lead_level_value_relation, lead_subject_relation_all, report_card_subjects):
            level_value_priorities = []
            subject_priorities = []

            # Calculate level value priorities
            course_level_values = [clr for clr in course_level_value_relation_all if clr.course_id == course.id]
            for clr in course_level_values:
                level_value_name = clr.level_value.name if clr.level_value_id else None
                if level_value_name:
                    sim_with_lead_level = Helper.cosine_sim(level_value_name, lead_level_value_relation.level_value.name) 
                    sim_with_external_degree = Helper.cosine_sim(level_value_name, lead_level_value_relation.external_degree.name) 
                    avg_similarity = (sim_with_lead_level + sim_with_external_degree) / 2
                    level_value_priorities.append((avg_similarity, clr.priority))

            # Calculate subject priorities
            course_subjects = [csr for csr in course_subject_relation_all if csr.course_id == course.id]
            for csr in course_subjects:
                subject_name = csr.subject.name if csr.subject_id else None
                if subject_name:
                    for report_card_subject in report_card_subjects:
                        sim_with_report_card_subject = Helper.cosine_sim(subject_name, report_card_subject.subject.name) if report_card_subject.subject_id else 0
                        sim_with_external_degree = Helper.cosine_sim(subject_name, report_card_subject.external_subject.name) if report_card_subject.external_subject_id else 0
                        avg_similarity = (sim_with_report_card_subject + sim_with_external_degree) / 2
                        subject_priorities.append((avg_similarity, csr.priority))

                    for lead_subject_relation in lead_subject_relation_all:
                        sim_with_lead_subject = Helper.cosine_sim(subject_name, lead_subject_relation.subject.name) if lead_subject_relation.subject_id else 0
                        subject_priorities.append((sim_with_lead_subject, csr.priority))

            # Calculate weighted average priorities
            total_level_priority = sum(priority for _, priority in level_value_priorities)
            avg_level_value_priority = sum(similarity * priority for similarity, priority in level_value_priorities) / total_level_priority if total_level_priority > 0 else 0

            total_subject_priority = sum(priority for _, priority in subject_priorities)
            avg_subject_priority = sum(similarity * priority for similarity, priority in subject_priorities) / total_subject_priority if total_subject_priority > 0 else 0

            return (avg_level_value_priority + avg_subject_priority) / 2

        # Calculate priority for each course and sort by priority in descending order
        valid_courses = list(valid_courses) 
        valid_courses.sort(key=lambda course: calculate_priority(course, lead_level_value_relation, lead_subject_relation_all, report_card_subjects), reverse=True)




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
        
