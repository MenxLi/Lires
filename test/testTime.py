import datetime
from resbibman.core.utils import TimeUtils

print(datetime.datetime.now())
utc = TimeUtils.utcNow()
print(utc)
now = TimeUtils.utc2Local(utc)
print(now)

time_str = "2022-09-12 13:51:01"
dt = TimeUtils.strLocalTimeToDatetime(time_str)
print(dt)
print(dt.timestamp())
dt = TimeUtils.local2Utc(dt)
print(dt)
print(dt.timestamp())
dt_local = TimeUtils.stamp2Local(dt.timestamp())
print(dt_local)
dt_utc = TimeUtils.stamp2Utc(dt.timestamp())
print(dt_utc)


stp = TimeUtils.utcNow().timestamp()
dt = TimeUtils.stamp2Local(stp)
print(dt.strftime("%Y-%m-%d %H:%M:%S"))
