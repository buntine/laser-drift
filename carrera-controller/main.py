import lirc
from time import sleep

with lirc.CommandConnection(socket_path="/usr/local/var/run/lirc/lircd") as conn:
    while True:
        msg = conn.readline()

        sleep(0.013)

        resp = lirc.SendCommand(conn, "carreratower2", "K").run()
        print(resp.data)
