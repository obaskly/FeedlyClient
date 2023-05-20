import requests
import json

class FeedlyClient:
    def __init__(self, sandbox=True, additional_headers=None):
        self.client_id = 'FEEDLY_CLIENT_ID'
        self.client_secret = 'FEEDLY_CLIENT_SECRET'
        self.token = 'FEEDLY_API_TOKEN'
        self.sandbox = sandbox
        self.service_host = 'sandbox.feedly.com' if sandbox else 'cloud.feedly.com'
        self.additional_headers = additional_headers or {}

    def _get_endpoint(self, path=None):
        url = f"https://{self.service_host}"
        if path is not None:
            url += f"/{path}"
        return url

    def _make_request(self, method, endpoint, params=None, data=None, headers=None):
        url = self._get_endpoint(endpoint)
        headers = headers or {}
        if self.token:
            headers['Authorization'] = f'OAuth {self.token}'

        response = requests.request(method, url, params=params, json=data, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_code_url(self, callback_url):
        scope = 'https://cloud.feedly.com/subscriptions'
        response_type = 'code'
        
        request_url = f"{self._get_endpoint('v3/auth/auth')}?client_id={self.client_id}&redirect_uri={callback_url}&scope={scope}&response_type={response_type}"      
        return request_url
    
    def get_access_token(self, redirect_uri, code):
        return self._make_request('POST', 'v3/auth/token', params={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code
        })

    def refresh_access_token(self, refresh_token):
        return self._make_request('POST', 'v3/auth/token', params={
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        })
    
    def get_user_subscriptions(self):
        return self._make_request('GET', 'v3/subscriptions')

    def get_feed_content(self, streamId, unreadOnly=True, newerThan=None):
        return self._make_request('GET', 'v3/streams/contents', params={
            'streamId': streamId,
            'unreadOnly': unreadOnly,
            'newerThan': newerThan
        })

    def mark_article_read(self, entryIds):
        return self._make_request('POST', 'v3/markers', data={
            'action': "markAsRead",
            'type': "entries",
            'entryIds': entryIds
        }, headers={'content-type': 'application/json'})

    def save_for_later(self, user_id, entryIds):
        request_url = self._get_endpoint('v3/tags') + f'/user%2F{user_id}%2Ftag%2Fglobal.saved'
        return self._make_request('PUT', request_url, data={'entryIds': entryIds}, headers={'content-type': 'application/json'})
    
# Create a client instance
client = FeedlyClient()

# Get the user's subscriptions
subscriptions = client.get_user_subscriptions()

# Loop over the subscriptions
for subscription in subscriptions:
    # Get the id of the subscription
    stream_id = subscription['id']

    # Get the contents of the subscription
    content = client.get_feed_content(stream_id)

    # Print the title of each article in the feed
    for item in content['items']:
        print(item['title'])
