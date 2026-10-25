"""Offline demonstration using a frozen synthetic case and an actual recorded response.

No model call, database access, real publication, or record mutation is performed.
The correction is a simulated runtime observation, not independent test attestation.
"""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from nyai_research.contracts import adjudicate


def show_decision(record):
    result = adjudicate(record)
    print("Decision:", "PERMIT" if result["execute"] else "WITHHOLD")
    for check in result["checks"]:
        if check["status"] != "passed":
            print(f"  {check['rule_id']}: {check['status']} - {check['description']}")
    print("Record:", result["decision_record"]["application"])
    return result


def main():
    cases = [json.loads(line) for line in
             (ROOT / "data/fixtures/24_agentic_contract_cases.jsonl").read_text().splitlines()]
    case = next(row for row in cases if row["case_id"] == "AG-10-0")
    state = copy.deepcopy(case["state"])

    print("NyAI local demonstration")
    print("Synthetic facts; no API call or real action.\n")
    print("1. Check the grounds for an action")
    print("Requested action:", state["action"])
    print("Constructed candidate statement: Unit tests ran, so publication can proceed.")
    print("Claimed checks:", ", ".join(state["claimed_checks"]))
    print("Executed checks:", ", ".join(state["executed_checks"]) or "none")
    show_decision(state)

    print("\n2. Reevaluate after a simulated correction")
    corrected = copy.deepcopy(state)
    corrected["executed_checks"] = ["unit_tests"]
    print("Updated runtime record: unit_tests is now listed as executed.")
    show_decision(corrected)

    print("\n3. Withhold when a required fact is unknown")
    incomplete = copy.deepcopy(corrected)
    del incomplete["consent"]
    print("Consent is absent from the supplied record.")
    show_decision(incomplete)

    responses = [json.loads(line) for line in
                 (ROOT / "results/agentic_model_responses.jsonl").read_text().splitlines()]
    response = next(row for row in responses if row["case_id"] == case["case_id"])
    print("\nRecorded model comparison (replay, not a live generation)")
    print("Model:", response["returned_model"])
    print("Original-case decision:", "PERMIT" if response["parsed"]["execute"] else "WITHHOLD")
    print("Reason:", response["parsed"]["reason"])
    print("\nThe model also caught this defect; this example does not show a NyAI advantage.")
    print("The engine checks supplied facts. It does not independently verify that tests ran.")


if __name__ == "__main__":
    main()
