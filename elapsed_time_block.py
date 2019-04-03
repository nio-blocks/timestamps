import math
from datetime import datetime, timezone
from nio import Block
from nio.block.mixins import EnrichSignals
from nio.block.mixins.enrich.enrich_signals import EnrichProperties
from nio.properties import BoolProperty, ObjectProperty, PropertyHolder, \
    StringProperty, VersionProperty


class CustomEnrichProperties(EnrichProperties):
    """ Overrides default enrichment to include existing fields."""
    exclude_existing = BoolProperty(title='Exclude Existing?', default=False)


class Units(PropertyHolder):

    days = BoolProperty(title='Days', default=False, order=0)
    hours = BoolProperty(title='Hours', default=False, order=1)
    minutes = BoolProperty(title='Minutes', default=False, order=2)
    seconds = BoolProperty(title='Seconds', default=False, order=3)


class ElapsedTime(EnrichSignals, Block):

    timestamp_a = StringProperty(title='Timestamp A', order=0)
    timestamp_b = StringProperty(title='Timestamp B', order=1)

    output_attr = StringProperty(
        title='Outgoing Signal Attribute',
        default='timedelta',
        order=0,
        advanced=True)
    units = ObjectProperty(
        Units,
        title='Units',
        default=Units(),
        order=1,
        advanced=True)
    milliseconds = BoolProperty(
        title='Include Milliseconds',
        default=True,
        order=2,
        advanced=True)

    enrich = ObjectProperty(
        CustomEnrichProperties,
        title='Signal Enrichment',
        default=CustomEnrichProperties(),  # use custom default
        order=100,
        advanced=True)
    version = VersionProperty('0.1.0')

    def process_signal(self, signal):
        seconds = self._get_timedelta(signal)
        delta = self._format_seconds_diff(seconds, signal)
        signal_dict = {
            self.output_attr(signal): delta,
        }
        output_signal = self.get_output_signal(signal_dict, signal)
        return output_signal

    def _get_timedelta(self, signal):
        """Returns the number of seconds between the timestamps on a signal"""
        truncate = not self.milliseconds(signal)
        time_a = self._load_timestamp(
            self.timestamp_a(signal),
            truncate=truncate)
        time_b = self._load_timestamp(
            self.timestamp_b(signal),
            truncate=truncate)
        # subtract datetimes to get timedelta in seconds
        seconds = (time_b - time_a).total_seconds()
        if truncate and self.units().seconds(signal):
            # timedelta.total_seconds() returns a float
            seconds = int(seconds)
        return seconds

    def _format_seconds_diff(self, seconds, signal):
        """ Returns the number of seconds in terms of `units` using `signal`"""
        days_enabled = self.units().days(signal)
        hours_enabled = self.units().hours(signal)
        mins_enabled = self.units().minutes(signal)
        secs_enabled = self.units().seconds(signal)
        least_significant = "seconds"
        least_significant_mult = 1

        if not any([days_enabled, hours_enabled, mins_enabled, secs_enabled]):
            # Treat nothing enabled as all enabled
            days_enabled = hours_enabled = mins_enabled = secs_enabled = True

        output = {}

        # Go through and remove the most significant values first. Stick the
        # remainder on the least significant enabled value
        if days_enabled:
            least_significant = "days"
            least_significant_mult = 60 * 60 * 24
            output["days"] = days = math.floor(seconds / 60 / 60 / 24)
            seconds -= days * 60 * 60 * 24

        if hours_enabled:
            least_significant = "hours"
            least_significant_mult = 60 * 60
            output["hours"] = hours = math.floor(seconds / 60 / 60)
            seconds -= hours * 60 * 60

        if mins_enabled:
            least_significant = "minutes"
            least_significant_mult = 60
            output["minutes"] = mins = math.floor(seconds / 60)
            seconds -= mins * 60

        if secs_enabled:
            least_significant = "seconds"
            least_significant_mult = 1
            output["seconds"] = seconds
            seconds = 0

        output[least_significant] += seconds / least_significant_mult
        if secs_enabled and not self.milliseconds(signal):
            output["seconds"] = int(output["seconds"])

        return output

    def _load_timestamp(self, timestamp, truncate=False):
        """ Returns a datetime object from an ISO 8601 string."""
        if '.' in timestamp:  # includes milliseconds
            if truncate:
                # remove millisecond component
                _timestamp = timestamp.split('.')
                timestamp = _timestamp[0] + _timestamp[1][3:]
                timestamp_format = '%Y-%m-%dT%H:%M:%S'
            else:
                timestamp_format = '%Y-%m-%dT%H:%M:%S.%f'
        else:
            timestamp_format = '%Y-%m-%dT%H:%M:%S'
        if timestamp.endswith('Z'):  # UTC timezone
            timestamp_format += 'Z'
        else:
            timestamp_format += '%z'
        # create datetime object from timestamp string
        time = datetime.strptime(timestamp, timestamp_format)
        if time.tzinfo is None:  # if UTC the datetime will be offset-naive
            time = time.replace(tzinfo=timezone.utc)
        return time

    def _more_significant_selected(self, item, signal):
        """ Use a signal to evaluate if a unit more significant than item has
            been selected.
        """
        units = ['seconds', 'minutes', 'hours', 'days']
        # get index to item in units
        for i, unit in enumerate(units):
            if unit == item:
                break
        # check more significant units and return True if selected
        i += 1
        for r in range(len(units) - i):
            if getattr(self.units(), units[r + i])(signal):
                return True
        return False
