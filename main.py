from tnbus import TNBus, API, By, Cond
from datetime import datetime, timedelta
from pytz import timezone
from json import dump, load
from json.decoder import JSONDecodeError
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
        for _ in range(10):
            try:
                trs = st.load_trips(t, limit=3)
                break
            except JSONDecodeError:
                pass
        ok, ok_a = None, None
        for tr in trs:
            a = st.get_trip_stop(tr).arrival.replace(tzinfo=timezone("cet"))
            if ok is not None:
                if ok_a > a > datetime.now().time():
                    ok, ok_a = tr, a
            else:
                ok, ok_a = tr, a

        if ok is None:
            arr = "N/A"
            delay = 0
        else:
            delay = ok.delay or 0
            arr = st.get_trip_stop(ok).arrival
            if 0 <= arr.hour <= 4:
                arr = datetime.combine(datetime.today() + timedelta(days=1), arr)
            else:
                arr = datetime.combine(datetime.today(), arr)

        data.append({
            "name": assoc[st.id],
            "time": arr.timestamp() if isinstance(arr, datetime) else arr,
            "delay": delay,
            "status": (-1 if arr == "N/A" else (0 if delay == 0 else (1 if delay > 0 else 2)))
        })

    dump(data,
         open("busses.json", "w+"),
         indent=4)
    print(data)
    sleep(15)
