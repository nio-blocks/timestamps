import datetime
from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..elapsed_time_block import ElapsedTime


class TestElapsedTime(NIOBlockTestCase):

    # define a timestamp in the past
    dummy_timestamp = '1970-01-01T00:00:00.000000Z'
    dummy_timestamp_obj = datetime.datetime.strptime(
        dummy_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    # define a value for the current time during testing
    mock_current_time = dummy_timestamp_obj + datetime.timedelta(seconds=3.14)

    @patch('datetime.datetime')
    def test_local_timestamp(self, mock_datetime):
        """ The time elapsed since an input timestamp is returned."""
        mock_datetime.now.return_value = self.mock_current_time
        mock_datetime.strptime.return_value = self.dummy_timestamp_obj
        delta = (self.mock_current_time - self.dummy_timestamp_obj)
        # all values are expected as floats with no config
        elapsed = dict(days=delta.days,
                       hours=delta.total_seconds() / 60 ** 2,
                       minutes=delta.total_seconds() / 60,
                       seconds=delta.total_seconds())

        blk = ElapsedTime()
        self.configure_block(blk, {})
        blk.start()
        blk.process_signals([Signal({'timestamp': self.dummy_timestamp})])
        blk.stop()
        # current time is checked once per signal list
        mock_datetime.now.assert_called_once_with()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'timestamp': self.dummy_timestamp, 'elapsed': elapsed})

    @patch('datetime.datetime')
    def test_utc_timestamp(self, mock_datetime):
        """ UTC time is used for comparison instead of local time."""
        blk = ElapsedTime()
        self.configure_block(blk, {'utc': True})
        blk.start()
        blk.process_signals([Signal({'timestamp': self.dummy_timestamp})])
        blk.stop()
        mock_datetime.now.assert_not_called()
        mock_datetime.utcnow.assert_called_once_with()

    @patch('datetime.datetime')
    def test_all_units(self, mock_datetime):
        """ All units are selected"""
        mock_datetime.now.return_value = self.mock_current_time
        mock_datetime.strptime.return_value = self.dummy_timestamp_obj
        delta = (self.mock_current_time - self.dummy_timestamp_obj)
        elapsed = dict(days=0,
                       hours=0,
                       minutes=0,
                       seconds=delta.total_seconds())

        blk = ElapsedTime()
        self.configure_block(blk, {
            "units": {
                "days": True,
                "hours": True,
                "minutes": True,
                "seconds": True,
            }
        })
        blk.start()
        blk.process_signals([Signal({'timestamp': self.dummy_timestamp})])
        blk.stop()
        # current time is checked once per signal list
        mock_datetime.now.assert_called_once_with()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'timestamp': self.dummy_timestamp, 'elapsed': elapsed})

    @patch('datetime.datetime')
    def test_some_units(self, mock_datetime):
        """ Some units are selected"""
        mock_datetime.now.return_value = self.mock_current_time
        mock_datetime.strptime.return_value = self.dummy_timestamp_obj
        delta = (self.mock_current_time - self.dummy_timestamp_obj)
        elapsed = dict(hours=0,
                       minutes=delta.total_seconds() / 60)

        blk = ElapsedTime()
        self.configure_block(blk, {
            "units": {
                "hours": True,
                "minutes": True,
            }
        })
        blk.start()
        blk.process_signals([Signal({'timestamp': self.dummy_timestamp})])
        blk.stop()
        # current time is checked once per signal list
        mock_datetime.now.assert_called_once_with()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'timestamp': self.dummy_timestamp, 'elapsed': elapsed})

    @patch('datetime.datetime')
    def test_one_units(self, mock_datetime):
        """ one unit is selected"""
        mock_datetime.now.return_value = self.mock_current_time
        mock_datetime.strptime.return_value = self.dummy_timestamp_obj
        delta = (self.mock_current_time - self.dummy_timestamp_obj)
        elapsed = dict(days=delta.days)

        blk = ElapsedTime()
        self.configure_block(blk, {
            "units": {
                "days": True,
            }
        })
        blk.start()
        blk.process_signals([Signal({'timestamp': self.dummy_timestamp})])
        blk.stop()
        # current time is checked once per signal list
        mock_datetime.now.assert_called_once_with()
        self.assert_num_signals_notified(1)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            {'timestamp': self.dummy_timestamp, 'elapsed': elapsed})
