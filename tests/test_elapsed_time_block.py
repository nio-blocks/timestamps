from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..elapsed_time_block import ElapsedTime


class TestElapsedTime(NIOBlockTestCase):

    # test timestamps with interval 1 day, 12 hours, 42 minutes, 3.142 seconds
    timestamp_a = '1984-05-03T05:45:00+0545'  # midight UTC in Nepal
    timestamp_b = '1984-05-04T12:42:03.142Z'  # UTC, with optional milliseconds
    # create refs to elapsed time
    seconds = (36 * 60**2) + (42 * 60) + 3.142  # 36h + 42m + 3.142s
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

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
                    'days': self.days,
                    'hours': self.hours,
                    'minutes': self.minutes,
                    'seconds': self.seconds,
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
                    'days': self.days,
                    'hours': self.hours,
                    'minutes': self.minutes,
                    'seconds': self.seconds,
                },
            }),
        ])

    def test_all_units_selected(self):
        """ Elapsed time is returned in only the selected unit."""
        blk = ElapsedTime()
        config = {
            'timestamp_a': self.timestamp_a,
            'timestamp_b': self.timestamp_b,
            'units': {
                'days': True,
                'hours': True,
                'minutes': True,
                'seconds': True,
            },
        }
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal(),
        ])
        blk.stop()

        # check output
        self.assert_last_signal_list_notified([
            Signal({
                'timedelta': {
                    'days': int(self.days),
                    'hours': int(self.hours),
                    'minutes': int(self.minutes),
                    'seconds': self.seconds % 60,
                },
            }),
        ])

    def test_single_unit_selected(self):
        """ Elapsed time is returned in only the selected unit."""
        blk = ElapsedTime()
        config = {
            'timestamp_a': self.timestamp_a,
            'timestamp_b': self.timestamp_b,
            'units': {
                'minutes': True,
            },
        }
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal(),
        ])
        blk.stop()

        # check output
        self.assert_last_signal_list_notified([
            Signal({
                'timedelta': {
                    'minutes': self.minutes,
                },
            }),
        ])

    def test_some_units_selected(self):
        """ Elapsed time is returned in only the selected unit."""
        blk = ElapsedTime()
        config = {
            'timestamp_a': self.timestamp_a,
            'timestamp_b': self.timestamp_b,
            'units': {
                'hours': True,
                'minutes': True,
            },
        }
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal(),
        ])
        blk.stop()

        # check output
        self.assert_last_signal_list_notified([
            Signal({
                'timedelta': {
                    'hours': int(self.hours),
                    'minutes': self.minutes % 60,
                },
            }),
        ])
