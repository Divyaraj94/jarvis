import urllib.request
import json
response = urllib.request.urlopen('https://hacker-news.firebaseio.com/v0/topstories.json')
data = json.loads(response.read().decode())
for i in range(3):
    story_id = data[i]
    response = urllib.request.urlopen(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
    item_data = json.loads(response.read().decode())
    print(f"{item_data['title']}")