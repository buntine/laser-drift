key_range = range(0, 256)

def to_action(b):
    action = {"player": 0,
              "speed": 0,
              "lane_change": False}
    ds = [int(d) for d in b]

    action["player"] = ((ds[0] * 2) + ds[1] + (ds[7] * 2))
    action["speed"] = ((ds[2] * (2**3)) + (ds[3] * (2**2)) + (ds[4] * 2) + ds[5])
    action["lane_change"] = ds[6] == 1

    return action

def to_key(a):
    return "p%ds%dl%d" % (a["player"], a["speed"], a["lane_change"])

def to_pulses(b):
    ds = [int(d) for d in b]
    payload = [300, 750]
    previous = 1

    for d in ds:
        if d != previous:
            payload[-1] += 250
            payload.append(250)
        else:
            payload.extend([250, 250])

        previous = d

    return payload

keys = {}

for n in key_range:
    b = "{0:b}".format(n).zfill(8)
    action = to_action(b)
    key = to_key(action)

    keys[key] = to_pulses(b)
