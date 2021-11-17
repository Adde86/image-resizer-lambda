terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.65.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
  shared_credentials_file = "C:\\Users\\adde\\.aws\\credentials"
}

resource "aws_s3_bucket" "input-bucket" {
  bucket = "image-resizer-input-bucket"
  acl = "private"
  server_side_encryption_configuration {
    rule {
     apply_server_side_encryption_by_default {
       
       sse_algorithm = "aws:kms"
      }
       bucket_key_enabled = true
    }
  }
 
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "PutObjectPolicy",
  "Statement": [
    {
      "Sid": "DenyIncorrectEncryptionHeader",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::image-resizer-input-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::image-resizer-input-bucket/*",
      "Condition": {
        "Null": {
          "s3:x-amz-server-side-encryption": "true"
        }
      }
    }
  ]
}
POLICY

}

resource "aws_s3_bucket_notification" "s3-notification" {
    bucket = aws_s3_bucket.input-bucket.id
  
    topic {
        topic_arn = aws_sns_topic.image-uploaded.arn
        events = ["s3:ObjectCreated:*"]
    }
  
}

resource "aws_s3_bucket" "output-bucket" {

     bucket = "image-resizer-output-bucket"
     acl = "private"
    server_side_encryption_configuration {
    rule {
     apply_server_side_encryption_by_default {
       
       sse_algorithm = "aws:kms"
      }
       bucket_key_enabled = true
    }
  }
     policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "PutObjectPolicy",
  "Statement": [
    {
      "Sid": "DenyIncorrectEncryptionHeader",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::image-resizer-output-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::image-resizer-output-bucket/*",
      "Condition": {
        "Null": {
          "s3:x-amz-server-side-encryption": "true"
        }
      }
    }
  ]
}
POLICY
     
}

data "archive_file" "zipit" {
  type = "zip"
  source_file = "app.py"
  output_path = "image_resizer.zip"
}

resource "aws_lambda_function" "image-resizer" {
  
  function_name = "app"
  handler = "app.image_resizer_handler"
  runtime = "python3.8"
  filename = "image_resizer.zip"
  source_code_hash = "${data.archive_file.zipit.output_base64sha256}"
  role = aws_iam_role.lambda-role.arn
  layers = [aws_lambda_layer_version.pillow.arn]
  
}

resource "aws_lambda_layer_version" "pillow" {
  layer_name = "pillow_layer"
  filename = "Klayers-python38-Pillow-b064ad60-1a98-4515-aefe-2c5b43311592.zip"
}


resource "aws_lambda_event_source_mapping" "event_source_mapping" {
  event_source_arn = "${aws_sqs_queue.image-queue.arn}"
  enabled          = true
  function_name    = "${aws_lambda_function.image-resizer.arn}"
  batch_size       = 1
}

resource "aws_iam_role" "lambda-role" {
  name = "lambda-role"

  assume_role_policy = jsonencode({
      Version = "2012-10-17"
      Statement = [{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid = ""
        Principal = {
            Service = "lambda.amazonaws.com"
        }
      }
      ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_policy" {
  
  role = aws_iam_role.lambda-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

}

resource "aws_iam_policy" "lambda_s3_queue_access" {
    name = "lambda-s3"
    description = "policy to allow lambda to retrieve from input bucket and put in outbutpucket and recieve messages from queue"
    path = "/"

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action =  [
                  "s3:GetObject*" 
                ]
                Effect = "Allow"
                Resource = "${aws_s3_bucket.input-bucket.arn}"
            },
            {
                Action = [
                  "s3:PutObject*"
                ],
                Effect = "Allow"
                Resource = "${aws_s3_bucket.output-bucket.arn}"
            },
            {
                Action = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
                Effect = "Allow"
                Resource = "${aws_sqs_queue.image-queue.arn}"
            }
        ]
    })
  
}

resource "aws_iam_role_policy_attachment" "lambda_s3_access" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda_s3_queue_access.arn
}

resource "aws_sns_topic" "image-uploaded" {
  name = "image-uploaded-topic"
  policy = <<POLICY
{
    "Version":"2012-10-17",
    "Statement":[{
        "Effect": "Allow",
        "Principal": { "Service": "s3.amazonaws.com" },
        "Action": "SNS:Publish",
        "Resource": "arn:aws:sns:*:*:image-uploaded-topic",
        "Condition":{
            "ArnLike":{"aws:SourceArn":"${aws_s3_bucket.input-bucket.arn}"}
        }
    }]
}
POLICY
}

 
resource "aws_sqs_queue" "image-queue" {
    name = "image-queue"
    policy = <<POLICY
{
  "Version": "2012-10-17",
  "Id": "Policy1637142052180",
  "Statement": [
    {
      "Sid": "Stmt1637142041381",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::977629633660:role/lambda-role"
      },
      "Action": [
        "sqs:CreateQueue",
        "sqs:DeleteMessage",
        "sqs:ReceiveMessage"
      ],
      "Resource": "arn:aws:sqs:eu-west-1:977629633660:image-queue"
    },
    {
      "Sid": "topic-subscription-arn:aws:sns:eu-west-1:977629633660:image-uploaded-topic",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:eu-west-1:977629633660:image-queue",
      "Condition": {
        "ArnLike": {
          "aws:SourceArn": "arn:aws:sns:eu-west-1:977629633660:image-uploaded-topic"
        }
      }
    }
  ]
}
POLICY
}

resource "aws_sns_topic_subscription" "sqs-subscription" {
    topic_arn = aws_sns_topic.image-uploaded.arn
    protocol = "sqs"
    endpoint = aws_sqs_queue.image-queue.arn

}

