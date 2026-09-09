import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoints():
    print("--- 1. Testing /health ---")
    r = requests.get(f"{BASE_URL}/health")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print("\n--- 2. Testing /stats ---")
    r = requests.get(f"{BASE_URL}/stats")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print("\n--- 3. Testing /documents ---")
    r = requests.get(f"{BASE_URL}/documents")
    print(r.status_code, f"Found {len(r.json())} documents")
    assert r.status_code == 200
    for doc in r.json():
        print(f" - {doc['title']} ({doc['file_type']}, {doc['pages']} pages, {doc['chunks']} chunks)")

    print("\n--- 4. Testing Supported Query (PMFBY Claim) ---")
    payload_supported = {
        "query": "What is the PMFBY claim settlement procedure and deadline?",
        "language": "en"
    }
    r = requests.post(f"{BASE_URL}/chat", json=payload_supported, timeout=60)
    print(r.status_code)
    data = r.json()
    print("Status:", data.get("status"))
    print("Confidence:", data.get("confidence"))
    print("Intent:", data.get("intent"))
    print("Answer excerpt:", (data.get("answer") or "")[:150])
    print("Sources count:", len(data.get("sources", [])))
    for s in data.get("sources", []):
        print(f"   * {s['document']} (Page {s['page']}, {s['section']})")
    assert data.get("status") == "SUPPORTED"
    assert data.get("confidence") >= 0.75
    assert len(data.get("sources")) > 0

    print("\n--- 5. Testing Unsupported Query (Loan waiver without records) ---")
    payload_unsupported = {
        "query": "Can I get a loan waiver of 10 lakh rupees without land records under government scheme?",
        "language": "en"
    }
    r = requests.post(f"{BASE_URL}/chat", json=payload_unsupported, timeout=60)
    print(r.status_code)
    data2 = r.json()
    print("Status:", data2.get("status"))
    print("Confidence:", data2.get("confidence"))
    print("Ticket ID:", data2.get("ticket_id"))
    print("Reason:", data2.get("reason"))
    print("Answer (should be None):", data2.get("answer"))
    assert data2.get("status") == "ESCALATED"
    assert data2.get("ticket_id") is not None
    assert data2.get("answer") is None

    print("\n--- 6. Verifying Created Grievance Ticket in /tickets ---")
    ticket_id = data2.get("ticket_id")
    r = requests.get(f"{BASE_URL}/tickets/{ticket_id}", timeout=15)
    print(r.status_code, r.json()["id"], r.json()["status"])
    assert r.status_code == 200
    assert r.json()["id"] == ticket_id

    print("\n--- 7. Testing Officer Status Resolution ---")
    r = requests.patch(
        f"{BASE_URL}/tickets/{ticket_id}",
        json={"status": "UNDER_REVIEW", "officer_notes": "Assigned to Block Agriculture Officer for verification."},
        timeout=15
    )
    print(r.status_code, r.json()["status"], "Notes:", r.json()["officer_notes"])
    assert r.status_code == 200
    assert r.json()["status"] == "UNDER_REVIEW"

    print("\n=======================================================")
    print("ALL 7 API VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    test_endpoints()
