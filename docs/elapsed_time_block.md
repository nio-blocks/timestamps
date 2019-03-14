ElapsedTime
===
Compare Two [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted timestamps and add the elapsed time information to each incoming signal. Elapsed times can be represented in any or all of four floating point numbers representing days, hours, minutes, and seconds.

See Also: [AddTimestamp](https://blocks.n.io/AddTimestamp) for creating timestamps.

Properties
===
- **Time A**: A timestamp string.
- **Time B**: A timestamp string.
- **Units**
  - *Days*: default `False`
  - *Hours*: default `False`
  - *Minutes*: default `False`
  - *Seconds*: default `False`
- **Outgoing Signal Attribute** (advanced): Attribute of outgoing signals to contain the time delta, default `elapsed_time`

Example
===
Configure the block to compare timestamps in an incoming signal:

```
Timestamp A: {{ $then }}
Timestamp B: {{ $now }}
```

Process a list of signals:

```
[
  {
    "now": "1984-05-03T00:42:03.141593Z",
    "then": "1984-05-03T00:00:00.000000Z"
  }
]
```

The timestamps are compared, and the delta of `Timestamp B - Timestamp A` is parsed according to the configuration and added to the incoming signal in the **Outgoing Signal Attribute**. Because each of *Units* is de-selected by default, all available units will be included, with decmials, in the output:

```
[
  {
    "elapsed_time": {
      "days": 0.029166...,
      "hours": 0.7,
      "minutes": 42.074799...,
      "seconds": 45.141593
    },
    "now": "1984-05-03T00:42:03.141593Z",
    "then": "1984-05-03T00:00:00.000000Z"
  }
]
```

If selecting one or more **Units**, only those units will be included in `elapsed_time`. The smallest of the **Units** selected will remain a floating-point number with decmials, while all others will be integers.

Configure the block, selecting some of **Units**:

```
Time A: {{ $then }}
Time B: {{ $now }}
Units:
  Days: False
  Hours: True
  Minutes: True
  Seconds: False
```

Process the same list of signals:

```
[
  {
    "now": "1984-05-03T00:42:03.141593Z",
    "then": "1984-05-03T00:00:00.000000Z"
  }
]
```

Less than one full hour has elapsed so `hours` is zero, while `minutes` includes the smaller, de-selected `seconds` component as a decimal:

```
[
  {
    "elapsed_time": {
      "hours": 0,
      "minutes": 42.074799...
    },
    "now": "1984-05-03T00:42:03.141593Z",
    "then": "1984-05-03T00:00:00.000000Z"
  }
]
```

Similarly, had all of the available **Units** been selected:

```
[
  {
    "elapsed_time": {
      "days": 0,
      "hours": 0,
      "minutes": 42,
      "seconds": 3.141593
    },
    "now": "1984-05-03T00:42:03.141593Z",
    "then": "1984-05-03T00:00:00.000000Z"
  }
]
```

And if a single **Unit** is selected:

```
[
  {
    "elapsed_time": {
      "seconds": 45.141593
    },
    "now": "1984-05-03T00:42:03.141593Z",
    "then": "1984-05-03T00:00:00.000000Z"
  }
]
```
