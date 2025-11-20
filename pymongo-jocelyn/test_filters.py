import pytest
from datetime import datetime
import re


#TEST SEARCH FILTER(name/email/phone/jobTitle)
@pytest.mark.application
def test_search_filter_count(applications, search_term):
    pattern = re.compile(search_term, re.IGNORECASE)

    query = {
        "$or": [
            {"fullName": pattern},
            {"email": pattern},
            {"contactNumber": pattern},
            {"jobTitle": pattern},
        ]
    }

    count = applications.count_documents(query)
    print(f"\n[Search] Documents matching '{search_term}': {count}\n")

    expected_count = 6  #set to expected count from application result page 
    assert count == expected_count

#TEST AGE BRACKET FILTER
@pytest.mark.application
def test_age_bracket_count(applications):
    query = {"ageBracket": "40-50"}
    count = applications.count_documents(query)
    print(f"\n[Age] Documents with ageBracket '40-50': {count}\n")

    expected_count = 9   #set to expected count from application result page 
    assert count == expected_count


# TEST HEALTHCARE WORKER FILTER
@pytest.mark.application 
def test_healthcare_worker_count(applications):
    query = {"isHealthcareWorker": "Yes"}
    count = applications.count_documents(query)
    print(f"\n[HC Worker] Documents with isHealthcareWorker='Yes': {count}\n")

    expected_count = 3   #set to expected count from application result page 
    assert count == expected_count


#TEST WORK WITH PRACTITIONER
@pytest.mark.application
def test_worked_with_practitioner(applications):
    query = {"workedWithPractitioner": "Currently working with one"}

    count = applications.count_documents(query)
    print(f"\n[Practitioner] Docs with workedWithPractitioner='Currently working with one': {count}\n")

    expected_count = 4  #set to expected count from application result page 
    assert count == expected_count



#TEST FAMILUR WITH FILTER 
@pytest.mark.application
def test_familiar_with_count(applications):
    query = {
        "familiarWith":{
            "$all": ["Kundalini Yoga", "Life Coaching"]
        }
    } 
    count = applications.count_documents(query)
    print(f"\n[FamiliarWith] Docs familiar with 'Kundalini Yoga' and 'Life Coaching' : {count}\n")

    expected_count = 2  #set to expected count from application result page 
    assert count == expected_count



# TEST CHALLENGES CHECKBOX FILTER 
@pytest.mark.application
def test_challenges_count(applications):
    query = {
        "challenges":{
            "$all": ["Physical", "Emotional"]
        }
    }
    count = applications.count_documents(query)
    print(f"\n[Challenges] Docs with 'Physical' and 'Emotional' challenge: {count}\n")

    expected_count = 3  #set to expected count from application result page 
    assert count == expected_count


#TEST DATE RANGE FILTER 
@pytest.mark.application
def test_date_range_filter(applications):
    date_from = datetime(2025, 11, 12)
    date_to = datetime(2025, 11, 19, 23, 59, 59)

    query = {
        "submittedAt": {
            "$gte": date_from,
            "$lte": date_to,
        }
    }

    count = applications.count_documents(query)
    print(f"\n[Date] Docs submitted between {date_from} and {date_to}: {count}\n")

    expected_count = 11 #set to expected count from application result page 
    assert count == expected_count


#COMBINED FILTER SEARCH 
@pytest.mark.application
def test_combined_multiple_filters(applications):
    query = {
        "$and": [
            {"workedWithPractitioner": "Currently working with one"},
            {"isHealthcareWorker": "Yes"},
            {"familiarWith": {"$all": ["Life Coaching", "Kundalini Yoga"]}},
            {"challenges": {"$all": ["Physical", "Emotional"]}}
        ]
    }

    count = applications.count_documents(query)
    print(
        f"\n[Combined Filters] Practitioner='Currently working with one', "
        f"HC Worker='Yes', familiarWith contains Life Coaching + Kundalini, "
        f"challenges contain Physical + Emotional ----> Results: {count}"
    )

    
    expected_count = 1   #set to expected count from application result page 
    assert count == expected_count