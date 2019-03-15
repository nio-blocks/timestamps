from datetime import datetime
from nio import Block
from nio.block.mixins import EnrichSignals
from nio.block.mixins.enrich.enrich_signals import EnrichProperties
from nio.properties import BoolProperty, ObjectProperty, StringProperty, \
    VersionProperty


class CustomEnrichProperties(EnrichProperties):
    """ Overrides default enrichment to include existing fields."""
    exclude_existing = BoolProperty(title='Exclude Existing?', default=False)


class ElapsedTime(EnrichSignals, Block):

    timestamp_a = StringProperty(title='Timestamp A', order=0)
    timestamp_b = StringProperty(title='Timestamp B', order=1)

    output_attr = StringProperty(
        title='Outgoing Signal Attribute',
        default='timedelta',
        order=0,
        advanced=True)

    enrich = ObjectProperty(
        CustomEnrichProperties,
        title='Signal Enrichment',
        default=CustomEnrichProperties(),  # use custom default
        order=100,
        advanced=True)
    version = VersionProperty('0.1.0')

    def process_signal(self, signal):
        delta = self._get_timedelta(signal)
        signal_dict = {
            self.output_attr(signal): delta,
        }
        output_signal = self.get_output_signal(signal_dict, signal)
        return output_signal

    def _get_timedelta(self, signal):
        """ Returns computed delta in terms of `units` using `signal`"""
        time_a = self._load_timestamp(self.timestamp_a(signal))
        time_b = self._load_timestamp(self.timestamp_b(signal))
        # subtract datetimes to get timedelta in seconds
        seconds = (time_b - time_a).total_seconds()
        # convert to other units
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        delta = {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
        }
        return delta

    def _load_timestamp(self, timestamp):
        """ Returns a datetime object from an ISO 8601 string."""
        if '.' in timestamp:  # includes milliseconds
            timestamp_format = '%Y-%m-%dT%H:%M:%S.%f%z'
        else:
            timestamp_format = '%Y-%m-%dT%H:%M:%S%z'
        if timestamp.endswith('Z'):  # UTC timezone
            # include an offset so that resulting datetime is timezone aware
            timestamp = timestamp.replace('Z', '+0000')
        # create datetime object from timestamp string
        time = datetime.strptime(timestamp, timestamp_format)
        return time
