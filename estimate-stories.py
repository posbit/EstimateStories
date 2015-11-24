#!/usr/bin/env python3

import math
import os
import sys
import re


# it is common sense to add ten percent more to your programming task time estimates
# increase it for wider safety magin
common_sense_multiplier = 1.1

pessimistic_coefficient = 0.1

# make it 8 to get work-days schedule
# make it 24 to get unrealistic schedule
HOURS_IN_A_DAY = 8

ROUND_TO = 2


def isMeaningful(line):
    return (line.startswith('@Subject: ') or line.startswith('@EstOpti: ') or line.startswith('@EstReal: ') or line.startswith('@EstPess: ') or line.startswith('@DoneAfter: ') or line.startswith('@WorkInProgress: '))

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
        'done_after': None,
        'work_in_progress': None,
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
        if t.startswith('@DoneAfter: '):
            est_attributes['done_after'] = t[len('@DoneAfter: '):]
        if t.startswith('@WorkInProgress: '):
            est_attributes['work_in_progress'] = t[len('@WorkInProgress: '):]

    est_keys = ['optimistic', 'pessimistic', 'realistic', 'done_after', 'work_in_progress']
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

def process(estimate_file_path):
    print(estimate_file_path)
    estimate_lines = []
    with open(estimate_file_path) as ifstream:
        estimate_lines = ifstream.read().splitlines()

    estimate_meaningful_lines = [line for line in estimate_lines if isMeaningful(line)]

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
    left_optimistic = 0
    left_expected = 0
    left_average = 0
    left_pessimistic = 0
    tasks_in_progress = 0
    tasks_done = 0
    work_in_progress = 0
    done_after = 0
    for est in preprocessed_lines:
        optimistic += est['optimistic_hours']
        expected += est['realistic_hours']
        pessimistic += est['pessimistic_hours']
        average += ((est['optimistic_hours'] + est['pessimistic_hours']) / 2)

        if not est['done_after'] and not est['work_in_progress']:
            left_optimistic += est['optimistic_hours']
            left_expected += est['realistic_hours']
            left_pessimistic += est['pessimistic_hours']
            left_average += ((est['optimistic_hours'] + est['pessimistic_hours']) / 2)
        if not est['done_after'] and est['work_in_progress']:
            left_optimistic += (est['optimistic_hours'] - est['work_in_progress_hours'])
            left_expected += (est['realistic_hours'] - est['work_in_progress_hours'])
            left_pessimistic += (est['pessimistic_hours'] - est['work_in_progress_hours'])
            left_average += ((est['optimistic_hours'] + est['pessimistic_hours'] - (est['work_in_progress_hours'] / 2)) / 2)

        if est['done_after']:
            tasks_done += 1
            done_after += est['done_after_hours']
        if est['work_in_progress']:
            tasks_in_progress += 1
            work_in_progress += est['work_in_progress_hours']

    optimistic = round((optimistic * (common_sense_multiplier + pessimistic_coefficient)), 4)  # take pessimistic coefficient into account for optimistic estimate
    expected = round((expected * common_sense_multiplier), 4)
    average = round((average * common_sense_multiplier), 4)
    pessimistic = round((pessimistic * (common_sense_multiplier + pessimistic_coefficient)), 4)  # take pessimistic coefficient into account for pessimistic estimate

    return (preprocessed_lines, expected, optimistic, pessimistic, average, left_expected, left_optimistic, left_pessimistic, left_average, work_in_progress, done_after, tasks_in_progress, tasks_done)

def estimateTasksTime(story_files):
    e_preprocessed_lines, e_expected, e_optimistic, e_pessimistic, e_average, e_left_expected, e_left_optimistic, e_left_pessimistic, e_left_average, e_work_in_progress, e_done_after, e_tasks_in_progress, e_tasks_done = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    tasks_per_file = []
    for sf in story_files:
        preprocessed_lines, expected, optimistic, pessimistic, average, left_expected, left_optimistic, left_pessimistic, left_average, work_in_progress, done_after, tasks_in_progress, tasks_done = process(sf)
        tasks_per_file.append((sf, len(preprocessed_lines)))
        e_preprocessed_lines += len(preprocessed_lines)
        e_expected += expected
        e_optimistic += optimistic
        e_pessimistic += pessimistic
        e_average += average
        e_left_expected += left_expected
        e_left_optimistic += left_optimistic
        e_left_pessimistic += left_pessimistic
        e_left_average += left_average
        e_work_in_progress += work_in_progress
        e_done_after += done_after
        e_tasks_in_progress += tasks_in_progress
        e_tasks_done += tasks_done
    return tasks_per_file, e_preprocessed_lines, e_expected, e_optimistic, e_pessimistic, e_average, e_left_expected, e_left_optimistic, e_left_pessimistic, e_left_average, e_work_in_progress, e_done_after, e_tasks_in_progress, e_tasks_done

def toDays(hours):
    r = round((hours / HOURS_IN_A_DAY), ROUND_TO)
    if ROUND_TO == 0:
        r = int(r)
    return r

tasks_per_file, preprocessed_lines, expected, optimistic, pessimistic, average, left_expected, left_optimistic, left_pessimistic, left_average, work_in_progress, done_after, tasks_in_progress, tasks_done = estimateTasksTime(sys.argv[1:])

print('SUMMARY')
print('  TASKS:')
for tasks_file, tasks_no in tasks_per_file:
    print('    {0}: {1} task(s)'.format(tasks_file, tasks_no))
print()
print('  ESTIMATED:')
print('    expected:    {0} hours ({1} days)'.format(expected, toDays(expected)))
print('    optimistic:  {0} hours ({1} days)'.format(optimistic, toDays(optimistic)))
print('    pessimistic: {0} hours ({1} days)'.format(pessimistic, toDays(pessimistic)))
print('    average:     {0} hours ({1} days)'.format(average, toDays(average)))
print()
print('  LEFT:')
print('    expected:    {0} hours ({1} days)'.format(left_expected, toDays(left_expected)))
print('    optimistic:  {0} hours ({1} days)'.format(left_optimistic, toDays(left_optimistic)))
print('    pessimistic: {0} hours ({1} days)'.format(left_pessimistic, toDays(left_pessimistic)))
print('    average:     {0} hours ({1} days)'.format(left_average, toDays(left_average)))
print()
print('  FINISHED:')
print('    not started:      {0} task(s)'.format((preprocessed_lines - tasks_in_progress - tasks_done)))
print('    work in progress: {0} task(s) - {1} hours ({2} days)'.format(tasks_in_progress, work_in_progress, toDays(work_in_progress)))
print('    finished:         {0} task(s) - {1} hours ({2} days)'.format(tasks_done, done_after, toDays(done_after)))
