import logging
import os

import boto3
import requests
from botocore.config import Config
from botocore.exceptions import ClientError

from utils.helpers import is_local, get_random_string

aws_config = Config(
    region_name='ap-east-1',
)


def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

    s3_client = boto3.client('s3', config=aws_config)

    if is_local(file_name):

        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = os.path.basename(file_name)

        # Upload the file

        try:
            response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read'})
        except ClientError as e:
            logging.error(e)
            raise e

    else:
        r = requests.get(file_name, stream=True)

        print('response headers', r.headers)

        if r.headers.get("content_type") == 'image/jpeg':
            object_name = get_random_string(16) + '.jpg'
        else:
            object_name = get_random_string(16) + '.png'

        print("object_name: ", object_name)

        try:
            response = s3_client.upload_fileobj(r.raw, bucket, object_name, ExtraArgs={'ACL': 'public-read'})
        except ClientError as e:
            logging.error(e)
            raise e

    return f"https://{bucket}.s3.ap-east-1.amazonaws.com/{object_name}"
