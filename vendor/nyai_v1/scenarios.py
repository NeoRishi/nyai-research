"""
The 5 test scenarios for NyAI demonstration.

3 wellness (Ayurveda) + 2 general domain.
These are locked and should not change.
"""

from datetime import datetime, timedelta
from .pramana import Evidence, PramanaType
from .reasoning_agent import NyAIAgent, NaiveAgent


def get_scenarios():
    """Return all 5 scenarios with their evidence and metadata."""
    now = datetime.now()

    return [
        {
            "id": "s1",
            "number": 1,
            "domain": "wellness",
            "title": "Vata winter care",
            "subtitle": "Happy path — all sources agree",
            "claim": "Warm sesame oil abhyanga is recommended for this person",
            "expected_verdict": "accepted",
            "context": {
                "example": "In Vata-predominant individuals during cold seasons, warm oil application has consistently shown benefits across both traditional texts and modern practice.",
                "application": "This person is Vata-predominant, it is winter (cold+dry), and they report dry skin. All evidence sources converge on warm sesame oil abhyanga.",
            },
            "evidence": [
                {"content": "User reports dry skin and cold extremities", "pramana_type": "pratyaksha", "source": "User check-in", "tags": ["vata", "dry_skin", "winter"]},
                {"content": "Vata-predominant prakriti derived from constitution assessment", "pramana_type": "anumana", "source": "BioRhythm engine", "tags": ["vata"]},
                {"content": "Charaka Samhita recommends warm oil for Vata in Hemanta/Shishira", "pramana_type": "shabda", "source": "Charaka Samhita Ch.5", "tags": ["vata", "oil", "warm", "winter"]},
                {"content": "85% of similar Vata users reported improvement with warm oil abhyanga in winter", "pramana_type": "upamana", "source": "NeoRishi cohort data", "tags": ["vata", "oil", "warm"]},
            ],
        },
        {
            "id": "s2",
            "number": 2,
            "domain": "wellness",
            "title": "Stale check-in data",
            "subtitle": "Kalatita — evidence too old",
            "claim": "Summer diet plan is appropriate for this person",
            "expected_verdict": "suspended",
            "evidence_age_days": 12,
            "context": {
                "example": "Seasonal diet recommendations require current body observations as the basis for any advice.",
                "application": "The user's last check-in was 12 days ago — beyond the 7-day freshness threshold. We cannot rely on stale Pratyaksha data for seasonal recommendations.",
            },
            "evidence": [
                {"content": "User reported feeling hot and thirsty (12 days ago)", "pramana_type": "pratyaksha", "source": "User check-in (stale)", "tags": ["pitta", "summer", "grishma"]},
                {"content": "Grishma rtu calls for cooling foods and lighter meals", "pramana_type": "shabda", "source": "Charaka Samhita", "tags": ["summer", "cooling", "grishma"]},
                {"content": "Pitta dosha increases in summer months", "pramana_type": "anumana", "source": "Seasonal inference", "tags": ["pitta", "summer"]},
            ],
        },
        {
            "id": "s3",
            "number": 3,
            "domain": "wellness",
            "title": "Ginger for Pitta",
            "subtitle": "Savyabhichara — the money moment",
            "claim": "Ginger tea is recommended for this person's digestive issues",
            "expected_verdict": "rejected",
            "context": {
                "example": "In Vata and Kapha types, ginger relieves sluggish digestion. However, in Pitta types, ginger's heating quality can aggravate existing heat-related symptoms.",
                "application": "This person has Pitta prakriti AND reports acid reflux. Ginger is heating (ushna virya) and will worsen both Pitta and acid reflux. The general rule 'ginger aids digestion' does not apply here.",
            },
            "evidence": [
                {"content": "User reports acid reflux and burning sensation after meals", "pramana_type": "pratyaksha", "source": "User symptom report", "tags": ["pitta", "acid_reflux", "digestive"]},
                {"content": "Ayurvedic texts recommend ginger for digestive complaints", "pramana_type": "shabda", "source": "Bhavaprakasha Nighantu", "tags": ["ginger", "digestive", "heating"]},
                {"content": "Pitta-predominant prakriti inferred from assessment", "pramana_type": "anumana", "source": "BioRhythm engine", "tags": ["pitta"]},
            ],
        },
        {
            "id": "s4",
            "number": 4,
            "domain": "general",
            "title": "Lab overrides guideline",
            "subtitle": "Belief revision — Pratyaksha > Shabda",
            "claim": "The bridge is safe for continued use",
            "expected_verdict": "revised",
            "context": {
                "example": "When direct measurement contradicts published guidance, the measurement takes precedence in epistemic hierarchy.",
                "application": "The lab test (Pratyaksha, strength 4) directly contradicts the clinical guideline (Shabda, strength 2). By Nyaya hierarchy, direct perception overrides testimony.",
            },
            "existing_evidence": [
                {"content": "Clinical guideline states material is safe below 500 PSI", "pramana_type": "shabda", "source": "Engineering safety manual", "tags": ["safe", "bridge"]},
            ],
            "new_evidence": {
                "content": "Lab stress test shows micro-fractures at 450 PSI", "pramana_type": "pratyaksha", "source": "Lab test results", "tags": ["unsafe", "bridge", "fracture"],
            },
        },
        {
            "id": "s5",
            "number": 5,
            "domain": "general",
            "title": "Conflicting studies",
            "subtitle": "Honest uncertainty",
            "claim": "Screen time of 2+ hours daily harms children's development",
            "expected_verdict": "uncertain",
            "context": {
                "example": "Research on this topic shows genuinely conflicting results from credible sources.",
                "application": "A government-funded longitudinal study (Shabda) and a recent large-scale dataset analysis (Anumana) reach opposite conclusions. When credible sources conflict, intellectual honesty requires acknowledging uncertainty.",
            },
            "evidence": [
                {"content": "Government-funded 5-year study found significant developmental delays with 2+ hours screen time", "pramana_type": "shabda", "source": "NIH longitudinal study 2024", "tags": ["screen_time", "harmful", "children"]},
                {"content": "Meta-analysis of 50 studies shows no significant effect when controlling for socioeconomic factors", "pramana_type": "anumana", "source": "Oxford meta-analysis 2025", "tags": ["screen_time", "harmless", "children"]},
            ],
        },
    ]


def run_scenario(scenario: dict) -> dict:
    """Run a single scenario through both NyAI and Naive agents."""
    nyai = NyAIAgent()
    naive = NaiveAgent()

    now = datetime.now()

    # Build evidence objects
    if scenario["id"] == "s4":
        # Belief revision scenario
        existing_evidence = [
            Evidence(
                content=e["content"],
                pramana_type=PramanaType(e["pramana_type"]),
                source=e["source"],
                tags=e["tags"],
            )
            for e in scenario["existing_evidence"]
        ]
        ne = scenario["new_evidence"]
        new_evidence = Evidence(
            content=ne["content"],
            pramana_type=PramanaType(ne["pramana_type"]),
            source=ne["source"],
            tags=ne["tags"],
        )
        all_evidence = existing_evidence + [new_evidence]

        nyai_result = nyai.revise_belief(
            claim=scenario["claim"],
            existing_evidence=existing_evidence,
            new_evidence=new_evidence,
            context=scenario.get("context"),
        )
        naive_result = naive.evaluate_claim(scenario["claim"], all_evidence)

        # Add what naive missed
        naive_result["what_it_missed"] = [
            "Did not track evidence sources or their strength",
            "Cannot perform belief revision — new evidence is just more data",
            "Pratyaksha (lab test) contradicts Shabda (guideline) but naive agent ignores hierarchy",
        ]
    else:
        evidence_age = scenario.get("evidence_age_days", 0)
        evidence_timestamp = now - timedelta(days=evidence_age) if evidence_age else None

        evidence = [
            Evidence(
                content=e["content"],
                pramana_type=PramanaType(e["pramana_type"]),
                source=e["source"],
                tags=e["tags"],
                timestamp=evidence_timestamp if e["pramana_type"] == "pratyaksha" and evidence_age else None,
            )
            for e in scenario["evidence"]
        ]

        nyai_result = nyai.evaluate_claim(
            claim=scenario["claim"],
            evidence=evidence,
            context=scenario.get("context"),
            evidence_timestamp=evidence_timestamp,
        )
        naive_result = naive.evaluate_claim(scenario["claim"], evidence)

        # Add what naive missed per scenario
        missed_map = {
            "s1": [],  # Happy path — both agree
            "s2": [
                "No staleness check — 12-day-old data treated as current",
                "Would recommend a summer diet plan based on stale observations",
            ],
            "s3": [
                "No fallacy detection — ginger recommended despite Pitta + acid reflux",
                "No counter-case awareness — general rule blindly applied",
                "This recommendation could cause harm",
            ],
            "s5": [
                "Accepted the first piece of evidence without considering conflicts",
                "No mechanism to express genuine uncertainty",
                "Pramana gate would catch insufficient source diversity",
            ],
        }
        naive_result["what_it_missed"] = missed_map.get(scenario["id"], [])

    return {
        "scenario": {
            "id": scenario["id"],
            "number": scenario["number"],
            "domain": scenario["domain"],
            "title": scenario["title"],
            "subtitle": scenario["subtitle"],
            "claim": scenario["claim"],
            "expected_verdict": scenario["expected_verdict"],
        },
        "nyai_result": nyai_result,
        "naive_result": naive_result,
        "diverges": nyai_result.get("verdict") != naive_result.get("verdict"),
    }


def run_all_scenarios() -> list:
    """Run all 5 scenarios and return comparison results."""
    scenarios = get_scenarios()
    return [run_scenario(s) for s in scenarios]
