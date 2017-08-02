key_range = range(0, 256)
pulse = 250

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
    return "P%dS%dL%d" % (a["player"], a["speed"], a["lane_change"])

def to_pulses(b):
    ds = [int(d) for d in b]
    payload = [300, 750]
    previous = 1

    for d in ds:
        if d != previous:
            payload[-1] += pulse
            payload.append(pulse)
        else:
            payload.extend([pulse, pulse])

        previous = d

    return payload

def format(name, pulses):
    return "    name %s\n      %s\n" % (name, " ".join(map(str, pulses)))

keys = []

for n in key_range:
    b = "{0:b}".format(n).zfill(8)
    action = to_action(b)
    key = to_key(action)

    keys.append([key, to_pulses(b)])

conf = """
begin remote
  name carrera
  flags RAW_CODES
  eps 30
  aeps 100
  gap 1
  begin raw_codes
    name SYNC
      800 700 550
%s
  end raw_codes
end remote"""

print(conf % "\n".join([format(n, p) for n, p in keys]))
