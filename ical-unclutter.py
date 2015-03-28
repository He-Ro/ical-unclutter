#! /usr/bin/python

# For information on the calendar format,
# see the iCal specification:
#   http://tools.ietf.org/html/rfc2445
# and the icalendar implementation:
#   https://github.com/collective/icalendar/tree/master/src/icalendar

from icalendar import Calendar, Event, vPeriod, vDatetime, Parameters, vRecur, vFrequency
from icalendar.prop import vDDDLists
import sys
import argparse
import fractions
import functools
from datetime import timedelta

secsInDay = 24 * 60 * 60

def areSimilar(event, otherEvent):
	return (event.get('summary') == otherEvent.get('summary') and
	event.get('class') == otherEvent.get('class') and
	event.get('location') == otherEvent.get('location') and
	event.get('description') == otherEvent.get('description') and
	event.get('categories') == otherEvent.get('categories') and
	event.get('dtstart').dt.hour == otherEvent.get('dtstart').dt.hour and
	event.get('dtstart').dt.minute == otherEvent.get('dtstart').dt.minute and
	event.get('dtstart').dt.second == otherEvent.get('dtstart').dt.second and
	event is not otherEvent)

def extractSimilarEvents(cal):
	newEvents = []
	for event in cal.walk("vEvent"):
		# compare event with all existing events
		for (existingEvent, similarDates) in newEvents:
			# check if the event date can be added to the similar dates
			if areSimilar(event, existingEvent):
				start = event.get('dtstart')
				end = event.get('dtend')
				similarDates.append((start, end))
				break
		else:
			# only gets executed, if the for loop exits cleanly (not by break)
			newEvents.append((event, []))
	return newEvents

def addOtherDates(event, otherDates):
	if len(otherDates) > 0:
		start = event["dtstart"]
		differenceInSecs = []
		for (otherStart, otherEnd) in otherDates:
			assert (otherStart.dt - start.dt).total_seconds() > 0
			assert otherEnd.dt - otherStart.dt == event["dtend"].dt - start.dt
			differenceInSecs.append((otherStart.dt - start.dt).total_seconds())
		intervalSecs = int(gcd(differenceInSecs))
		assert intervalSecs % secsInDay == 0
		exdiffs = sorted(list(set(range(intervalSecs, int(max(differenceInSecs)), intervalSecs)) -
						set([int(x) for x in differenceInSecs])))
		exdates = vDDDLists([(start.dt + timedelta(seconds=difference)) for difference in exdiffs])
		until = (start.dt + timedelta(seconds=max(differenceInSecs)))
		if (intervalSecs % 7 == 0):
			recur = vRecur({"FREQ": vFrequency("WEEKLY"),
							"INTERVAL": intervalSecs / secsInDay / 7,
							"UNTIL": until})
		else:
			recur = vRecur({"FREQ": vFrequency("DAILY"),
							"INTERVAL": intervalSecs / secsInDay,
							"UNTIL": until})
		event.add("RRULE", recur)
		event.add("EXDATE", exdates)
	return event

def gcd(L):
	return functools.reduce(fractions.gcd, L)

def main():
	# set up the command line arguments for this script
	parser = argparse.ArgumentParser(description='Refactor ical files.')
	parser.add_argument('input', metavar="INPUT", type=argparse.FileType('r'),
						help="iCal file that needs uncluttering")
	parser.add_argument('-o', '--output', metavar="OUTPUT",
						type=argparse.FileType('wb', 0),
						default=sys.stdout.buffer,
						help="refactored ical file (default: stdout)")

	# get the calendar
	args = parser.parse_args()
	cal = Calendar.from_ical(args.input.read())

	events = extractSimilarEvents(cal)

	# remove all events from the calendar
	cal.subcomponents = [notEvent for notEvent in cal.subcomponents
						if not isinstance(notEvent, Event)]

	# re-add all events
	for (event, otherDates) in events:
		event = addOtherDates(event, otherDates)
		cal.add_component(event)

	args.output.write(cal.to_ical())

if  __name__ =='__main__':main()
