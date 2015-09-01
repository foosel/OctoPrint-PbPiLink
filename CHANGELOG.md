# Printrboard Pi Link Plugin Changelog

## 0.1.2 (unreleased)

### Improvements

  * Option to power off when not printing and no clients connected to the UI
  * Option to power back on when a client reconnects to the UI
  * Option to automatically power on before connecting
  * Option to automatically power off after disconnecting
  * Settings dialog
  * GPIO initialization on startup (no entry in `/etc/init.d/octoprint` or
    `/etc/rc.local` needed for this anymore thanks to wiringPi being setuid
    root by default)

## 0.1.1 (2015-07-29)

### Improvements

  * Confirmation dialog when disconnecting power while printing.
  * Re-establish communication with the printer after re-powering it.

## 0.1.0 (2015-07-19)

Initial release
