# Laser Drift

![Laser Drift](/dist/images/logo.jpg?raw=true "Laser Drift")

Laser Drift is a collection of tools that allow you to remotely control your [Carrera Digital 132/124](http://www.carrera-toys.com/en/) race track by emulating the infrared wireless controllers for between one and four players simultaneously.

Laser Drift allows you to control the speed and lane change status of your cars in realtime via a simple language sent over TCP. It will also abstract away the messiness involved in tasks like reverse-engineering infrared signals, identifying individual players and syncing with the IR tower. And because each car is accesible over the network, each car can be controlled separately from different computers.

This system acts as a low level interface into a Carrera Digital slot car set and is intended to be used to build higher lever applications.  See the [frontends](#Frontends) section for some examples of things you can do with this system. 

## How it works

## Frontends

This repo provides two simple frontend applications:

  - **./scripts/repl**: Provides a REPL to send raw commands to a Laser Drift server
  - **./scripts/keyboard**: A simple keyboard-based controller (node.js)

Other frontends can be built in any language that has a networking library (AKA: any language). Some ideas are:

  - Voice-controlled racing
  - Tap racer (the more you press, the faster you drive)
  - Race with hand gestures using a [Leap Motion](https://www.leapmotion.com/)
  - Do a lap every time someone tweets about your favourite topic

## What you need

## Installation

## FAQ
