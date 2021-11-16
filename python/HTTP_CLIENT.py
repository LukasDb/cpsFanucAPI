import requests
import time

# api-endpoint
URL = "http://127.0.0.1/KAREL/rsiposition"

# defining a params dict for the parameters to be sent to the API
PARAMS = {}

start = time.perf_counter()
# sending get request and saving the response as response object
r = requests.get(url=URL, params=PARAMS)
# extracting data in json format
data = r.json()
print(f"Completed Execution in {(time.perf_counter() - start) * 1000} ms")

print(data)