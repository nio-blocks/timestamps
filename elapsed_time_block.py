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
        delta = self._get_timedelta(signal)
        signal_dict = {
            self.output_attr(signal): delta,
        }
        output_signal = self.get_output_signal(signal_dict, signal)
        return output_signal

    def _get_timedelta(self, signal):
        """ Returns computed delta in terms of `units` using `signal`"""
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
            _days = int(days)
            try:
                _hours = int(hours % (_days * 24))
            except ZeroDivisionError:
                # zero days
                _hours = int(hours)
            try:
                _minutes = int(minutes % (_hours * 60)) % 60
            except ZeroDivisionError:
                # zero hours
                _minutes = int(minutes)
            _seconds = seconds % 60
            delta = {
                'days': _days,
                'hours': _hours,
                'minutes': _minutes,
                'seconds': _seconds,
            }
        else:
            # some units selected
            delta = {}
            if self.units().seconds(signal):
                if not self._more_significant_selected('seconds', signal):
                    # seconds only
                    delta['seconds'] = seconds
                elif self.units().minutes(signal):
                    if not self._more_significant_selected('minutes', signal):
                        # seconds and minutes
                        delta['minutes'] = int(minutes)
                        delta['seconds'] = seconds % (delta['minutes'] * 60)
                    elif self.units().hours(signal):
                        if not self._more_significant_selected(
                                'hours', signal):
                            # seconds and minutes and hours
                            delta['hours'] = int(hours)
                            delta['minutes'] = \
                                int(minutes % (delta['hours'] * 60))
                            delta['seconds'] = seconds % 60
                        else:
                            # seconds and minutes and hours and days
                            # aka all_units_selected, already covered
                            pass
                    elif self.units().days(signal):
                        # seconds and minutes and days
                        delta['days'] = int(days)
                        delta['minutes'] = int(minutes % (60 * 24))
                        delta['seconds'] = seconds % 60
                elif self.units().hours(signal):
                    if not self._more_significant_selected('hours', signal):
                        # seconds and hours
                        delta['hours'] = int(hours)
                        delta['seconds'] = seconds % (delta['hours'] * 60**2)
                    else:
                        # seconds and hours and days
                        delta['days'] = int(days)
                        delta['hours'] = int(hours % (delta['days'] * 24))
                        delta['seconds'] = seconds % (delta['hours'] * 60**2)
                elif self.units().days(signal):
                    # seconds and days
                    delta['days'] = int(days)
                    delta['seconds'] = seconds % (delta['days'] * 60**2 * 24)
            elif self.units().minutes(signal):
                if not self._more_significant_selected('minutes', signal):
                    # minutes only
                    delta['minutes'] = minutes
                elif self.units().hours(signal):
                    if not self._more_significant_selected('hours', signal):
                        # minutes and hours
                        delta['hours'] = int(hours)
                        delta['minutes'] = minutes % (delta['hours'] * 60)
                    else:
                        # minutes and hours and days
                        delta['days'] = int(days)
                        delta['hours'] = int(hours % (delta['days'] * 24))
                        delta['minutes'] = minutes % (delta['hours'] * 60)
                elif self.units().days(signal):
                    # minutes and days
                    delta['days'] = int(days)
                    delta['minutes'] = minutes % (delta['days'] * 60 * 24)
            elif self.units().hours(signal):
                if not self._more_significant_selected('hours', signal):
                    # hours only
                    delta['hours'] = hours
                else:
                    # hours and days
                    delta['days'] = int(days)
                    delta['hours'] = hours % (delta['days'] * 24)
            elif self.units().days(signal):
                # days only
                delta['days'] = days
        return delta

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
        for r in range(len(units) - (i + 1)):
            if getattr(self.units(), units[r + (i + 1)])(signal):
                return True
        return False
