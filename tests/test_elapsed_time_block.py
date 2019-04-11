from datetime import timedelta
from unittest.mock import patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal
from nio.testing.block_test_case import NIOBlockTestCase
from ..elapsed_time_block import ElapsedTime


class RoundedSig(Signal):

    def to_dict(self):
        my_dict = super().to_dict()
        for key, item in my_dict.items():
            if isinstance(item, dict):
                for attr, value in item.items():
                    if isinstance(value, float):
                        my_dict[key][attr] = round(value, 6)
            else:
                if isinstance(item, float):
                    my_dict[key] = round(item, 6)
        return my_dict


@patch('nio.block.mixins.enrich.enrich_signals.Signal', side_effect=RoundedSig)
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

    def test_default_config(self, Signal):
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
                'seconds': self.total_seconds,
            }),
        ])

    def test_unit_selections(self, Signal):
        """ Unit selection and signal enrichment options."""
        blk = ElapsedTime()
        config = {
            'enrich': {
                'exclude_existing': True,
            },
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
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': False,
                'seconds': False,
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': False,
                'seconds': False,
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': True,
                'seconds': False,
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': False,
                'seconds': True,
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': False,
                'seconds': False,
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': True,
                'seconds': False,
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': False,
                'seconds': True,
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': True,
                'seconds': False,
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': False,
                'seconds': True,
            }),
            Signal({
                'days': False,
                'hours': False,
                'minutes': True,
                'seconds': True,
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': True,
                'seconds': False,
            }),
            Signal({
                'days': True,
                'hours': True,
                'minutes': False,
                'seconds': True,
            }),
            Signal({
                'days': True,
                'hours': False,
                'minutes': True,
                'seconds': True,
            }),
            Signal({
                'days': False,
                'hours': True,
                'minutes': True,
                'seconds': True,
            }),
        ])
        blk.stop()

        # checkout ouput
        self.assert_last_signal_list_notified([
            Signal({
                'days': 1,
                'hours': 12,
                'minutes': 42,
                # use modulo for consistent floating point error
                'seconds': self.total_seconds % 60,  # 3.142
            }),
            Signal({
                'days': self.total_days,
            }),
            Signal({
                'hours': self.total_hours,
            }),
            Signal({
                'minutes': self.total_minutes,
            }),
            Signal({
                'seconds': self.total_seconds,
            }),
            Signal({
                'days': int(self.total_days),
                'hours': self.total_hours % (int(self.total_days) * 24),
            }),
            Signal({
                'days': int(self.total_days),
                'minutes': \
                    self.total_minutes % (int(self.total_days) * 60 * 24),
            }),
            Signal({
                'days': int(self.total_days),
                'seconds': \
                    self.total_seconds % (int(self.total_days) * 60**2 * 24),
            }),
            Signal({
                'hours': int(self.total_hours),
                'minutes': self.total_minutes % (int(self.total_hours) * 60),
            }),
            Signal({
                'hours': int(self.total_hours),
                'seconds': \
                    self.total_seconds % (int(self.total_hours) * 60**2),
            }),
            Signal({
                'minutes': int(self.total_minutes),
                'seconds': self.total_seconds % (int(self.total_minutes) * 60),
            }),
            Signal({
                'days': int(self.total_days),
                'hours': int(self.total_hours % (int(self.total_days) * 24)),
                'minutes': self.total_minutes % (int(self.total_hours) * 60),
            }),
            Signal({
                'days': int(self.total_days),
                'hours': int(self.total_hours % (int(self.total_days) * 24)),
                'seconds': \
                    self.total_seconds % (int(self.total_hours) * 60**2),
            }),
            Signal({
                'days': int(self.total_days),
                'minutes': int(
                    self.total_minutes % (int(self.total_days) * 60 * 24)),
                'seconds': self.total_seconds % (int(self.total_minutes) * 60),
            }),
            Signal({
                'hours': int(self.total_hours),
                'minutes': int(
                    self.total_minutes % (int(self.total_hours) * 60)),
                'seconds': self.total_seconds % (int(self.total_minutes) * 60),
            }),
        ])

    def test_optional_milliseconds(self, Signal):
        """ Milliseconds in incoming timestamps can optionally be truncated."""
        blk = ElapsedTime()
        config = {
            'milliseconds': '{{ $ms }}',
            'units': {
                'days': True,
                'hours': True,
                'minutes': True,
                'seconds': True,
            },
            'timestamp_a': '1984-05-03T00:00:00.999Z',
            'timestamp_b': '1984-05-03T00:00:01.001Z',
        }
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal({
                'ms': False,
            }),
        ])
        blk.stop()

        # check output
        # milliseconds are truncated BEFORE comparing timestamps
        self.assert_last_signal_list_notified([
            Signal({
                'ms': False,
                'days': 0,
                'hours': 0,
                'minutes': 0,
                'seconds': 1,
            }),
        ])
        # check that seconds was cast to int
        seconds = self.last_notified[DEFAULT_TERMINAL][0].seconds
        self.assertTrue(isinstance(seconds, int))

    def test_nothing_checked(self, Signal):
        """ Empty dict out when no values are checked """
        blk = ElapsedTime()
        config = {
            'units': {
                'days': False,
                'hours': False,
                'minutes': False,
                'seconds': False,
            },
            'timestamp_a': '1984-05-03T00:00:00.999Z',
            'timestamp_b': '1984-05-03T00:00:01.001Z',
        }
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal({
                'pi': 3.142,
            }),
        ])
        blk.stop()

        self.assert_last_signal_list_notified([
            Signal({
                'pi': 3.142,
            }),
        ])
