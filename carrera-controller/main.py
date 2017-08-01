import lirc
from time import sleep

i = 0
with lirc.CommandConnection(socket_path="/usr/local/var/run/lirc/lircd") as conn:
    while True:
        msg = conn.readline()
        print(i)
        i+=1

        sleep(0.010)

        resp = lirc.SendCommand(conn, "carreratower2", ["AA"]).run()
        print(resp.data)

        sleep(0.010)

        resp = lirc.SendCommand(conn, "carreratower2", "L").run()
        print(resp.data)
