from dateutil.rrule import *
from datetime import datetime, timedelta

def strToTime(str):
    return datetime.strptime(str, '%b %d %Y %H:%M')
def strToDay(str):
    return datetime.strptime(str, '%b %d %Y %H:%M').replace(hour=0, minute=0)
def timeToStr(t):
    return t.strftime("%b %d %Y %H:%M")
"""
Function to handle date ranges
Input is a tuple of this form: (start date, end date, interval in minutes, excluded week days, work hours, work minutes)
    The first 3 are mandatory, first 2 will have this form:
        mmm dd YYYY HH:MM
        for example: 'Jun 7 2016  9:00'
    The third will be a the number of minutes separating each value in the output range list.
        Example: 60 will give a value for every hour
    The forth member is a comma separated list of days to exclude, for example : "SA, FR"
        The following short week day names must be used: SU, MO, TU, WE, TH, FR, SA
    The fifth member is a a string of the form "HH-HH" the represents business
    hours range in 24 hour format. range includes end hour.
        Example: '9-18'
    The last one is similar to work hours and defines minutes after start hour and end hour
"""
def getdaterange(timerange):
    start_date = strToTime(timerange[0]) #datetime.strptime(timerange[0], '%b %d %Y %H:%M')
    end_date = strToTime(timerange[1]) #datetime.strptime(timerange[1], '%b %d %Y %H:%M')
    interval = timerange[2]
    week_days = {"SU": SU, "MO": MO, "TU": TU, "WE": WE, "TH": TH, "FR": FR, "SA": SA}
    if len(timerange) > 3 and timerange[3]:
        for day in [x.replace(" ", "") for x in str(timerange[3]).split(",")]:
            del week_days[day]
    hours = range(0, 24)
    if len(timerange) > 4 and timerange[4]:
        rangebounds = [int(x) for x in str(timerange[4]).split("-")]
        hours = range(rangebounds[0], rangebounds[1]+1)
    minutes = range(0, 60)
    if len(timerange) > 5 and timerange[5]:
        rangebounds = [int(x) for x in str(timerange[5]).split("-")]
        minutes = range(rangebounds[0], rangebounds[1] + 1)
    times = rrule(MINUTELY,
                  dtstart=start_date,
                  until=end_date,
                  byweekday=week_days.values(),
                  byhour=hours,
                  byminute=minutes,
                  interval= interval)
    for single_date in times:
        yield timeToStr(single_date)#single_date.strftime("%b %d %Y %H:%M")

AllHours = [x for x in getdaterange(('Jun 7 2016  9:00', 'Jun 30 2016  18:00', 60, "SA", "9-18", "0-60"))]
# for X in AllHours:
#     print X

TestA = AllHours[0]
TestB = AllHours[10]
TestC = AllHours[20]
TestD = AllHours[30]
TestE = AllHours[40]
TestF = AllHours[40]

foo = lambda x,y: strToTime(x) + timedelta(hours=3) < strToTime(y) or strToTime(y) + timedelta(hours=3) < strToTime(x)

foo2 = foo = lambda x,y: abs((strToDay(x) - strToDay(y)).days) > 4
print  TestA, TestB
print foo(TestA,TestB)
print  TestA, TestD
print foo(TestA,TestD)
print  TestA, TestE
print foo(TestA,TestE)
print  TestA, TestF
print foo(TestA,TestF)

