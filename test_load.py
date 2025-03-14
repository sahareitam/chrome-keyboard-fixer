import requests
import threading
import time

def send_request():
    try:
        response = requests.post(
            "http://localhost:5000/api/convert",
            json={"text": "שלום עולם"},
            timeout=5
        )
        print(f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Send 50 concurrent requests
threads = []
for i in range(50):
    t = threading.Thread(target=send_request)
    threads.append(t)
    t.start()
    time.sleep(0.05)  # Small delay between thread starts

# Wait for all threads to complete
for t in threads:
    t.join()