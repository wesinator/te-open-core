# Total Email Core API

## Adding New Endpoints

To add a new API endpoint:

0. Write tests for it.
1. Create a serializer for the model if one does not exist.
2. Add a url path for the endpoint.
3. Write a view class (or function) for the endpoint.
4. Retest everything and get it working properly.

## Making a Request

### Authorization

```
import requests
base_url = 'http://localhost:8000'

# the token below is created from a registered user's profile (/accounts/me)
headers = {'Authorization': 'Token 1234567890987654321'}
r = requests.get(base_url + '/api/v1/emails/', headers=headers)
print(r)
print(r.text)
```
