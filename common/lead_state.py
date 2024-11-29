from dataclasses import dataclass
from typing import Optional, List, Set
from datetime import datetime

@dataclass
class LeadState:
    # Progression states
    mark_has_progressed_2_years_no_redoublement: bool = False
    mark_has_progressed_3_years_no_redoublement: bool = False
    mark_no_progression_2_years: bool = False
    mark_no_progression_3_years: bool = False
    
    # Work experience states
    has_work_experience_3_months: bool = False
    has_work_experience_6_months: bool = False
    has_work_experience_more_than_12_months: bool = False
    no_working_experience: bool = False
    no_working_experience_proof: bool = False
    
    # Academic states
    rank_MP_top_10: bool = False
    rank_no_progression_2_years: bool = False
    blank_year_1_time: bool = False
    blank_year_2_times_and_more: bool = False
    repeat_1_time: bool = False
    repeat_2_times: bool = False
    TP_subjects_validated: bool = False
    TP_subjects_insufficient_mark: bool = False

    def update_progression_state(self, mark_has_progressed_2_years: bool, mark_has_progressed_3_years: bool, 
                               repeats_n3: int) -> None:
        """Update progression state based on marks and repeats"""
        repeats_n3 = int(repeats_n3) if repeats_n3 is not None else 0
        if mark_has_progressed_2_years:
            if repeats_n3 > 1:
                self.repeat_2_times = True
                mark_has_progressed_2_years = False
            elif repeats_n3 == 1:
                self.repeat_1_time = True
            elif repeats_n3 == 0:
                self.mark_has_progressed_2_years_no_redoublement = True
                
        if mark_has_progressed_3_years and repeats_n3 == 0:
            self.mark_has_progressed_3_years_no_redoublement = True
            
        if not mark_has_progressed_2_years:
            self.mark_no_progression_2_years = True
            
        if not mark_has_progressed_3_years:
            self.mark_no_progression_3_years = True
            self.mark_no_progression_2_years = False

    def update_work_experience(self, work_experience) -> None:
        """Update work experience state based on WorkExperience object"""
        if not work_experience or not hasattr(work_experience, 'start_date'):
            self.no_working_experience = True
            return
        if not work_experience:
            self.no_working_experience = True
            return

        if not work_experience.can_prove:
            self.no_working_experience_proof = True
            return

        if work_experience.start_date:
            if work_experience.end_date:
                experience_duration = (work_experience.end_date - work_experience.start_date).days / 30
                if experience_duration >= 3:
                    self.has_work_experience_3_months = True
                if experience_duration >= 6:
                    self.has_work_experience_6_months = True
                if experience_duration > 12:
                    self.has_work_experience_more_than_12_months = True
            else:
                self.has_work_experience_more_than_12_months = True

    def update_from_blank_years(self, blank_year_count: int) -> None:
        """Update state based on blank years"""
        if blank_year_count == 1:
            self.blank_year_1_time = True
        elif blank_year_count >= 2:
            self.blank_year_2_times_and_more = True

    def update_from_repeats(self, repeat_count: int) -> None:
        """Update state based on repeat count"""
        if repeat_count == 1:
            self.repeat_1_time = True
        elif repeat_count == 2:
            self.repeat_2_times = True

    def update_TP_subjects(self, practical_subjects: List) -> None:
        """Update state based on practical subjects performance"""
        if practical_subjects:
            average_mark = sum(subject.mark_in_20 for subject in practical_subjects) / len(practical_subjects)
            if average_mark < 12:
                self.TP_subjects_insufficient_mark = True
            else:
                self.TP_subjects_validated = True
                
    def update_ranking_state(self, rank_has_progressed: bool) -> None:
        """Update ranking state based on progression"""
        if not rank_has_progressed:
            self.rank_no_progression_2_years = True 

    def set_rank_MP_top_10(self) -> None:
        """Set the rank MP top 10 state"""
        self.rank_MP_top_10 = True
