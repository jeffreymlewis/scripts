"""Unittests for sns_to_cloudwarch_logs
"""
import datetime
import os
import unittest

from unittest import mock

import lambda_sns_to_cloudwatch_logs

# TODO: Testing the lambda_handler() requires mocking the aws calls, which I
# don't have time for right now. :(

# class TestLambdaHandler(unittest.TestCase):
#   def setUp(self) -> None:
#     self.event = {
#       'Records': [
#         {
#           'Sns': {
#             'Message': 'Hello from SNS!',
#             'TopicArn': 'arn:aws:sns:us-east-2:123456789012:sns-lambda',
#             'Timestamp': "2019-01-02T12:45:07.000Z",
#           }
#         }
#       ]
#     }

#   def test_inputExists(self):
#     self.assertIsNotNone(self.event)

#   def test_inputEventType(self):
#     self.assertIsInstance(self.event, dict)

#   def test_inputEventRecordsType(self):
#     self.assertIsInstance(self.event['Records'], list)

#   def test_inputEventRecordsElementType(self):
#     self.assertIsInstance(self.event['Records'][0], dict)

#   def test_inputEventRecordsSnsType(self):
#     self.assertIsInstance(self.event['Records'][0]['Sns'], dict)

#   def test_inputEventRecordsSnsMessageType(self):
#     self.assertIsInstance(self.event['Records'][0]['Sns']['Message'], str)

#   def test_inputEventRecordsSnsTopicArnType(self):
#     self.assertIsInstance(self.event['Records'][0]['Sns']['TopicArn'], str)

#   def test_inputEventRecordsSnsTopicArnNumElements(self):
#     arn_parts = self.event['Records'][0]['Sns']['TopicArn'].split(':')
#     self.assertEqual(len(arn_parts), 6)

#   def test_inputEventRecordsSnsTimestampType(self):
#     self.assertIsInstance(datetime.datetime.fromisoformat(
#       self.event['Records'][0]['Sns']['Timestamp']), datetime.datetime)


class TestIsoToEpochMs(unittest.TestCase):
  """Test the iso_to_epoch_ms() function.
  """
  def setUp(self):
    self.iso_datetime = '2019-01-02T12:45:07.000Z'
    self.expected_epoch = 1546433107000

  def test_input_exists(self):
    self.assertIsNotNone(self.iso_datetime)

  def test_input_type(self):
    self.assertIsInstance(self.iso_datetime, str)

  def test_input_is_iso_format(self):
    self.assertIsInstance(datetime.datetime.fromisoformat(self.iso_datetime),
                          datetime.datetime)

  def test_output_type(self):
    epoch = lambda_sns_to_cloudwatch_logs.iso_to_epoch_ms(self.iso_datetime)
    self.assertIsInstance(epoch, int)

  def test_output_expected(self):
    epoch = lambda_sns_to_cloudwatch_logs.iso_to_epoch_ms(self.iso_datetime)
    self.assertEqual(epoch, self.expected_epoch)


@mock.patch.dict(os.environ,
                 {'CLOUDWATCH_LOG_GROUP_NAME': 'valid-cloudwatch_logs#name'})
class TestGetLogGroupName(unittest.TestCase):
  """Test the get_log_group_name() function
  """
  def setUp(self):
    self.env_var_name = 'CLOUDWATCH_LOG_GROUP_NAME'

  def test_input_exists(self):
    self.assertIn(self.env_var_name, os.environ)

  def test_input_type(self):
    self.assertIsInstance(os.environ[self.env_var_name], str)

  def test_output_type(self):
    name = lambda_sns_to_cloudwatch_logs.get_log_group_name()
    self.assertIsInstance(name, str)

  def test_output_length(self):
    name = lambda_sns_to_cloudwatch_logs.get_log_group_name()
    self.assertGreaterEqual(len(name), 1)
    self.assertLessEqual(len(name), 512)

  def test_raises_exception(self):
    with mock.patch.dict('os.environ'):
      del os.environ[self.env_var_name]
      self.assertRaisesRegex(
        lambda_sns_to_cloudwatch_logs.MissingEnvironmentVariableException,
        f'{self.env_var_name} does not exist',
        lambda_sns_to_cloudwatch_logs.get_log_group_name
      )


if __name__ == '__main__':
  unittest.main()
