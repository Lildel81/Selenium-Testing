import pytest
from datetime import datetime
import re


# TEST FOCUS CHAKRA FILTER
@pytest.mark.chakra
def test_focus_chakra_filter(chakra_results):
    focus_chakra = "solarPlexusChakra"

    query = {
        "focusChakra": focus_chakra,
    }

    count = chakra_results.count_documents(query)
    print(f"\n[Focus Chakra] Docs with focusChakra='{focus_chakra}': {count}\n")

   
    assert count == 4  #set to expected count from chakra result page 


#TEST ARCHETYPE FILTER 
@pytest.mark.chakra
def test_archetype_filter(chakra_results):
    archetype = "workerBee"

    query = {
        "archetype": archetype,
    }

    count = chakra_results.count_documents(query)
    print(f"\n[Archetype] Docs with archetype='{archetype}' : {count}\n")

    assert count == 8 #set to expected count from chakra result page



#TEST FAMILUR WITH + CHALLENGES 
@pytest.mark.chakra
def test_familiar_with_and_challenges_combined(chakra_results):
   
    familiar_values = [
        "kundalini"
    ]
    challenge_values = [
        "spiritual"
    ]

    query = {
        "familiarWith": {"$all": familiar_values},
        "challenges": {"$all": challenge_values},
    }

    count = chakra_results.count_documents(query)
    print(
        f"\n[Familiar + Challenges] Docs where it has familiar with\n "
        f"{familiar_values} AND has challenges {challenge_values}: {count}\n"
    )

    assert count == 7 #set to expected count from chakra result page



# TEST SEARCH BAR + DATE RANGE
@pytest.mark.chakra
def test_search_and_date_range_combined(chakra_results):
    search_term = "camacho"
    pattern = re.compile(search_term, re.IGNORECASE)

    date_from = datetime(2025, 11, 12)
    date_to = datetime(2025, 11, 20, 23, 59, 59)

    query = {
        "$and": [
            {
                "createdAt": {
                    "$gte": date_from,
                    "$lte": date_to,
                }
            },
            {
                "$or": [
                    {"fullName": pattern},
                    {"email": pattern},
                    {"contactNumber": pattern},
                    {"jobTitle": pattern},
                ]
            },
        ]
    }

    count = chakra_results.count_documents(query)
    print(
        f"\n[Search + Date] Docs matching '{search_term}' between\n"
        f"{date_from} and {date_to}: {count}\n"
    )

    assert count == 1 #set to expected count from chakra result page