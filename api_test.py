import requests
  # the value from Secrets Manager
API_URL = os.environ['OCT7URL']
API_KEY = os.environ['OCT7KEY']
def send_records(records):
    response = requests.post(
        API_URL,
        json=records,
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
        }
    )
    response.raise_for_status()
    return response.json()
 
 
if __name__ == "__main__":
    test_record = [{
        "pid":         "TEST001",
        "firstNameHe": "בדיקה",
        "firstNameEn": "John",
        "lastNameHe":  "בדיקה",
        "lastNameEn":  "Cohen",
        "statusEn": ["killed", "kidnapped"],
        "statusHe": ["נהרג", "נחטף"],
        "eventDate": "2023-10-07",
        "deathDate":  "2023-10-07",
    }]
 
    print("Sending test record...")
    result = send_records(test_record)
    print("Response:", result)