from functools import update_wrapper
from genericpath import exists, isfile
from io import BufferedReader, BytesIO
import boto3
import os
from PIL import Image
import re
import logging
from botocore.exceptions import ClientError
import json

s3 = boto3.client("s3")
upload_bucket = "image-resizer-output-bucket"
    
def image_resizer_handler(event, context):
    
    record = event['Records'][0]
    body = json.loads(record['body'].strip('\n'))
    bodyMessage = json.loads(body['Message'])
    message_record =bodyMessage['Records']
    bucket_name = message_record[0]['s3']['bucket']['name']
    object_key = message_record[0]['s3']['object']['key']
    
    
    image = get_object_from_s3(object_key, bucket_name)
        
    with open(image, "rb") as file:
        
         new_name = resize_image(file)
         response = save_resized_image(bucket_name=upload_bucket, image=new_name)
         return response


def get_object_from_s3(object_key, bucket_name):
    s3.download_file(bucket_name, object_key, "/tmp/"+object_key)
    if os.path.exists("/tmp/"+object_key):
        return "/tmp/"+object_key
    else:
        raise FileNotFoundError("No such file")

def resize_image(image_file:BufferedReader):

    image = Image.open(image_file)
    resized = image.resize(size=[100,100])
    new_name = rename_file(image_file.name)
    resized.save(new_name)
    
    return new_name
    

def rename_file(file_name:str):
   return re.sub(r"(/tmp/)([\w]*)(\.[a-z]*$)", r"\1\2_thumb.jpg", file_name)
  

def save_resized_image(bucket_name:str ,image:str):
    try:
       response = s3.upload_file(image, bucket_name, os.path.basename(image), ExtraArgs={"ServerSideEncryption": "AES256"})
       return True
    except ClientError as e:
        logging.error(e)
        return False
    


