# Laser Drift

![Laser Drift](/dist/images/logo.jpg?raw=true "Laser Drift")

Laser Drift is a collection of tools that allow you to remotely control your [Carrera Digital 132/124](http://www.carrera-toys.com/en/) race track by emulating the infrared wireless controllers for between one and four players simultaneously.

Laser Drift allows you to control the speed and lane change status of your cars in realtime via a simple language sent over TCP. It will also abstract away the messiness involved in tasks like reverse engineering infrared signals, identifying individual players and syncing with the IR tower.

Each car that is being controlled by a Laser Drift server is uniquely accessible over the network. This means that applications can communicate with Laser Drift without requiring users to be running a server or have any of Laser Drifts dependencies (or even be in the same building!).

This system acts as a low level interface into a Carrera Digital slot car set and is intended to be used to build higher lever applications. See the [frontends](#user-content-frontends) section for some examples of things you can do with this system. 

I have some additional details and a technical explanation of the reverse engineering process available [at my blog](http://bunts.io/).

## How it works

The main Laser Drift system is comprised of two processes:

  - A game loop that maintains each players state, listens for syncing pulses from the IR tower, and encodes each players data into a data packet the control unit expects. The game loop also consumes commands from the TCP server every ~60ms.
  - A TCP server that accepts commands from the outside world and translates them into a data structures the game loop understands. Those data packets are then added to a queue for consumption by the game loop.

A server and game loop can be spun up using the `laserdriftd` program. In this case we are starting a server on localhost:8099 that will send data packets for players 1 and 2:

```
$ ./laserdriftd --port=8099 --p0 --p1 --socket="/usr/local/var/run/lirc/lircd"
```

See the [Installation](#user-content-installation) section for more information.

### Commands

Once you have a server running, you can communicate with it via simple commands.

The following definitions should be acknowledged:

  - **P** is the player number (an int between 0 and 3 inclusive)
  - **S** is the speed to travel (an int between 0 and 15 inclusive)
  - **L** is lane change state (0 = off, 1 = on)

The commands are:

  - **start**: Start responding to IR syncs
  - **stop**: Stop responding to IR syncs (cars will instantly stop but retain their state)
  - **pPsS**: Set player *P* to speed *S*
  - **pPs+**: Increment player *P*'s speed by 1 (if possible)
  - **pPs-**: Decrement player *P*'s speed by 1 (if possible)
  - **pPlL**: Set player *P*'s lane change status to *L*

Note, the infrared packets are physically sent and received by [lirc](http://www.lirc.org/), which must be running in order for Laser Drift to successfully initialize. The full list of software and hardware dependencies is listed in the [What you need](#Whatyouneed) section below.

## Frontends

This repo provides some simple frontend applications that should serve as examples:

  - **accelerator**: A curses GUI for visualizing the acceleration and speed of a player
    - ```./frontends/accelerator [player=1] [host=localhost] [port=8099]```
  - **repl**: Provides a REPL to send raw commands to a Laser Drift server
    - ```./frontends/repl [host=localhost] [port=8099]```
  - **keyboard**: A simple keyboard-based controller (node.js)
    - ```./frontends/keyboard [player=1] [host=localhost] [port=8099]```

**Note**: In Laser Drift itself, players start at zero. So player #1 is 0, etc. The frontend apps (except for ```repl```) start the players at 1.

Other frontends can be built in any programming language that has a networking library (AKA: any language). Some ideas are:

  - Voice-controlled racing
  - Tap Racer: The more you press, the faster you drive
  - Type Racer: You must type out a paragraph and the car travels relative to your words-per-minute
  - Race with hand gestures using a [Leap Motion](https://www.leapmotion.com/)
  - Do a lap every time someone tweets about your favourite topic

## What you need

### Hardware

You will need the following (or equivalent):

  - Carrera Digital 132/124 race track with [Control Unit](http://www.carrera-toys.com/en/products/digital-132/accessories/control-unit-361/). Any modern set will be fine, but even older sets with the "black box" should be fine (although I have not tested that!)
  - [Carrera Wireless Receiver/Tower](http://www.carrera-toys.com/en/products/digital-132/accessories/wireless-empfaengertower-58/).
  - Some [radical](http://www.carrera-toys.com/en/products/digital-132/cars/lamborghini-huracan-lp610-4-3003/years-2015/) [cars](http://www.carrera-toys.com/en/products/go/cars/ferrari-f12-berlinetta-3114/#64055).
  - A USB infrared transceiver. I've successfully tested [USB-UIRT](http://www.usbuirt.com/) and the [irdroid](http://www.irdroid.com/).

Currently, I've only been able to emulate the older infrared controllers with decent accuracy. The more modern 2.4Ghz wireless+ controllers are not supported (yet). Please note, you *do not* actually need any of the old controllers for this system to operate.

### Software

You will need the following:

  - Linux - I've tried Debian and Arch Linux, but any modern distro that supports lirc should be fine
  - [lirc](http://lirc.org/) - latest stable (>= v0.10)
  - Python3

## Installation

I assume you are using Linux. I've successfully tested on Debian 9 and Arch Linux. It's also totally possible that Laser Drift may work in a Windows environment with [WinLirc](http://winlirc.sourceforge.net/) (let me know if you try).

### Lirc

You will need to install [lirc](http://lirc.org/) at `>= v0.10.0`. At the time of writing, this is the bleeding edge version and is not available in any of the respositories of major package managers (although there is an Arch User Repository you can use). I decided to compile it from source.

I used the USB-UIRT transceiver (AKA: send/receive), which is supported natively by lirc with the `usb_uirt_raw` driver. My `lirc_options.conf` file looks a bit like this:

```
[lircd]
nodaemon        = False
driver          = usb_uirt_raw
device          = /dev/ttyUSB0
output          = /usr/local/var/run/lirc/lircd
pidfile         = /usr/local/var/run/lirc/lircd.pid
plugindir       = /usr/local/lib/lirc/plugins
permission      = 666
allow-simulate  = Yes
repeat-max      = 600

[lircmd]
uinput          = False
nodaemon        = False
```

Once installed, you can test that lirc is receiving data by starting a `lircd` process and using the `mode2` binary:

  - Plug in your USB IR transceiver
  - Start lirc: ```$ sudo lircd --nodaemon```
  - Print raw data: ```$ mode2```
  - Point a TV remove at the device and press some buttons (using the Carrera IR controllers will not work unless the IR tower is in range and turned on as they only emit IR if they are receiving syncing blasts from it)
  - You should see a raw stream of pulses and spaces caught by your device and sent to lirc for processing
  - Lirc (latest - maybe from source)

I had some issues in getting the Python bindings for lirc installed on my system. I ended up having to run `setup.py` manually and copy some files around a bit. Hopefully you won't run into this issue, but if you do:

```
$ cd /usr/local/share/lirc/python-pkg/
$ sudo PKG_CONFIG_PATH="/usr/local/lib/pkgconfig/" python3 setup.py install
$ sudo cp config.py /usr/lib/python3.6/site-packages/lirc-0.0.0-py3.6-linux-x86_64.egg/lirc/
```

And now this should run without error:
```
$ python -c "import lirc"
```

### Carrera signals

You will need to let lirc know about all of the signals Carrera IR controllers are capable of sending. To do this, you can copy the pre-generated lircd configuration in this repository to your local lirc path:

```
sudo cp ./dist/carrera.remote.lircd.conf /usr/local/ect/lirc/lircd.conf.d/
```

And then restart lirc.

Now you can test your receiving:

  - Point your IR tower at your IR transceiver
  - ```$ irw```
  - You should see something like ```00000000001 carrera SYNC``` as lirc interprets the input

And sending:

  - ```$ irsend SEND_ONCE carrera SYNC```
  - You should see the lights on your transceiver flash a couple of times

### Laser Drift server

Laser Drift can now be started:

```
$ ./laserdriftd --host=192.168.1.1 --daemon --logfile="/var/log/laserdriftd.log" --port=8080 --p0 --p2  
```

By default, `laserdriftd` will not run as a daemon and will simply log to STDOUT. It can be stopped via ```Ctrl+c```. When running as a daemon, you can kill `laserdriftd` by sending a `SIGINT` signal to the main process: ```$ kill -2 <pid>```

The full options supported by `laserdrift` are:

  - `-d`, `--daemon`: Daemonise the laserdriftd process
  - `--socket=PATH`: Location of the lircd socket [default: /var/run/lirc/lircd]
  - `--host=HOST`: Host name to run TCP server on [default: localhost]
  - `--port=PORT`: TCP port to listen on [default: 8099]
  - `--logfile=PATH`: The path to a file to log output to [default: STDOUT]
  - `--p0`: Activate Player #0
  - `--p1`: Activate Player #1
  - `--p2`: Activate Player #2
  - `--p3`: Activate Player #3

The full set of options can be seen by passing the help flag: ```./laserdriftd --help```.
  
### Recommendations

  - Reduce light pollution. Have the IR tower and USB IR device in a low-light environment (like hidden in a box somewhere)
  - Braking performance should be programmed on your Carrera set to about a 1 or 2. This will prevent the cars from jerking if pulse cycles are missed
  - I programmed my cars at a speed of about 7 - 9. If you program them all the way up then even a mild speed may send them off the rails. That is pretty rad, but it gets annoying.

## Tests

The test suite can be executed via:

```
$ ./tests
```

## FAQ

  - Did you have any help?
    - Yes! The resources available at [SlotBaer](http://www.slotbaer.de) were very important during the reverse engineering process. And Reddit user [byingling](https://www.reddit.com/user/byingling) who helped me with some hardware specifics (and even sent me an old controller!). Also, [David Cristofaro](https://dtcristo.com/) helped me a lot in the first couple of days when I was figuring out how devices like the Carrera race tracks may operate.
  - Why infrared?
    - Because it's much easier to capture and decode signals from devices that emit 38khz IR than devices that operate at 2.4ghz. IR controllers are effectively television remotes. Cheap, off-the-shelf IR transceivers are also much easier to come across. Yes, I suppose I could also have used the wired controllers, but I don't have the depth of knowledge in electrical engineering required to prevent myself from being electrucuted to death.
  - Who did the logo?
    - [Melanie Huang](http://melaniehuang.com/) with the background by [Freepik](http://freepik.com/)
