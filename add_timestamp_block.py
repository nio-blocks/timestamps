from datetime import datetime
from tzlocal import get_localzone
from nio import Block
from nio.block.mixins import EnrichSignals
from nio.block.mixins.enrich.enrich_signals import EnrichProperties
from nio.properties import BoolProperty, ObjectProperty, PropertyHolder, \
    StringProperty, VersionProperty


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
        if self.milliseconds():
            timespec = 'milliseconds'  # HH:MM:SS.sss time format
        else:
            timespec = 'seconds'  # HH:MM:SS
        if self.utc():
            current_time = str(datetime.utcnow().isoformat(timespec=timespec))
            # Add timezone
            current_time += 'Z'
        else:
            # TODO: Add options for TZ format
            current_time_tz = get_localzone().localize(datetime.now())
            current_time = str(current_time_tz.isoformat(timespec=timespec))
            # remove colon from TZ info
            current_time = ''.join(current_time.rsplit(':', 1))
        return current_time
