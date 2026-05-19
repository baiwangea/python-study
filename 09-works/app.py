import requests

headers = {"Accept": "application/json"}
data = {'mchOrderNo': 'VIP20251004202034583', 'amount': 2990}
resp = requests.post("http://16.162.188.178:59596/mobile/api/mock/callback", headers=headers, data=data, timeout=5)
print(resp.status_code, resp.text)