import lirc
from time import sleep

with lirc.CommandConnection() as conn:
    msg = conn.readline()
    print(msg)

    sleep(0.013)

    resp = lirc.StartRepeatCommand(conn, "carreratower2", "KEY_2").run()
    if resp.success:
        print(resp.data)
    else:
        print(resp.data)
