from datetime import datetime
from unittest.mock import ANY, Mock, patch
from nio import Signal
from nio.block.terminals import DEFAULT_TERMINAL
from nio.testing.block_test_case import NIOBlockTestCase
from ..add_timestamp_block import AddTimestamp


class TestAddTimestamp(NIOBlockTestCase):

    def validate_timestamps(self, format, attr='timestamp'):
        """ Iterates over the notified signal list and raises ValueError if 
            any signal's `attr` is not valid according to `format`.
        """
        for signal in self.last_notified[DEFAULT_TERMINAL]:
            datetime.strptime(getattr(signal, attr), format)

    @patch(AddTimestamp.__module__ + '.datetime')
    def test_default_config(self, mock_datetime):
        """ UTC timestamp is added to each signal in a list, `Z` timezone."""
        format = '%Y-%m-%dT%H:%M:%S.%fZ'
        # set up mocks for assertions,
        # return a real datetime object for simplicity in testing
        mock_datetime.utcnow = Mock(return_value=datetime.utcnow())

        blk = AddTimestamp()
        config = {}
        self.configure_block(blk, config)

        # process a list of signals
        blk.start()
        blk.process_signals([
            Signal({'foo': 'bar'}),
            Signal({'foo': 'baz'}),
        ])
        blk.stop()

        # check calls
        mock_datetime.now.assert_not_called()
        mock_datetime.utcnow.assert_called_once_with()
        # check output, enriched by default
        self.validate_timestamps(format)
        self.assert_last_signal_list_notified([
            Signal({
                'foo': 'bar',
                'timestamp': ANY,
            }),
            Signal({
                'foo': 'baz',
                'timestamp': ANY,
            }),
        ])

    @patch(AddTimestamp.__module__ + '.datetime')
    def test_local_timestamp(self, mock_datetime):
        """ Local time is used instead of UTC, includes timezone info."""
        format = '%Y-%m-%dT%H:%M:%S.%f%z'
        # set up mocks for assertions,
        # return a real datetime object for simplicity in testing
        mock_datetime.now = Mock(return_value=datetime.now())

        blk = AddTimestamp()
        config = {'utc': False}
        self.configure_block(blk, config)

        # process a signal
        blk.start()
        blk.process_signals([
            Signal(),
        ])
        blk.stop()

        # check calls
        mock_datetime.now.assert_called_once_with()
        mock_datetime.utcnow.assert_not_called()
        # check output
        self.validate_timestamps(format)
        self.assert_num_signals_notified(1)

    def test_advanced_configuration(self):
        """ Signal attribute, millisecond, and enrichment options."""
        format = '%Y-%m-%dT%H:%M:%SZ'
        blk = AddTimestamp()
        config = {
            'enrich': {
                'exclude_existing': True,
            },
            'milliseconds': False,
            'output_attr': '{{ $custom_attr }}',
        }
        self.configure_block(blk, config)

        # process a signal
        blk.start()
        blk.process_signals([
            Signal({
                'custom_attr': 'custom',
            }),
        ])
        blk.stop()

        # check output
        self.validate_timestamps(format, attr='custom')
        self.assert_last_signal_list_notified([
            Signal({
                'custom': ANY,
            }),
        ])
