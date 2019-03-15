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

The timestamps are compared, and the delta of `Timestamp B - Timestamp A` is parsed according to any selected **Units** and added to the incoming signal in the **Outgoing Signal Attribute**. Because each of **Units** is de-selected by default, in this example the elapsed time is represented individually with each unit, with decimal places, in the output:

```
[
  {
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z",
    "timedelta": {
      "days": 0.029166...,
      "hours": 0.700873...,
      "minutes": 42.074799...,
      "seconds": 2523.142
    }
  }
]
```

To put it another way, if each of **Units** is `False` then the values in **Outgoing Signal Attribute** all represent the same time interval using different units.

Example 2a
---

If selecting one or more **Units**, the computed duration between **Timestamp A** and **Timestamp B** will be represented in terms of those units in **Outgoing Signal Attribute**. The least significant of the **Units** selected will be a floating-point number (with a decimal), while all others will be (whole) integers. This is useful, for example, when preparing data for a human to read.

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
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z",
    "timedelta": {
      "hours": 0,
      "minutes": 42.074799...
    }
  }
]
```

Example 2b
---

Similarly, with all of the available **Units** selected, each will be truncated to an integer value, except for the least significant, *Seconds*, which is a float:

```
[
  {
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z",
    "timedelta": {
      "days": 0,
      "hours": 0,
      "minutes": 42,
      "seconds": 3.142
    }
  }
]
```

Example 2c
===

If a single item from **Units** is selected, for example *Hours*, the entire timedelta is represented only in terms of that **Unit**:

```
[
  {
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z",
    "timedelta": {
      "hours": 0.700873...
    }
  }
]
```
