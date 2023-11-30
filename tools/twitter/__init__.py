import os
import time
from datetime import datetime

import requests
from requests_oauthlib import OAuth1Session

from utils.retry import retry

oauth: OAuth1Session = OAuth1Session(
    os.getenv("TWEETER_API_KEY"),
    client_secret=os.getenv("TWEETER_SECRET_KEY"),
    resource_owner_key=os.getenv("TWEETER_ACCESS_TOKEN"),
    resource_owner_secret=os.getenv("TWEETER_ACCESS_TOKEN_SECRET"),
)


class Twitter:
    async def publish_tweet(self, tweet, media=None) -> dict:
        print("tweet: ", tweet)
        print("media: ", media)
        data = {"text": tweet}

        if media is not None:
            image_id = await self.upload_image(media)
            data['media'] = {
                "media_ids": [str(image_id)]
            }

        # Making the request
        response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=data
        )

        if response.status_code != 201:
            raise Exception(
                "Request returned an error: {} {}".format(response.status_code, response.text)
            )

        print("Response code: {}".format(response.status_code))

        # Saving the response as JSON
        json_response = response.json()

        json_response['created_at'] = datetime.now().isoformat()

        return json_response

    @retry(max_attempts=3, delay_seconds=2)
    async def upload_image(self, image_url):

        total_bytes = requests.head(image_url).headers['content-length']
        data = {
            "command": "INIT",
            "media_type": "image/*",
            "total_bytes": int(total_bytes),
            "media_category": "tweet_image"
        }

        print(data)

        init_response = oauth.post(
            url="https://upload.twitter.com/1.1/media/upload.json",
            data=data,
        )

        print("init_response", init_response.text)

        media_id = init_response.json()['media_id']

        self._process_file(image_url, media_id)
        print("complete upload")

        self._finalize_upload(media_id)
        print("finalised")

        return media_id

    def _segment_file(self, file_url, chunk_size=1024 * 1024):  # 1MB
        response = requests.get(file_url, stream=True)
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:  # End of file
                break
            yield chunk

    def _send_chunk(self, chunk, chunk_count, media_id):
        data = {
            "command": "APPEND",
            "media_id": media_id,
            "segment_index": chunk_count
        }
        print("chunk: ", data)
        response = oauth.post("https://upload.twitter.com/1.1/media/upload.json",
                              data=data,
                              files={'media': chunk})
        return response.status_code

    def _process_file(self, file_url, media_id):
        chunk_count = 0
        for chunk in self._segment_file(file_url):
            status_code = self._send_chunk(chunk, chunk_count, media_id)
            chunk_count += 1
            print(f"Chunk sent with status code: {status_code}")

    def _finalize_upload(self, media_id):
        response = oauth.post("https://upload.twitter.com/1.1/media/upload.json",
                              data={
                                  "command": "FINALIZE",
                                  "media_id": media_id
                              })

        print('finalize response: ', response.json())

        if response.json().get('processing_info'):
            return self._check_status(media_id)

        return True

    def _check_status(self, media_id):
        response = oauth.get("https://upload.twitter.com/1.1/media/upload.json",
                             params={
                                 "command": "STATUS",
                                 "media_id": media_id
                             })

        print("check status: ", response.json())

        data = response.json()
        if data.get('processing_info'):
            if data['processing_info']['state'] == 'succeeded':
                return True
            elif data['processing_info']['state'] == 'failed':
                print(data['processing_info']['error'])
                return False
            else:
                time.sleep(data['processing_info']['check_after_secs'])
                return self._check_status(media_id)
        else:
            return True
