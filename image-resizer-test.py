import unittest
from app import image_resizer_handler
import app as image_resizer
import os.path
from PIL import Image


class TestImageResizer(unittest.TestCase):

   


    def test_get_object_from_s3(self):
        object_key = "lfc.jpg"
        bucket_name = "image-resizer-images"
        self.assertEqual("tmp/lfc.jpg", image_resizer.get_object_from_s3(object_key, bucket_name))

    def test_get_object_from_s3_file_not_found(self):
        object_key = "adafafafasf"
        bucket_name = "image-resizer-images"
        self.assertRaises(FileNotFoundError)

    def resize_image_test_thumbnail_file_created(self):
        image = Image.open("lfc.jpg", 'r')
        image_resizer.resize_image(image)
              
        self.assertTrue(os.path.exists("lfc_thumb.jpg"))

    def test_image_rename(self):
        self.assertEqual("tmp/lfc_thumb.jpg", image_resizer.rename_file("tmp/lfc.jpg"))

    def test_save_object_to_s3(self):
        with open("tmp/lfc.jpg", 'rb') as file:
            self.assertTrue(image_resizer.save_resized_image("image-resizer-images",image_resizer.resize_image(file)))
        

    def test_script(self):
        event = {
        'Records': [{'messageId': '982e4071-77eb-4948-8415-a8d6f3f72a21', 'receiptHandle': 'AQEByneZZx5BloTBwBnRfHGpLCoYDCzgpFJ+OMN9XvLLLo/PiCbL3ke2qNJHkPuiTJnEmJyzzO7ySnkF+AMeZLMhFS7YZmHuXtEISsZs+cR7QdvmKrC+lzh3MdS5fYySkldvFvIn27VpkyIZH/ybOd5AY9r2auD2+dhUrSixgJkn3rpLrp4cCCSU0E5o7NNlAGvCiKjb51z1jiD69nflVz90Z5Te0Vpj9f1zt+xmAAdfn1uZuiZBqWlSxe89RM35Bn+H3WDvP6A625DCoQsDA+tnN8ZpRcGTE7u2HbZ+irgBoLkRzfPpZFwpCEImfQNtqcMcGmKjT9CQ7rIC9/jtI6gXqWlUSc6cBt13befeVDbFYPzN79kyth6fpcevp5zfnPNQVZ+RccGBWWFV8TpJomMLjg==', 'body': '{\n  "Type" : "Notification",\n  "MessageId" : "93cff531-1a46-530f-b664-af3fe8651232",\n  "TopicArn" : "arn:aws:sns:eu-west-1:977629633660:image-uploaded-topic",\n  "Subject" : "Amazon S3 Notification",\n  "Message" : "{\\"Records\\":[{\\"eventVersion\\":\\"2.1\\",\\"eventSource\\":\\"aws:s3\\",\\"awsRegion\\":\\"eu-west-1\\",\\"eventTime\\":\\"2021-11-17T12:04:50.176Z\\",\\"eventName\\":\\"ObjectCreated:Put\\",\\"userIdentity\\":{\\"principalId\\":\\"AWS:AIDA6HH2ELR6FLRKZPDRT\\"},\\"requestParameters\\":{\\"sourceIPAddress\\":\\"83.250.50.237\\"},\\"responseElements\\":{\\"x-amz-request-id\\":\\"2T65SHRTFRTVN8ZE\\",\\"x-amz-id-2\\":\\"mkN5RxUturV1p0vhBkhdSRznUW7o2dGyy7uphsSbyJBIn6/Ia6KhGIR4JlOKaCvblwoKcx7vwiErwPcq6TDPhs/tvJ99Akod\\"},\\"s3\\":{\\"s3SchemaVersion\\":\\"1.0\\",\\"configurationId\\":\\"tf-s3-topic-20211117085951053800000003\\",\\"bucket\\":{\\"name\\":\\"image-resizer-input-bucket\\",\\"ownerIdentity\\":{\\"principalId\\":\\"A37DYUGILQ74GA\\"},\\"arn\\":\\"arn:aws:s3:::image-resizer-input-bucket\\"},\\"object\\":{\\"key\\":\\"1194786_527386_635904744488623840.jpg\\",\\"size\\":85922,\\"eTag\\":\\"580560d0d6d70bacfa331380530d2f73\\",\\"sequencer\\":\\"006194EFE21742EC44\\"}}}]}",\n  "Timestamp" : "2021-11-17T12:04:51.193Z",\n  "SignatureVersion" : "1",\n  "Signature" : "Cm94m8Ra4bCMmutH37stjL814Oq4UvpPiOug7NXd91UMCFb6MQNpvOPwgMGjMIHmJWnk6ySlfxEhArHX4johirB35D302gMDIaYctdkS9DRkukJNYA0djbuWUc/0uLWfXsFmftiuDO8wtg3oLU9rJ067+6WZDirjanM/wn889kBPd/g+Cc1QQo3L4kvYT8kGAjhg5Bv0JY/Y28RBlJyoLxJlMUHrT86FaFMHvJDQ/RiM99A2O1qZ5/Pjgm90jCJry7EPzw7R3hIqtZqSGRiNXvgwo6bqdMb6CTEox2VIyUJplH81Qv2W6UYMFrxKUeZStT9QJpeBaN6SDcAl1oC3XA==",\n  "SigningCertURL" : "https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-7ff5318490ec183fbaddaa2a969abfda.pem",\n  "UnsubscribeURL" : "https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-1:977629633660:image-uploaded-topic:a316f069-df1c-48e0-a73b-1618c074f15a"\n}', 'attributes': {'ApproximateReceiveCount': '8', 'SentTimestamp': '1637150691226', 'SenderId': 'AIDAISMY7JYY5F7RTT6AO', 'ApproximateFirstReceiveTimestamp': '1637150691226'}, 'messageAttributes': {}, 'md5OfBody': '4e392c1085ea5e367ae1539118d5fd03', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:eu-west-1:977629633660:image-queue', 'awsRegion': 'eu-west-1'}]}
        
        image_resizer.image_resizer_handler(event, None)
       


if __name__ == '__main__':
    unittest.main()



 