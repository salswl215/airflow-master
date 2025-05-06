import requests
# client_id, authorize_code 노출 주의, 실제 값은 임시로만 넣고 Git에 올라가지 않도록 유의

client_id = '2396b69529de66e1cab1759c9774fb21'
redirect_uri = 'https://example.com/oauth'
authorize_code = 'W1XO-xsf4jYxCYtapfgwL1xMQ4DygB2tynkqKNs6Wc4apHCCo-CxGwAAAAQKFxafAAABlqSjgwvkNSpXBP-m7Q'


token_url = 'https://kauth.kakao.com/oauth/token'
data = {
    'grant_type': 'authorization_code',
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'code': authorize_code,
    }

response = requests.post(token_url, data=data)
tokens = response.json()
print(tokens)