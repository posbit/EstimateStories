#!/usr/bin/env python3

import math
import os
import sys
import re


estimate_file_path = sys.argv[1]
print('estimates taken from: {0}'.format(estimate_file_path))

estimate_lines = []
with open(estimate_file_path) as ifstream:
    estimate_lines = ifstream.read().splitlines()


def isMeaningful(line):
    return (line.startswith('@Subject: ') or line.startswith('@EstOpti: ') or line.startswith('@EstReal: ') or line.startswith('@EstPess: '))

estimate_meaningful_lines = [line for line in estimate_lines if isMeaningful(line)]


def consume(lines, offset):
    if len(lines) < offset:
        raise IndexError('offset too big: {0} < {1}'.format(len(lines), offset))
    if not lines:
        raise IndexError('list empty')
    if not lines[0].startswith('@Subject: '):
        raise Exception('bad ordering (start)')

    est_attributes = {
        'subject': None,
        'optimistic': None,
        'realistic': None,
        'pessimistic': None,
    }

    tokens = [lines[offset]]

    i = 1
    while (offset+i) < len(lines):
        if lines[offset+i].startswith('@Subject: '):
            break
        tokens.append(lines[offset+i])
        i += 1

    for t in tokens:
        if t.startswith('@Subject: '):
            if est_attributes['subject'] is None:
                est_attributes['subject'] = t[len('@Subject: '):]
            else:
                raise Exception('bad ordering')
        if t.startswith('@EstOpti: '):
            if est_attributes['optimistic'] is None:
                est_attributes['optimistic'] = t[len('@EstOpti: '):]
            else:
                raise Exception('bad ordering')
        if t.startswith('@EstReal: '):
            if est_attributes['realistic'] is None:
                est_attributes['realistic'] = t[len('@EstReal: '):]
            else:
                raise Exception('bad ordering')
        if t.startswith('@EstPess: '):
            if est_attributes['pessimistic'] is None:
                est_attributes['pessimistic'] = t[len('@EstPess: '):]
            else:
                raise Exception('bad ordering (inside)')

    est_keys = ['optimistic', 'pessimistic', 'realistic']
    for k in est_keys:
        if est_attributes[k] is not None:
            est_attributes[k] = [p for p in est_attributes[k].split() if p.strip()]
        else:
            est_attributes[k] = []
        est_attributes[k + '_hours'] = 0

    time_patterns = {
        'hours': re.compile('^(\d+)(hours?)$'),
        'days': re.compile('^(\d+)(days?)$'),
        'weeks': re.compile('^(\d+)(weeks?)$'),
        'months': re.compile('^(\d+)(months?)$'),
    }

    for k in est_keys:
        total_est_hours = 0
        for time_chunk in est_attributes[k]:
            for pattern_name, p in time_patterns.items():
                pm = p.match(time_chunk)
                increase = 0

                if pm is not None:
                    increase += int(pm.group(1))

                if pattern_name == 'days':
                    increase *= 24
                if pattern_name == 'weeks':
                    increase *= (24 * 5)
                if pattern_name == 'months':
                    increase *= (24 * 5 * 4)

                total_est_hours += increase
        est_attributes[k + '_hours'] = total_est_hours

    if not est_attributes['optimistic_hours'] and not est_attributes['realistic_hours']:
        est_attributes['realistic_hours'] = 2
        est_attributes['optimistic_hours'] = 1
    if not est_attributes['optimistic_hours'] and est_attributes['realistic_hours']:
        est_attributes['optimistic_hours'] = int(math.ceil(est_attributes['realistic_hours'] * 0.7))
    if est_attributes['optimistic_hours'] and not est_attributes['realistic_hours']:
        est_attributes['realistic_hours'] = int(math.ceil(est_attributes['optimistic_hours'] * 1.2))
    if not est_attributes['pessimistic_hours'] and est_attributes['realistic_hours']:
        est_attributes['pessimistic_hours'] = int(math.ceil(est_attributes['realistic_hours'] * 1.6))

    return (est_attributes, i)


preprocessed_lines = []
i = 0
while i < len(estimate_meaningful_lines):
    estimate, inc = consume(estimate_meaningful_lines, i)
    preprocessed_lines.append(estimate)
    i += inc


optimistic = 0
expected = 0
average = 0
pessimistic = 0
for est in preprocessed_lines:
    optimistic += est['optimistic_hours']
    expected += est['realistic_hours']
    pessimistic += est['pessimistic_hours']
    average += ((est['optimistic_hours'] + est['pessimistic_hours']) / 2)


# it is common sense to add ten percent more to your programming task time estimates
# increase it for wider safety magin
common_sense_multiplier = 1.1

optimistic = round((optimistic * (common_sense_multiplier + 0.1)), 4)  # add ten percent to optimistic estimate
expected = round((expected * common_sense_multiplier), 4)
average = round((average * common_sense_multiplier), 4)
pessimistic = round((pessimistic * (common_sense_multiplier + 0.1)), 4)  # add ten percent to pessimistic estimate


# print('DETAILS:')
# for est in preprocessed_lines:
#     print('  {0}: {1}h / {2}h / {3}h'.format(est['subject'], est['realistic_hours'], est['optimistic_hours'], est['pessimistic_hours']))

print('SUMMARY:')
print('  expected:    {0} hours ({1} days)'.format(expected, (round((expected / 24), 2))))
print('  optimistic:  {0} hours ({1} days)'.format(optimistic, (round((optimistic / 24), 2))))
print('  pessimistic: {0} hours ({1} days)'.format(pessimistic, (round((pessimistic / 24), 2))))
print('  average:     {0} hours ({1} days)'.format(average, (round((average / 24), 2))))
