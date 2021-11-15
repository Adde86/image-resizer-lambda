import unittest
import image_resizer
import os.path
from PIL import Image

class TestImageResizer(unittest.TestCase):

    def test_get_message_from_event(self):
        event = {
            "Records": [
                {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": "Hello from SQS!",
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MyQueue",
                "awsRegion": "us-east-1"
                }
            ]
            }
       
       
        self.assertEqual("Hello from SQS!", image_resizer.get_message_body(event))

    def test_get_object_key(self):
        message =  {"Message": {"Records":
        [
            {"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"eu-west-1","eventTime":"2021-11-08T14:24:13.786Z","eventName":"ObjectCreated:Put","userIdentity":
            {"principalId":"AWS:AIDA6HH2ELR6FLRKZPDRT"},"requestParameters":
            {"sourceIPAddress":"83.250.50.237"},"responseElements":
            {"x-amz-request-id":"JESD39B3K59K0MMM","x-amz-id-2":"jrLUGV/vbu8DMRNzGNm1Halb1GHjPJk2HfF9NtY7jmouMfq1HfOIrF8JEpKVfLlrChgHZXeF4mvEtAxnB4yx9GWWo7p2wCDM"},
            "s3":{"s3SchemaVersion":"1.0","configurationId":"image-uploaded",
            "bucket":{"name":"image-resizer-images",
                "ownerIdentity":{"principalId":"A37DYUGILQ74GA"},
                "arn":"arn:aws:s3:::image-resizer-images"},
            "object":{"key":"test.jpg","size":85922,"eTag":"580560d0d6d70bacfa331380530d2f73","sequencer":"006189330DB73C3508"}}}
        ]}}

        self.assertEqual("test.jpg", image_resizer.get_object_key(message).get("key"))

    def test_get_object_from_s3(self):
        object_key = "lfc.jpg"
        bucket_name = "image-resizer-images"
        self.assertEqual("lfc.jpg", image_resizer.get_object_from_s3(object_key, bucket_name))

    def test_get_object_from_s3_file_not_found(self):
        object_key = "adafafafasf"
        bucket_name = "image-resizer-images"
        self.assertRaises(FileNotFoundError)

    def resize_image_test_thumbnail_file_created(self):
        image = Image.open("lfc.jpg", 'r')
        image_resizer.resize_image(image)
              
        self.assertTrue(os.path.exists("lfc_thumb.jpg"))

    def test_image_rename(self):
        self.assertEqual("lfc_thumb.jpg", image_resizer.rename_file("lfc.jpg"))

    def test_save_object_to_s3(self):
        with open("lfc.jpg", 'rb') as file:
            self.assertTrue(image_resizer.save_resized_image("image-resizer-images",image_resizer.resize_image(file)))
        



if __name__ == '__main__':
    unittest.main()