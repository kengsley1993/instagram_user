# Instagram Crawler User Profile v0.1

## Purpore
Create a crawler to download Profile detail into local folder via the usename or useid.

## Usage
*   Python 3.6
*   urllib
*   pyquery
*   PyMySQL
*   MySQL
*   pyspider
*   Scrapy

## Setup
Create a project folder:
```bash
scrapy startproject instagram_user
```
Create a spider crawl into project folder:
```bash
scrapy spider user_crawler www.instagram.com
```

## Information
The information need to crawl:

*   user's id
*   username
*   post's id
*   post's liked
*   post's caption
*   post's commit count
*   post's images and videos

## Project
### 1. Spider (user_crawler)
#### 1.1 Send Requests
Capture the user information from 'https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables={'id':{userid},'first':'12','after':{after_string}}'
It will return a json data.
```python
base_url = 'https://www.instagram.com/graphql/query/?'
if settings.USERID is '':
    find_id_url = 'https://www.instagram.com/' + settings.USERNAME
    response = requests.get(find_id_url, headers=headers)
    result = re.search('"profilePage_(.*?)"', response.text)
    settings.USERID = result[1]

param = {
    'query_hash': 'e769aa130647d2354c40ea6a439bfc08',
    'variables': '{"id":"'+ settings.USERID +'","first":12}',
}

def start_requests(self):
    url = self.base_url + urlencode(self.param)
    yield Request(url, headers=headers, callback=self.parse)
```

#### 1.2 Data Collect
Decoding the response by using json format:
```python
data_json = json.loads(response.text)
data = data_json.get('data').get('user').get('edge_owner_to_timeline_media')
```

#### 1.3 Store Item
Collect the data json into own database settings format for store into mysql and download images and videos in local folder.
```python
for user_detail in data.get('edges'):
    user_node = user_detail.get('node')
    item = InstagramUserItem()
    item['postid'] = user_node.get('id')
    item['username'] = user_node.get('owner').get('username')
    if settings.USERNAME is '':
        settings.USERNAME = user_node.get('owner').get('username')
    item['userid'] = user_node.get('owner').get('id')
    item['liked'] = user_node.get('edge_media_preview_like').get('count')
    try:
        item['caption'] = user_node.get('edge_media_to_caption').get('edges')[0].get('node').get('text')
    except:
        item['caption'] = ''
    item['comment'] = user_node.get('edge_media_to_comment').get('count')

    video_link = ''
    images_link = ''
    if user_node.get('edge_sidecar_to_children'):
        child_edges = user_node.get('edge_sidecar_to_children').get('edges')
        for child in child_edges:
            node = child.get('node')
            if user_node.get('is_video'):
                # get video link
                video_link += node.get('video_url')+';'
            else:
                images_link += node.get('display_url')+';'
    else:
        if user_node.get('is_video'):
            video_link = user_node.get('video_url')+';'
        else:
            images_link = user_node.get('display_url')+';'
    item['image_list'] = images_link
    item['video_list'] = video_link

    yield item
```
Get the next page and recall the request:
```python
page_info = data.get('page_info')
if page_info.get('has_next_page'):
    temp_variables = json.loads(self.param.get('variables'))
    temp_variables['after'] = page_info.get('end_cursor')
    self.param['variables'] = json.dumps(temp_variables)
    url = self.base_url + urlencode(self.param)
    yield Request(url, headers=headers, callback=self.parse)
```

### 2. Items
Setup the data elements for data storing and usage in item pipeline.
```python
collection = table = 'user_post'
postid = Field()
userid = Field()
username = Field()
liked = Field()
caption = Field()
comment = Field()
image_list = Field()
video_list = Field()
```

### 3. Pipelines
#### 3.1 FilePipeline
Download the videos or images and store into local folder.
```python
def file_path(self, request, response=None, info=None):
    file_name = settings.USERNAME + '/' + os.path.basename(urlparse(request.url).path)
    return file_name

def item_completed(self, results, item, info):
    image_paths = [x['path'] for ok, x in results if ok]
    if not image_paths:
        raise DropItem('Image Downloaded Failed')
    return item

def get_media_requests(self, item, info):
    for url in item['image_list'].split(';'):
        yield Request(url)
    for url in item['video_list'].split(';'):
        yield Request(url)
```
#### 3.2 MySQL Pipeline (Future)

### 4. Settings
Enter username or userid to caption the profile:
```python
USERID = '[Enter instagram userid]'
USERNAME = '[Enter instagram username]'
```
Setup the item pipelines:
```python
ITEM_PIPELINES = {
   'instagram_user.pipelines.FilePipeline': 301,
}

FILES_STORE = './user'
```

## Run
Start the crawler, store the image and information into local
```bash
scrapy crawl user_crawler
```
