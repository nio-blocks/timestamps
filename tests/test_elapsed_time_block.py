from unittest.mock import ANY, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..elapsed_time_block import ElapsedTime


class TestElapsedTime(NIOBlockTestCase):

    # define timestamps with interval 42 minutes and Pi seconds
    timestamp_a = '1984-05-03T05:45:00+0545'  # midight UTC in Nepal
    timestamp_b = '1984-05-03T00:42:03.142Z'  # UTC, with optional milliseconds

    def test_default_config(self):
        """ Two timestamps in an incoming signal are compared."""
        blk = ElapsedTime()
        config = {
            'timestamp_a': '{{ $timestamp_a }}',
            'timestamp_b': '{{ $timestamp_b }}',
        }
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal({
                'timestamp_a': self.timestamp_a,
                'timestamp_b': self.timestamp_b,
            }),
        ])
        blk.stop()

        # compare output to known interval of test timestamps
        seconds = (42 * 60) + 3.142
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        self.assert_last_signal_list_notified([
            Signal({
                'timestamp_a': self.timestamp_a,
                'timestamp_b': self.timestamp_b,
                'timedelta': {
                    'days': days,
                    'hours': hours,
                    'minutes': minutes,
                    'seconds': seconds,
                },
            }),
        ])

    def test_advanced_configuration(self):
        """ Signal attribute and enrichment options."""
        blk = ElapsedTime()
        config = {
            'enrich': {
                'exclude_existing': True,
            },
            'output_attr': '{{ $custom_attr }}',
            'timestamp_a': self.timestamp_a,
            'timestamp_b': self.timestamp_b,
        }
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal({
                'custom_attr': 'custom',
            }),
        ])
        blk.stop()

        # checkout ouput
        self.assert_last_signal_list_notified([
            Signal({
                'custom': {
                    'days': ANY,
                    'hours': ANY,
                    'minutes': ANY,
                    'seconds': ANY,
                },
            }),
        ])
