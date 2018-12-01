#!/usr/bin/env python
from csv import DictReader
from datetime import datetime, timedelta
import sys

from icalendar import Calendar, Event, vDate, vDatetime

import unittest
class Tests(unittest.TestCase):
    def test_mk_time(self):
        cases = [
            ("Wed Nov 7 14:35 2018", "20181107T143500"),
            ("Thu Nov 8 2018", "20181108"),
            ("Nov 7 14:35 2018", "20181107T143500"),
            ("Nov 01 2018", "20181101"),
            ("Nov 1 2018", "20181101"),
            ("Nov 07 14:35 2018", "20181107T143500"),
            ("Nov 7 14:35 2018", "20181107T143500"),
            ("Nov 7 2:35PM 2018", "20181107T143500"),
            ("11/7/2018 2:35PM", "20181107T143500"),
        ]
        for case in cases:
            self.assertEqual(case[1], mk_time(case[0]).to_ical())

    def test_mk_time_exc(self):
        bad_date = "foo"
        with self.assertRaises(DateParseError):
            mk_time(bad_date)


class DateParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Parse error: " + self.value

def mk_time(value):
    dateFormats = [
      # Thu Nov 8 2018
      "%a %b %d %Y",
      # Nov 8 2018
      "%b %d %Y",
    ]
    dateTimeFormats = [
      # Wed Nov 7 14:35 2018
      "%a %b %d %H:%M %Y",
      # Nov 7 14:35 2018
      "%b %d %H:%M %Y",
      # Nov 7 2:35PM 2018
      "%b %d %I:%M%p %Y",
      # 11/7/2018 2:35PM
      "%m/%d/%Y %I:%M%p",
    ]
    for fmt in dateFormats:
        try:
            return vDate(datetime.strptime(value, fmt))
        except ValueError as e:
            continue

    for fmt in dateTimeFormats:
        try:
            return vDatetime(datetime.strptime(value, fmt))
        except ValueError as e:
            continue

    # nothing worked!
    raise DateParseError(value)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        unittest.main()
        sys.exit()

    cal = Calendar()
    cal.add('prodid', '-//aaronferrucci//csv2ics//')
    cal.add('version', '2.0')

    with open(sys.argv[1]) as fp:
        reader = DictReader(fp, delimiter='\t')
        for item in reader:
            start = mk_time(item['start'])
            end = mk_time(item['end'])

            event = Event()
            event.add('summary', item['summary'])
            event.add('description', item['description'])
            event.add('location', item['location'])
            event.add('dtstart', start)
            event.add('dtend', end)

            cal.add_component(event)

    print cal.to_ical()
