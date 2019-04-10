from datetime import datetime
from tzlocal import get_localzone
from nio import Block
from nio.block.mixins import EnrichSignals
from nio.block.mixins.enrich.enrich_signals import EnrichProperties
from nio.properties import BoolProperty, ObjectProperty, StringProperty, \
    VersionProperty


class CustomEnrichProperties(EnrichProperties):
    """ Overrides default enrichment to include existing fields."""

    exclude_existing = BoolProperty(title='Exclude Existing?', default=False)


class AddTimestamp(EnrichSignals, Block):

    utc = BoolProperty(title='UTC', default=True)

    output_attr = StringProperty(
        title='Outgoing Signal Attribute',
        default='timestamp',
        order=0,
        advanced=True)
    milliseconds = BoolProperty(
        title='Milliseconds',
        default=True,
        order=1,
        advanced=True)

    enrich = ObjectProperty(
        CustomEnrichProperties,
        title='Signal Enrichment',
        default=CustomEnrichProperties(),  # use custom default
        order=100,
        advanced=True)
    version = VersionProperty('0.1.0')

    def process_signals(self, signals):
        current_time = self._get_current_time()
        output_signals = []
        for signal in signals:
            signal_dict = {
                self.output_attr(signal): current_time,
            }
            output_signal = self.get_output_signal(signal_dict, signal)
            output_signals.append(output_signal)
        self.notify_signals(output_signals)

    def _get_current_time(self):
        if self.utc():
            now = datetime.utcnow()
            if not self.milliseconds():
                # truncate fractional seconds
                now = datetime(
                    year=now.year,
                    month=now.month,
                    day=now.day,
                    hour=now.hour,
                    minute=now.minute,
                    second=now.second,
                    microsecond=0)
            current_time = str(now.isoformat())
            if self.milliseconds():
                # truncate microseconds to milliseconds
                _base, _microseconds = current_time.split('.')
                _milliseconds = _microseconds[:3]
                current_time = '.'.join([_base, _milliseconds])
            # Add timezone
            current_time += 'Z'
        else:
            now = datetime.now()
            if not self.milliseconds():
                # truncate fractional seconds
                now = datetime(
                    year=now.year,
                    month=now.month,
                    day=now.day,
                    hour=now.hour,
                    minute=now.minute,
                    second=now.second,
                    microsecond=0)
            current_time_with_tz = get_localzone().localize(now)
            current_time = str(current_time_with_tz.isoformat())
            # TODO: Add options for TZ format (±HHMM, ±HH:MM, ±HH)
            # remove colon from TZ info (±HHMM format)
            current_time = ''.join(current_time.rsplit(':', 1))
            if self.milliseconds():
                # truncate microseconds to milliseconds
                _base, _suffix = current_time.split('.')
                _microseconds = _suffix[:6]
                _offset = _suffix[-5:]
                _milliseconds = _microseconds[:3]
                current_time = '.'.join([_base, _milliseconds + _offset])
        return current_time
