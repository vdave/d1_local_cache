'''
Created on May 29, 2013

@author: vieglais

Copied directly from:
  http://asimpleweblog.wordpress.com/2010/06/20/julian-date-calculator/
'''

import math
import datetime
import pytz

MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours 

def base60_to_decimal(xyz,delimiter=None):
  """Decimal value from numbers in sexagesimal system. 

 The input value can be either a floating point number or a string
 such as "hh mm ss.ss" or "dd mm ss.ss". Delimiters other than " "
 can be specified using the keyword ``delimiter``.
 """
  divisors = [1,60.0,3600.0]
  xyzlist = str(xyz).split(delimiter)
  sign = -1 if xyzlist[0].find("-") != -1 else 1
  xyzlist = [abs(float(x)) for x in xyzlist]
  decimal_value = 0 

  for i,j in zip(xyzlist,divisors): # if xyzlist has <3 values then
                                    # divisors gets clipped.
    decimal_value += i/j

  decimal_value = -decimal_value if sign == -1 else decimal_value
  return decimal_value


def decimal_to_base60(deci,precision=1e-8):
  """Converts decimal number into sexagesimal number parts. 

 ``deci`` is the decimal number to be converted. ``precision`` is how
 close the multiple of 60 and 3600, for example minutes and seconds,
 are to 60.0 before they are rounded to the higher quantity, for
 example hours and minutes.
 """
  sign = "+" # simple putting sign back at end gives errors for small
             # deg. This is because -00 is 00 and hence ``format``,
             # that constructs the delimited string will not add '-'
             # sign. So, carry it as a character.
  if deci < 0:
    deci = abs(deci)
    sign = "-" 

  frac1, num = math.modf(deci)
  num = int(num) # hours/degrees is integer valued but type is float
  frac2, frac1 = math.modf(frac1*60.0)
  frac1 = int(frac1) # minutes is integer valued but type is float
  frac2 *= 60.0 # number of seconds between 0 and 60 

  # Keep seconds and minutes in [0 - 60.0000)
  if abs(frac2 - 60.0) < precision:
    frac2 = 0.0
    frac1 += 1
  if abs(frac1 - 60.0) < precision:
    frac1 = 0.0
    num += 1 

  return (sign,num,frac1,frac2)


def julian_date(year,month,day,hour,minute,second):
  """Given year, month, day, hour, minute and second return JD.

 ``year``, ``month``, ``day``, ``hour`` and ``minute`` are integers,
 truncates fractional part; ``second`` is a floating point number.
 For BC year: use -(year-1). Example: 1 BC = 0, 1000 BC = -999.
 """
  MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours 

  year, month, day, hour, minute =\
  int(year),int(month),int(day),int(hour),int(minute)

  if month <= 2:
    month +=12
    year -= 1 

  modf = math.modf
  # Julian calendar on or before 1582 October 4 and Gregorian calendar
  # afterwards.
  if ((10000L*year+100L*month+day) <= 15821004L):
    b = -2 + int(modf((year+4716)/4)[1]) - 1179
  else:
    b = int(modf(year/400)[1])-int(modf(year/100)[1])+\
        int(modf(year/4)[1]) 

  mjdmidnight = 365L*year - 679004L + b + int(30.6001*(month+1)) + day

  fracofday = base60_to_decimal(\
    " ".join([str(hour),str(minute),str(second)])) / 24.0 

  return MJD0 + mjdmidnight + fracofday


def caldate(mjd):
  """Given mjd return calendar date. 

 Retrns a tuple (year,month,day,hour,minute,second). The last is a
 floating point number and others are integers. The precision in
 seconds is about 1e-4. 

 To convert jd to mjd use jd - 2400000.5. In this module 2400000.5 is
 stored in MJD0.
 """
  MJD0 = 2400000.5 # 1858 November 17, 00:00:00 hours 

  modf = math.modf
  a = long(mjd+MJD0+0.5)
  # Julian calendar on or before 1582 October 4 and Gregorian calendar
  # afterwards.
  if a < 2299161:
    b = 0
    c = a + 1524
  else:
    b = long((a-1867216.25)/36524.25)
    c = a+ b - long(modf(b/4)[1]) + 1525 

  d = long((c-122.1)/365.25)
  e = 365*d + long(modf(d/4)[1])
  f = long((c-e)/30.6001)

  day = c - e - int(30.6001*f)
  month = f - 1 - 12*int(modf(f/14)[1])
  year = d - 4715 - int(modf((7+month)/10)[1])
  fracofday = mjd - math.floor(mjd)
  hours = fracofday * 24.0 

  sign,hour,minute,second = decimal_to_base60(hours)

  return (year,month,day,int(sign+str(hour)),minute,second)


def dateTime2MJD(dt):
  sec = dt.second + dt.microsecond / 1000.0
  jnow = julian_date(dt.year, dt.month, dt.day, 
                     dt.hour, dt.minute, sec)
  return jnow - MJD0 
  

def MJD2dateTime(mjd):
  dt = caldate(mjd)
  return datetime.datetime(int(dt[0]), int(dt[1]), int(dt[2]), int(dt[3]), int(dt[4]), int(dt[5]), 0, pytz.utc)  


def now():
  '''Returns MJD for right now, UTC
  '''
  dnow = datetime.datetime.utcnow()
  sec = dnow.second + dnow.microsecond / 1000.0
  jnow = julian_date(dnow.year, dnow.month, dnow.day, 
                     dnow.hour, dnow.minute, sec)
  return jnow - MJD0 



if __name__ == '__main__':
  print "Julian date for 2010/1/1 13:20:12.3456 : ",
  j = julian_date(2010,1,1,13,20,12.3456)
  print j
  print "Calendar date for MJD "+ str(j-MJD0) + " (jd = " + str(j)+" )"
  print "Year: {0}, Month: {1}, Day: {2}, Hour: {3}, Minute: {4},\
 Second: {5:8.5f}".format(*caldate(j-MJD0))
  print "MJD for now = %.5f" % (now())
 