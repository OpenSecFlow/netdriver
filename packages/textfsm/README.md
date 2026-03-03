# netdriver-textfsm

An enhanced [Google TextFSM](https://github.com/google/textfsm) parsing engine for converting semi-structured CLI output from network devices into structured data.

## Usage

```python
from netdriver_textfsm import TextFSMParser

template = """Value INTERFACE (\S+)
Value STATUS (up|down)

Start
  ^${INTERFACE}\s+${STATUS} -> Record
"""

parser = TextFSMParser(template)
result = parser.parse(cli_output)
```

## Enhancements over Google TextFSM

### New Value Options

| Option | Description |
|--------|-------------|
| `TmpFilldown` | Similar to `Filldown`, but the temporary value is cleared on `Clear` operations (whereas `Filldown` preserves its value). Useful for inheriting values across lines within a Block while resetting between Blocks. |
| `GroupBy` | Marks a Value as a grouping key. During `ParseTextToDicts` post-processing, records sharing the same `GroupBy` values are merged into a single record, with remaining fields aggregated into a `groups` list. |
| `ExcludeGroup` | Used with `GroupBy`. Marked Values are kept as top-level fields in the grouped record (last non-empty value wins) instead of being placed into the `groups` list. |

> In the original TextFSM, the `Key` option is a marker with no runtime behavior. In this enhanced version, `Key` drives record merging during `ParseTextToDicts` post-processing — records with the same `Key` values are merged, `List`-typed fields are concatenated, and other fields take the last non-empty value.

### New Record Operators

| Operator | Description |
|----------|-------------|
| `RecordLine` | Immediately records the current line into `BLOCK_RECORD`, commits the current record, and ends Block recording. |
| `RecordLastMatched` | Removes the last line from `BLOCK_RECORD`, then commits the current record. |
| `RecordGroupBy` | Commits the current record and re-enters Block recording mode. Used to split multiple records within a continuous state. |
| `RecordPrefixEq` | Splits `BLOCK_RECORD` based on where the current line's first character appears in the first recorded line — truncates prior content as one record and restarts recording with the full original line. Useful for splitting config blocks by indentation level. |
| `RecordFirstAndLast` | Commits the current record but carries over the first line of `BLOCK_RECORD` into the new Block. Useful when the first line needs to be shared across multiple records. |
| `RecordAndRawConf` | Commits the current record and rewinds the parse position to the raw config line number. Enables re-reading from the original position after parsing structured data (dual-pass parsing). |

### Block Record Mechanism

The original TextFSM has no Block Record support. This enhanced version adds a complete Block recording mechanism:

- **`BLOCK_RECORD` column**: Automatically appended to each output record as an `OrderedDict` keyed by line number with raw line content as values, preserving the original CLI output that produced the record.
- **`BL_` state naming convention**: When the state machine transitions from `Start` to a state prefixed with `BL_`, raw line recording begins automatically; transitioning from a `BL_` state to a non-`BL_` state stops recording.
- **`BL_RAW_CONF_` / `BL_PARSER_` dual-pass**: Supports recording raw config in a `BL_RAW_CONF_` state first, then jumping to a `BL_PARSER_` state for structured field parsing, combined with `RecordAndRawConf` for dual-pass parsing.

### Continue with State Transition

The original TextFSM does not allow `Continue` to specify a new state. This enhanced version removes that restriction, allowing `Continue` and state transitions to be used together — the FSM continues matching the current line while switching to the new state.

### Enhanced Clear Behavior

The original `Clear` operation calls `ClearVar`, which preserves `Filldown` values. The enhanced version calls `ClearTmpFilldownAndOtherVar` instead, which also clears the `TmpFilldown` temporary value, resetting it to empty rather than inheriting from the previous line.
