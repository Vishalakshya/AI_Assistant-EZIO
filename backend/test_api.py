import requests
import json

url = "http://localhost:8000/api/v1/chat/message"
headers = {"Content-Type": "application/json"}

# Test get_system_stats
print("Testing get_system_stats...")
res = requests.post(url, headers=headers, json={"message": "What are my system stats?"})
print(res.status_code, res.text)

# Test browser_search
print("\nTesting browser_search...")
res = requests.post(url, headers=headers, json={"message": "Search the web for python releases."})
print(res.status_code, res.text)

# Test get_running_processes
print("\nTesting get_running_processes...")
res = requests.post(url, headers=headers, json={"message": "What processes are running?"})
print(res.status_code, res.text)

