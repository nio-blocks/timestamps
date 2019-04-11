ElapsedTime
===
Compare Two [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted timestamps, **Timestamp A** and **Timestamp B**, and add the elapsed time delta information to each incoming signal. Computed time deltas account for timezone offsets. The total elapsed time can be represented in any or all of four **Units**: *Days*, *Hours*, *Minutes*, and *Seconds*. These values can be negative in the case that **Timestamp A** is later than **Timestamp B**.

See Also: [*AddTimestamp*](https://blocks.n.io/AddTimestamp) for creating timestamps.

Properties
===
- **Timestamp A**: An ISO timestamp string.
- **Timestamp B**: An ISO timestamp string, in most cases this is the later of the two times, often corresponding to the present.

Advanced Properties
---
- **Units** (advanced): Options for representing the total time delta.
  - *Days*: default `False`
  - *Hours*: default `False`
  - *Minutes*: default `False`
  - *Seconds*: default `False`
- **Include Milliseconds**: default `True`. When de-selected, milliseconds in incoming timestamps will be ignored.

Examples
===

Example 1
---
Configure the block to compare timestamps in an incoming signal:

```
Timestamp A: {{ $past }}
Timestamp B: {{ $present }}
```

Process a list of signals; these timestamps are in Nepal Standard Time (`+0545`) and UTC (`Z`), respectively, and the computed delta will account for these offsets:

```
[
  {
    "past": "1984-05-03T05:45:00+0545",
    "present": "1984-05-04T12:42:03.142Z"
  }
]
```

The timestamps are compared, and the delta of `Timestamp B - Timestamp A` is parsed according to any selected **Units** and added to the incoming signal in the **Outgoing Signal Attribute**. In this example each timestamp uses a different timezone offset and includes (optional) milliseconds. Timezone offsets (including Daylight Savings Time adjustments) are accounted for and therefore all timestamps must include the UTC offset in the format `±HHMM`

Because each of **Units** is de-selected by default, in this example the elapsed time is represented individually with each unit, with decimal places, in `$timedelta`

```
[
  {
    "past": "1984-05-03T05:45:00+0545",
    "present": "1984-05-04T12:42:03.142Z",
    "days": 1.529...,
    "hours": 36.700...,
    "minutes": 2202.052...,
    "seconds": 132123.142
  }
]
```

To put it another way, if each of **Units** is `False` then the values in **Outgoing Signal Attribute** all represent the same time interval using different units. Notice that by default the incoming signal's fields are included in the outgoing signal.

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
    "past": "1984-05-03T05:45:00+0545",
    "present": "1984-05-04T12:42:03.142Z"
  }
]
```

Less than one full hour has elapsed from **Timestamp A** to **Timestamp B** so `$timedelta['hours']` is zero, while `$timedelta['minutes']` includes the less significant, de-selected *Seconds* unit in its decimal:

```
[
  {
    "past": "1984-05-03T05:45:00+0545",
    "present": "1984-05-04T12:42:03.142Z",
    "hours": 36,
    "minutes": 42.052...,
  }
]
```

Example 2b
---

Similarly, with all of the available **Units** selected, each will be truncated to an integer value, except for the least significant, *Seconds*, which is a float:

```
[
  {
    "past": "1984-05-03T05:45:00+0545",
    "present": "1984-05-04T12:42:03.142Z",
    "days": 1,
    "hours": 12,
    "minutes": 42,
    "seconds": 3.142
  }
]
```

Example 2c
---

If a single item from **Units** is selected, for example *Hours*, the entire timedelta is represented only in terms of that **Unit**:

```
[
  {
    "past": "1984-05-03T00:00:00.000Z",
    "present": "1984-05-03T00:42:03.142Z",
    "hours": 36.700...
  }
]
```

Example 3
---

When **Include Milliseconds** is `False`, incoming timstamps will be truncated to whole seconds. In this example, two timestamps are only 0.001 second apart, but the computed delta will be `1` because each timestamp was truncated to whole seconds before comparison. This is distinct from truncating the computed timedelta, in which case the result would have been `0`

Configure the block:

```
Timestamp A: "1999-12-31T23:59:59.999Z"
Timestamp B: "2000-01-01T00:00:00.000Z"
Units:
  Days: True
  Hours: True
  Minutes: True
  Seconds: True
Include Milliseconds: False
```

All values in the outgoing signal are integers:

```
[
  {
    "days": 0,
    "hours": 0,
    "minutes": 0,
    "seconds": 1
  }
]
```

Example 4
---

The [SignalEnrichment](https://docs.n.io/blocks/block-mixins/enrich-signals.html)[SignalEnrichment](https://docs.n.io/blocks/block-mixins/enrich-signals.html) mixin can be leveraged to nest the time delta into a single, top-level attribute in the outgoing signal:

```
Timestamp A: {{ $past }}
Timestamp B: {{ $present }}
Signal Enrichment:
  Exclude Existing? True
  Results Field: {{ $output_attr }}
```

Process a list of signals:

```
[
  {
    "output_attr": "timedelta",
    "past": "1984-05-03T05:45:00+0545",
    "present": "1984-05-04T12:42:03.142Z"
  }
]
```

And the configured **Units** will be inside **Results Field**:

```
[
  {
    "timedelta": {
      "seconds": 132123.142
    }
  }
]
```
