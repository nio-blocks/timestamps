from datetime import timedelta
from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..elapsed_time_block import ElapsedTime


class TestElapsedTime(NIOBlockTestCase):

    maxDiff = None

    # test timestamps with interval 1 day, 12 hours, 42 minutes, 3.142 seconds
    timestamp_a = '1984-05-03T05:45:00+0545'  # midight UTC in Nepal
    timestamp_b = '1984-05-04T12:42:03.142Z'  # UTC, with optional milliseconds
    # create refs to elapsed time
    total_seconds = timedelta(
        days=1,
        hours=12,
        minutes=42,
        seconds=3.142).total_seconds()  # why not let the computer do the math
    total_minutes = total_seconds / 60
    total_hours = total_minutes / 60
    total_days = total_hours / 24

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

        # check output
        self.assert_last_signal_list_notified([
            Signal({
                'timestamp_a': self.timestamp_a,
                'timestamp_b': self.timestamp_b,
                'timedelta': {
                    'days': self.total_days,
                    'hours': self.total_hours,
                    'minutes': self.total_minutes,
                    'seconds': self.total_seconds,
                },
            }),
        ])

    def test_advanced_configuration(self):
        """ Unit selection, output attribute, and enrichment options."""
        blk = ElapsedTime()
        config = {
            'enrich': {
                'exclude_existing': True,
            },
            'output_attr': '{{ $output }}',
            'timestamp_a': self.timestamp_a,
            'timestamp_b': self.timestamp_b,
            'units': {
                'days': '{{ $days }}',
                'hours': '{{ $hours }}',
                'minutes': '{{ $minutes }}',
                'seconds': '{{ $seconds }}',
            },
        }
        self.configure_block(blk, config)

        # process a list of signals
        # cover all possible selections
        blk.start()
        blk.process_signals([
            Signal({
                'days': True,
                'hours': True,
                'minutes': True,
                'seconds': True,
                'output': 'all',
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': False,
                'seconds': False,
                'output': 'days',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': False,
                'seconds': False,
                'output': 'hours',
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': True,
                'seconds': False,
                'output': 'minutes',
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': False,
                'seconds': True,
                'output': 'seconds',
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': False,
                'seconds': False,
                'output': 'days+hours',
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': True,
                'seconds': False,
                'output': 'days+minutes',
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': False,
                'seconds': True,
                'output': 'days+seconds',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': True,
                'seconds': False,
                'output': 'hours+minutes',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': False,
                'seconds': True,
                'output': 'hours+seconds',
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': True,
                'seconds': True,
                'output': 'minutes+seconds',
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': True,
                'seconds': False,
                'output': 'days+hours+minutes',
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': False,
                'seconds': True,
                'output': 'days+hours+seconds',
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': True,
                'seconds': True,
                'output': 'days+minutes+seconds',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': True,
                'seconds': True,
                'output': 'hours+minutes+seconds',
            }),
        ])
        blk.stop()

        # checkout ouput
        self.assert_last_signal_list_notified([
            Signal({
                'all': {
                    'days': 1,
                    'hours': 12,
                    'minutes': 42,
                    # use modulo for consistent floating point error
                    'seconds': self.total_seconds % 60,  # 3.142
                },
            }),
            Signal({
                'days': {
                    'days': self.total_days,
                },
            }),
            Signal({
                'hours': {
                    'hours': self.total_hours,
                },
            }),
            Signal({
                'minutes': {
                    'minutes': self.total_minutes,
                },
            }),
            Signal({
                'seconds': {
                    'seconds': self.total_seconds,
                },
            }),
            Signal({
                'days+hours': {
                    'days': int(self.total_days),
                    'hours': self.total_hours % (int(self.total_days) * 24),
                },
            }),
            Signal({
                'days+minutes': {
                    'days': int(self.total_days),
                    'minutes': \
                        self.total_minutes % (int(self.total_days) * 60 * 24),
                },
            }),
            Signal({
                'days+seconds': {
                    'days': int(self.total_days),
                    'seconds': \
                        self.total_seconds % \
                        (int(self.total_days) * 60**2 * 24),
                },
            }),
            Signal({
                'hours+minutes': {
                    'hours': int(self.total_hours),
                    'minutes': \
                        self.total_minutes % (int(self.total_hours) * 60),
                },
            }),
            Signal({
                'hours+seconds': {
                    'hours': int(self.total_hours),
                    'seconds': \
                        self.total_seconds % (int(self.total_hours) * 60**2),
                },
            }),
            Signal({
                'minutes+seconds': {
                    'minutes': int(self.total_minutes),
                    'seconds': \
                        self.total_seconds % (int(self.total_minutes) * 60),
                },
            }),
            Signal({
                'days+hours+minutes': {
                    'days': int(self.total_days),
                    'hours': int(
                        self.total_hours % (int(self.total_days) * 24)),
                    'minutes': \
                        self.total_minutes % (int(self.total_hours) * 60),
                },
            }),
            Signal({
                'days+hours+Seconds': {
                    'days': int(self.total_days),
                    'hours': int(
                        self.total_hours % (int(self.total_days) * 24)),
                    'seconds': \
                        self.total_seconds % (int(self.total_hours) * 60**2),
                },
            }),
            Signal({
                'days+minutes+seconds': {
                    'days': int(self.total_days),
                    'minutes': int(
                        self.total_minutes % (int(self.total_days) * 60 * 24)),
                    'seconds': \
                        self.total_seconds % (int(self.total_minutes) * 60),
                },
            }),
            Signal({
                'hours+minutes+seconds': {
                    'hours': int(self.total_hours),
                    'minutes': int(
                        self.total_minutes % (int(self.total_hours) * 60)),
                    'seconds': \
                        self.total_seconds % (int(self.total_minutes) * 60),
                },
            }),
        ])
