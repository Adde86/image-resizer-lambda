from functools import update_wrapper
from genericpath import exists, isfile
from io import BufferedReader, BytesIO
import boto3
import os
from PIL import Image
import re
import logging
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
upload_bucket = "image-resizer-upload-bucket"
    
def image_resizer_handler(event, context):
    body = get_message_body(event)
    s3_object_from_event = get_object_key(body)
    image = get_object_from_s3(s3_object_from_event.get("key"), s3_object_from_event.get("bucket"))
    with open(image) as file:
        new_name = resize_image(file)
    save_resized_image(bucket_name=upload_bucket, image=new_name)

   
def get_message_body(event):
    records = event.get("Records")
    return records[0].get("body")

def get_object_key(message:dict):
    message = message.get("Message")
    records = message.get("Records")
    object =  records[0].get("s3").get("object")
    bucket = records[0].get("s3").get("bucket").get("name")
    return {"key": object.get("key"), "bucket_name": bucket}

def get_object_from_s3(object_key, bucket_name):
    s3.download_file(bucket_name, object_key, object_key)
    if os.path.exists(object_key):
        return object_key
    else:
        raise FileNotFoundError("No such file")

def resize_image(image_file:BufferedReader):

    image = Image.open(image_file)
    resized = image.resize(size=[100,100])
    new_name = rename_file(image_file.name)
    resized.save(new_name)
    return new_name

def rename_file(file_name:str):
   return re.sub(r"([\w]*)(\.[a-z]*$)", r"\1_thumb.jpg", file_name)

def save_resized_image(bucket_name:str ,image:str):
    try:
        s3.upload_file(image, bucket_name, image)
    except ClientError as e:
        logging.error(e)
        return False
    return True
    