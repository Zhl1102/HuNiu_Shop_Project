import requests

url = "http://127.0.0.1:8000/v1/users/hlzheng/address"
headers = {
    "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODA4NzU3NjMsInVzZXJuYW1lIjoiaGx6aGVuZyJ9.-7HCTpkv0xpVXaVgKTuFtDg_IL1FVRQgGX7xpw8u_Jk"
}
html = requests.get(url=url, headers=headers).json()
print(html)