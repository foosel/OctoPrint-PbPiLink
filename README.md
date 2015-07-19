# Printrboard Pi Link Plugin

---

**PRERELEASE:** Provided "as is" for now. If you do not have a Printrboard Pi Link board, this plugin is useless for you.

---

Addon plugin for the [Printrboard Pi Link board](https://github.com/j-laird/Printrboard-Pi-Link).

Will add a toggle button for the Printrboard 12V power supply to the navigation bar and also include the
Raspberry Pi serial port in the "Additional Ports" section of usable serial ports if it's not already
included.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/foosel/OctoPrint-PbPiLink/archive/master.zip

You also need [WiringPi]() set up and add

    gpio -g export 2 out
    gpio -g mode 2 out

to `/etc/rc.local` or `/etc/init.d/octoprint`, otherwise OctoPrint won't be able to manipulate
the power switching GPIO pin.

Please refer to the [README of the Printrboard Pi Link repository](https://github.com/j-laird/Printrboard-Pi-Link#printrboard-pi-link).

## Configuration

``` yaml
plugins:
  pbpilink:
    # whether to power on the Printrboard on startup
    # of OctoPrint
    power_on_startup: true

    # whether to power off the Printrboard on shutdown
    # of OctoPrint
    power_off_shutdown: true
```

## Future Improvements

  * Make configuration settings configurable
  * Automatically cut power on disconnect/error?
  * Serial port wrapper with custom "PbPiLink" name and auto connect
  * tbc
