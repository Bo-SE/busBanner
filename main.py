from tnbus import TNBus, API, By, Cond
from datetime import datetime
from pytz import timezone
from json import dump, load
from time import sleep

with open("auth") as f:
    t = TNBus(API(f.read().strip()), tz="CET")  # , preload=json.load(d))

# 25205x borino
# 25045x valoni discesa
# 25040z salè salita
# 25050- sommarive
# 21745z portaquila salita
# 25055z povo polo scientifico est

def load_stops():
    s = {}
    for i in t.get(TNBus.Stop, *((By.ID, i) for i in assoc.keys()), cond_mode=Cond.OR, override_unique=True):
        s[i.id] = i
    return s

i = 0

while True:
    if i == 0:
        assoc = load(open("data.json"))
        stops = load_stops()
        i = 4
    else:
        i -= 1
    data = []
    for st in stops.values():
        trs = st.load_trips(t, limit=3)
        ok, ok_a = None, None
        for tr in trs:
            a = st.get_trip_stop(tr).arrival.replace(tzinfo=timezone("cet"))
            if ok is not None:
                if ok_a > a > datetime.now().time():
                    ok, ok_a = tr, a
            else:
                ok, ok_a = tr, a

        if ok is None:
            arr = delay = "N/A"
        else:
            delay = ok.delay or 0
            arr = st.get_trip_stop(ok).arrival

        data.append({
            "name": assoc[st.id],
            "time": arr.strftime("%H:%M"),
            "delay": delay,
            "is_delayed": delay != "N/A" and delay != 0
        })

    dump(data,
         open("/var/www/django/raspserver2/static/busses.json", "w+"),
         indent=4)
    print(data)
    sleep(15)
