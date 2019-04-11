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
        """ Return an ISO-formatted string. Helper `_truncate_` functions
            are to support Python < 3.6, after which `datetime.isoformat()`
            takes a `timespec` arg."""
        if self.utc():
            now = datetime.utcnow()
            if not self.milliseconds():
                now = self._truncate_fractional_seconds(now)
                current_time = now.isoformat() + 'Z'
            else:
                current_time = now.isoformat()
                current_time = self._truncate_microseconds(current_time) + 'Z'
            return current_time
        # get local timestamp
        now = datetime.now()
        if not self.milliseconds():
            now = self._truncate_fractional_seconds(now)
            current_time = str(self._localize_time(now))
        else:
            current_time = str(self._localize_time(now))
            current_time = self._truncate_microseconds(current_time)
        # remove colon from TZ info (±HHMM format)
        # TODO: Add options for formats ±HH:MM, ±HH
        current_time = ''.join(current_time.rsplit(':', maxsplit=1))
        return current_time

    @staticmethod
    def _localize_time(now):
        """ Return datetime `now` with local timezone."""
        current_time_with_tz = get_localzone().localize(now)
        current_time = current_time_with_tz.isoformat()
        return current_time

    @staticmethod
    def _truncate_fractional_seconds(now):
        """ Return a datetime equal to `now` with `microsecond=0`"""
        now = datetime(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            second=now.second,
            microsecond=0)
        return now

    @staticmethod
    def _truncate_microseconds(timestamp):
        """ Remove microseconds from string `timestamp`"""
        base, suffix = timestamp.split('.')
        microseconds, offset = suffix[:6], suffix[6:]
        milliseconds = microseconds[:3]
        suffix = milliseconds + offset
        timestamp = '.'.join([base, suffix])
        return timestamp
