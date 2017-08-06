# Laser Drift

![Laser Drift](/dist/images/logo.jpg?raw=true "Laser Drift")

Laser Drift is a collection of tools that allow you to remotely control your [Carrera Digital 132/124](http://www.carrera-toys.com/en/) race track by emulating the infrared wireless controllers for between one and four players simultaneously.

Laser Drift allows you to control the speed and lane change status of your cars in realtime via a simple language sent over TCP. It will also abstract away the messiness involved in tasks like reverse-engineering infrared signals, identifying individual players and syncing with the IR tower. And because each car is accessible over the network, they can be controlled separately from different computers.

This system acts as a low level interface into a Carrera Digital slot car set and is intended to be used to build higher lever applications.  See the [frontends](#Frontends) section for some examples of things you can do with this system. 

## How it works

The main Laser Drift system is comprised of two processes:

  - A game loop that maintains each players state, listens for syncing pulses from the IR tower, and encodes each players data into a data packet the control unit expects. The game loop also consumes commands from the TCP server every ~60ms.
  - A TCP server that accepts commands from the outside world and translates them into a data structures the game loop understands. Those data packets are then added to a queue for consumption by the game loop.

A server and game loop can be spun up using the `race` program. In this case we are starting a server on port 8099 that will send data packets for players 1 and 2:

```
./race --host=127.0.0.1 --port=8099 --p1 --p2 --socket="/usr/local/var/run/lirc/lircd"
```

A full set of options can be seen by passing the help flag: ```./race --help```.

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
  - **pPlL**: Set player *P*'s lane change status to *L*

Note, the infrared packets are physically sent and received by [lirc](http://www.lirc.org/), which must be running in order for Laser Drift to successfully initialize. The full list of software and hardware dependencies is listed in the [What you need](#Whatyouneed) section below.

## Frontends

This repo provides two simple frontend applications:

  - **repl**: Provides a REPL to send raw commands to a Laser Drift server
    ```./scripts/repl [host=localhost] [port=8099]```
  - **keyboard**: A simple keyboard-based controller (node.js)
    ```./scripts/keyboard [player] [host=localhost] [port=8099]```

Other frontends can be built in any programming language that has a networking library (AKA: any language). Some ideas are:

  - Voice-controlled racing
  - Tap racer (the more you press, the faster you drive)
  - Race with hand gestures using a [Leap Motion](https://www.leapmotion.com/)
  - Do a lap every time someone tweets about your favourite topic

## What you need

## Installation

## FAQ
