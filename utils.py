#!/usr/bin/env python
#
# Author: Zhang Zhen
# E-Mail: zhangjoto@gmail.com
#
# Create Date: 2018-09-15
#

import datetime
import time


def next_time(timetuple):
    now = datetime.datetime.now()
    curtimestr = now.strftime('%H%M%S')

    items = [i for i in timetuple if i > curtimestr]
    if items:
        dst = min(items)
        delta = 0
    else:
        dst = min(timetuple)
        delta = 1

    t = {j: int(dst[i:i + 2]) for i, j in zip(range(0, len(dst), 2),
                                              ('hour', 'minute', 'second'))}

    day = now.replace(**t) + datetime.timedelta(days=delta)
    return day.timestamp()


def timestamp(secs):
    return time.strftime("%Y%m%d%H%M%S", time.localtime(secs))
