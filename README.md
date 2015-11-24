# EstimateStories

Estimate stories - a tool to help with estimating software deadlines


----

# Structure of stories file

Stories are stored in a simple plain text file.
However, there are certain conventions that **MUST** be followed for the
tool to work correctly.

Est is a simple tool at its core - it reads a file, analyzes it and
spits out some data.
The conventions that must be followed are there to make the input processable.

Each *story* in a file is a group of *keys*.
Every *key* begins with the `@` character and **MUST** begin on the first column of a line.
Key groups should be separated by at least one non-key line.

There are several keys that are recognied by Est.
Some of them are obligatory, some optional.

**Obligatory keys**:

- `@Subject:` one line description of a task,

**Optional keys**:

- `@EstReal:` realistic estimate,
- `@EstOpti:` optimistic estimate,
- `@EstPess:` pessimistic estimate,

Estimate keys (the ones beginning with `@Est`) **MUST** contain values in
the following format: `<number><time-class>`.
One or more of such time specifications may be given for each estimate key, and
they will be summed for the final report.

### Explanation of the time specification format

The `<number>` part is a decimal integer.
The `<time-class>` part may be one of the following time classes:

- `hours?`: specified number of hours should be assigned to the task,
- `days?`: specified number of days should be assigned to the task,
- `weeks?`: specified number of weeks should be assigned to the task,
- `months?`: specified number of months should be assigned to the task,

The `@Subject:` key begins a key group.
A key group goes until the next `@Subject:` key or an END-OF-FILE is encountered.
Optional keys **MUST** appear only *once* in a given group, or an error will be raised.

Apart from the structure described above stories files are free form, as
long as there are no non-key lines beginning with the `@` character.


## Example

```
@Subject: Implement C++ lexer
@EstReal: 3months 3weeks
@EstPess: 6months

Implement an efficient, context-aware C++ lexer.

----

@Subject: Implement Python lexer
@EstReal: 2weeks
@EstPess: 1month

----

@Subject: Learn to estimate software development schedules
@EstOpti: 120months 2weeks 1day 8hours
```
