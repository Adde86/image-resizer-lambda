terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.65.0"
    }
  }
}

provider "aws" {
  region = "eu_west_1"
  shared_credentials_file = "C:\\Users\\adde\\.aws\\credentials"
}

resource "aws_kms_key" "bucket_kms" {
  description             = "This key is used to encrypt bucket objects"
  deletion_window_in_days = 10
}

resource "aws_s3_bucket" "input-bucket" {
  bucket = "input-bucket"
  acl = "private"

  server_side_encryption_configuration {
    rule {
        apply_server_side_encryption_by_default {
            kms_master_key_id = aws_kms_key.bucket_kms.arn
            sse_algorithm = "aws:kms"
        }
    }
  }
}

resource "aws_s3_bucket_notification" "s3-notification" {
    bucket = aws_s3_bucket.input-bucket.id

    topic {
        topic_arn = aws_sns_topic.image-uploaded.arn
        events = ["s3:ObjectCreated:*"]
    }
  
}

resource "aws_s3_bucket" "output-bucket" {

     bucket = "output-bucket"
     acl = "private"

  server_side_encryption_configuration {
    rule {
        apply_server_side_encryption_by_default {
            kms_master_key_id = aws_kms_key.bucket_kms.arn
            sse_algorithm = "aws:kms"
        }
    }
  }
}

resource "aws_lambda_function" "image-resizer" {
  
  function_name = "image_resizer"
  handler = "image_resizer_handler"
  runtime = "python3.9"
  role = aws_iam_role.lambda-role.arn

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
                Action = [
                    "s3:GetObject"
                ]
                Effect = "Allow"
                Resouce = "${aws_s3_bucket.input-bucket.arn}"
            },
            {
                Action = [
                    "s3:PutObject"
                ]
                Effect = "Allow"
                Resource = "${aws_s3_bucket.output-bucket.arn}"
            },
            {
                Action = [
                    "sqs:ReceiveMessage"
                ]
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
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Principal": {
                  "Service": "s3.amazonaws.com"
              },
              "Action": "SNS:Publish",
              "Resource": "arn:aws:sns:*:*:image-uploaded-topic",
              "Condition": {
                  "ArnLike": "{
                      "aws:SourceArn": "${aws_s3_bucket.input-bucket.arn}"
                  }
              }
          }
      ]
  }
  POLICY
}


resource "aws_sqs_queue" "image-queue" {
    name = "image-queue"
    kms_master_key_id = "alias/aws/sqs"
}

resource "aws_sns_topic_subscription" "sqs-subscription" {
    topic_arn = aws_sns_topic.image-uploaded.arn
    protocol = "sqs"
    endpoint = aws_sqs_queue.image-queue.arn

}