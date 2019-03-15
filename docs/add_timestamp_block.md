AddTimestamp
===
Add an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted timestamp string to a list of signals. All signals in a list will have the same timestamp.

See Also: [ElapsedTime](https://blocks.n.io/ElapsedTime) for computing time intervals from a timestamp.

Properties
===
- **UTC**: Use [Coordinated Universal Time](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) instead of local machine time, default `True`
- **Outgoing Signal Attribute** (advanced): Attribute of outgoing signals to contain the new timestamp, default `timestamp`
- **Milliseconds** (advanced): Include milliseconds in time such as `HH:MM:SS.sss`, default `True`. If `False` the time will follow format `HH:MM:SS`

Example
===
ISO 8601 specifies the `T` delimiter separating the date and time, as well as the `Z` suffix for UTC times, `YYYY-MM-DDTHH:MM:SS.sssZ`. If **UTC** is `False` the local time's UTC offset will be included as a signed 4-digit value `±HHMM`, for example Nepal Standard Time: `YYYY-MM-DDTHH:MM:SS.sss+0545`. If **Milliseconds** is `False` then seconds will be truncated to whole values: `YYYY-MM-DDTHH:MM:SS+0545`
