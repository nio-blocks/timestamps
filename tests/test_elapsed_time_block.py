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
                'output': 'd',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': False,
                'seconds': False,
                'output': 'h',
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': True,
                'seconds': False,
                'output': 'm',
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': False,
                'seconds': True,
                'output': 's',
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': False,
                'seconds': False,
                'output': 'dh',
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': True,
                'seconds': False,
                'output': 'dm',
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': False,
                'seconds': True,
                'output': 'ds',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': True,
                'seconds': False,
                'output': 'hm',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': False,
                'seconds': True,
                'output': 'hs',
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': True,
                'seconds': True,
                'output': 'ms',
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': True,
                'seconds': False,
                'output': 'dhm',
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': False,
                'seconds': True,
                'output': 'dhs',
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': True,
                'seconds': True,
                'output': 'dms',
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': True,
                'seconds': True,
                'output': 'hms',
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
                'd': {
                    'days': self.total_days,
                },
            }),
            Signal({
                'h': {
                    'hours': self.total_hours,
                },
            }),
            Signal({
                'm': {
                    'minutes': self.total_minutes,
                },
            }),
            Signal({
                's': {
                    'seconds': self.total_seconds,
                },
            }),
            Signal({
                'dh': {
                    'days': int(self.total_days),
                    'hours': self.total_hours % (int(self.total_days) * 24),
                },
            }),
            Signal({
                'dm': {
                    'days': int(self.total_days),
                    'minutes': \
                        self.total_minutes % (int(self.total_days) * 60 * 24),
                },
            }),
            Signal({
                'ds': {
                    'days': int(self.total_days),
                    'seconds': \
                        self.total_seconds % \
                        (int(self.total_days) * 60**2 * 24),
                },
            }),
            Signal({
                'hm': {
                    'hours': int(self.total_hours),
                    'minutes': \
                        self.total_minutes % (int(self.total_hours) * 60),
                },
            }),
            Signal({
                'hs': {
                    'hours': int(self.total_hours),
                    'seconds': \
                        self.total_seconds % (int(self.total_hours) * 60**2),
                },
            }),
            Signal({
                'ms': {
                    'minutes': int(self.total_minutes),
                    'seconds': \
                        self.total_seconds % (int(self.total_minutes) * 60),
                },
            }),
            Signal({
                'dhm': {
                    'days': int(self.total_days),
                    'hours': \
                        int(self.total_hours % (int(self.total_days) * 24)),
                    'minutes': \
                        self.total_minutes % (int(self.total_hours) * 60),
                },
            }),
            Signal({
                'dhs': {
                    'days': int(self.total_days),
                    'hours': \
                        int(self.total_hours % (int(self.total_days) * 24)),
                    'seconds': \
                        self.total_seconds % (int(self.total_hours) * 60**2),
                },
            }),
            Signal({
                'dms': {
                    'days': int(self.total_days),
                    'minutes': \
                        int(self.total_minutes % (int(self.total_days) * 60 * 24)),
                    'seconds': \
                        self.total_seconds % (int(self.total_minutes) * 60),
                },
            }),
            Signal({
                'hms': {
                    'hours': int(self.total_hours),
                    'minutes': \
                        int(self.total_minutes % (int(self.total_hours) * 60)),
                    'seconds': \
                        self.total_seconds % (int(self.total_minutes) * 60),
                },
            }),
        ])
