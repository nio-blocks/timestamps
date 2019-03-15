ElapsedTime
===
Compare Two [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted timestamps, **Timestamp A** and **Timestamp B**, and add the elapsed time delta information to each incoming signal. Elapsed times can be represented in any or all of four floating point numbers representing *Days*, *Hours*, *Minutes*, and *Seconds*; including negative values in the case that **Time A** is later than **Time B**.

See Also: [*AddTimestamp*](https://blocks.n.io/AddTimestamp) for creating timestamps.

Properties
===
- **Timestamp A**: An ISO timestamp string.
- **Timestamp B**: An ISO timestamp string, in most cases this is the later of the two times, often corresponding to the present.
- **Outgoing Signal Attribute** (advanced): Attribute of outgoing signals to contain the computed time delta, default `timedelta`
- **Units** (advanced):
  - *Days*: default `False`
  - *Hours*: default `False`
  - *Minutes*: default `False`
  - *Seconds*: default `False`

Examples
===

Example 1
---
Configure the block to compare timestamps in an incoming signal:

```
Timestamp A: {{ $past }}
Timestamp B: {{ $present }}
```

Process a list of signals:

```
[
  {
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z"
  }
]
```

The timestamps are compared, and the delta of `Timestamp B - Timestamp A` is parsed according to any selected **Units** and added to the incoming signal in the **Outgoing Signal Attribute**. Because each of *Units* is de-selected by default, in this example all available units will be included, with decimal places, in the output:

```
[
  {
    "timedelta": {
      "days": 0.029166...,
      "hours": 0.7,
      "minutes": 42.074799...,
      "seconds": 45.141593
    },
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z"
  }
]
```

Example 2a
---

If selecting one or more **Units**, only those units will be included in `timedelta`. The least significant of the **Units** selected will remain a floating-point number (with a decimal), while all others will be (whole) integers.

Configure the block, selecting some of **Units**:

```
Timestamp A: {{ $past }}
Timestamp B: {{ $present }}
Units:
  Days: False
  Hours: True
  Minutes: True
  Seconds: False
```

Process a list of signals:

```
[
  {
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z"
  }
]
```

Less than one full hour has elapsed from **Timestamp A** to **Timestamp B** so `$timedelta['hours']` is zero, while `$timedelta['minutes']` includes the less significant, de-selected *Seconds* unit in its decimal:

```
[
  {
    "timedelta": {
      "hours": 0,
      "minutes": 42.074799...
    },
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z"
  }
]
```

Example 2b
---

Similarly, had all of the available **Units** been selected they would all be included with an integer value for each except for the least significant, *Seconds*:

```
[
  {
    "timedelta": {
      "days": 0,
      "hours": 0,
      "minutes": 42,
      "seconds": 3.141593
    },
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z"
  }
]
```

Example 2c
===

If a single item from **Units** is selected, for example *Hours*:

```
[
  {
    "timedelta": {
      "hours": 0.7
    },
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z"
  }
]
```
