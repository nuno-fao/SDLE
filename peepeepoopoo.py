import pytz
from datetime import datetime
from tzlocal import get_localzone

# time, tz = str(datetime.now()), str(get_localzone())

# pt_time = pytz.timezone(tz)
# us_time = pytz.timezone('America/New_York')

# pt = pt_time.localize(datetime(time))
# en = pt.astimezone(us_time).strftime("%Y-%m-%d %H:%M:%S")

# print(time, tz)
# print(en,'America/New_York')

# newyork_tz = timezone('America/New_York')
# berlin_tz = timezone('Europe/Berlin')

# newyork = newyork_tz.localize(datetime(2018, 5, 1, 8, 0, 0))
# berlin = newyork.astimezone(berlin_tz)
# print(newyork)
# print(berlin)


print(str(datetime.now()).split('.')[0])