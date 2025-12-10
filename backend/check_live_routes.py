import requests

# Test if server is running
health = requests.get('http://localhost:8000/api/v1/health')
print(f'Server health: {health.status_code} - {health.json()}')

# Test auth (known to work)
login = requests.post('http://localhost:8000/api/v1/auth/login',
    json={'email': 'admin@example.com', 'password': 'admin123'})
print(f'\nLogin: {login.status_code}')
token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test existing user route (known to work)
company = requests.get('http://localhost:8000/api/v1/user/company', headers=headers)
print(f'/user/company: {company.status_code}')

# Test operational indicators
operational = requests.get('http://localhost:8000/api/v1/user/operational-indicators?limit=20', headers=headers)
print(f'/user/operational-indicators: {operational.status_code}')
if operational.status_code != 200:
    print(f'  Error: {operational.text}')
else:
    data = operational.json()
    print(f'  Success! Total: {data["total"]} indicators')
