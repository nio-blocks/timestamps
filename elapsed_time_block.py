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

    days = BoolProperty(title='Days', default=False)
    hours = BoolProperty(title='Hours', default=False)
    minutes = BoolProperty(title='Minutes', default=False)
    seconds = BoolProperty(title='Seconds', default=False)


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
        # convert into more significant units
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        # parse into selected units
        all_units_selected = (
            self.units().days(signal) and
            self.units().hours(signal) and 
            self.units().minutes(signal) and 
            self.units().seconds(signal))
        any_units_selected = (
            self.units().days(signal) or
            self.units().hours(signal) or 
            self.units().minutes(signal) or 
            self.units().seconds(signal))
        if not any_units_selected:
            # the default case
            delta = {
                'days': days,
                'hours': hours,
                'minutes': minutes,
                'seconds': seconds,
            }
        elif all_units_selected:
            delta = {
                'days': int(days),
                'hours': int(hours),
                'minutes': int(minutes),
                'seconds': seconds % 60,
            }
        else:
            # some units selected
            delta = {}
            if self.units().days(signal):
                less_significant_selected = (
                    self.units().hours(signal) or
                    self.units().minutes(signal) or
                    self.units().seconds(signal))
                if not less_significant_selected:
                    delta['days'] = days
                else:
                    delta['days'] = int(days)
            if self.units().hours(signal):
                less_significant_selected = (
                    self.units().minutes(signal) or
                    self.units().seconds(signal))
                if not less_significant_selected:
                    delta['hours'] = hours
                else:
                    delta['hours'] = int(hours)
            if self.units().minutes(signal):
                less_significant_selected = self.units().seconds(signal)
                if not less_significant_selected:
                    delta['minutes'] = minutes
                else:
                    delta['minutes'] = int(less_significant_selected)
            if self.units().seconds(signal):
                delta['seconds'] = seconds
        return delta

    def _load_timestamp(self, timestamp):
        """ Returns a datetime object from an ISO 8601 string."""
        if '.' in timestamp:  # includes milliseconds
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
