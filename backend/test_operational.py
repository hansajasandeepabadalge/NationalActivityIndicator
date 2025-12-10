import requests

# Login
r = requests.post('http://localhost:8000/api/v1/auth/login', json={'email': 'admin@example.com', 'password': 'admin123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test operational indicators endpoint
resp = requests.get('http://localhost:8000/api/v1/user/operational-indicators?limit=20', headers=headers)
print(f'Status: {resp.status_code}')

if resp.status_code == 200:
    data = resp.json()
    print(f'Company: {data["company_id"]}')
    print(f'Total: {data["total"]}')
    print(f'Critical: {data["critical_count"]}')
    print(f'\nFirst 5 indicators:')
    for ind in data.get('indicators', [])[:5]:
        print(f'  - {ind["indicator_name"]}: {ind["current_value"]:.1f} ({ind["company_id"]})')
else:
    print(f'Error: {resp.text}')
