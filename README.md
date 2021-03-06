timestamps
===
Blocks for working with [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted date and time information.

Blocks in this Collection
===
- [AddTimestamp](docs/add_timestamp_block.md)
- [ElapsedTime](docs/elapsed_time_block.md)

Dependencies
===
- [tzlocal 1.5.1](https://pypi.org/project/tzlocal/1.5.1/)

Notes
===
These blocks implement [SignalEnrichment](https://docs.n.io/blocks/block-mixins/enrich-signals.html) with a custom subclass of `EnrichProperties` so that `EnrichProperties.exclude_existing` has a default value of `False`.
