# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import threading
from octoprint.events import Events

class PbPiLinkPlugin(octoprint.plugin.TemplatePlugin,
                     octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.StartupPlugin,
                     octoprint.plugin.ShutdownPlugin,
                     octoprint.plugin.SimpleApiPlugin,
                     octoprint.plugin.AssetPlugin,
                     octoprint.plugin.EventHandlerPlugin):

	EVENTS_NOCLIENTS = (Events.CLIENT_OPENED, Events.CLIENT_CLOSED, Events.PRINT_DONE)
	EVENTS_DISCONNECT = (Events.DISCONNECTED,)

	def __init__(self):
		self._connection_data = None
		self._clients = 0
		self._client_poweroff_timer = None

	##~~ Settings

	def get_settings_defaults(self):
		return dict(
			power_on_startup=True,
			power_off_shutdown=True,

			power_on_clients=False,
			power_off_noclients=False,
			noclients_countdown=60,

			power_on_connect=True,
			power_off_disconnect=True
		)

	def initialize(self):
		if self._settings.get_boolean(["power_on_connect"]):
			original_connect = self._printer.connect
			def wrapped_connect(*args, **kwargs):
				self._poweron(connect=False)
				original_connect(*args, **kwargs)
			self._printer.connect = wrapped_connect

	##~~ Softwareupdate hook

	def get_update_information(self):
		return dict(
			pbpilink=dict(
				displayName="Printrbot Pi Link Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="foosel",
				repo="OctoPrint-PbPiLink",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/foosel/OctoPrint-PbPiLink/archive/{target_version}.zip"
			)
		)

	##~~ Assets

	def get_assets(self):
		return dict(
			js=["js/pbpilink.js"]
		)

	##~~ Templates

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False),
		]

	##~~ Startup

	def on_startup(self, host, port):
		# setup GPIO
		self._setup_gpio()

		# setup serial port if necessary
		import fnmatch
		additional_ports = self._settings.global_get(["serial", "additionalPorts"])
		if not any(map(lambda x: fnmatch.fnmatch("/dev/ttyAMA0", x), additional_ports)):
			self._logger.info("Raspberry Pi Serial Port not yet in additional ports, adding it")
			additional_ports.append("/dev/ttyAMA*")
			self._settings.global_set(["serial", "additionalPorts"], additional_ports)
			self._settings.save()

		# power on if configured as such
		if self._settings.get_boolean(["power_on_startup"]):
			self._set_pb_power(True)

	##~~ Shutdown

	def on_shutdown(self):
		if self._settings.get_boolean(["power_off_shutdown"]):
			self._set_pb_power(False)

	##~~ SimpleAPI

	def on_api_get(self, request):
		from flask import jsonify

		return jsonify(**self._status())

	def get_api_commands(self):
		return dict(
			power_on=[],
			power_off=[]
		)

	def on_api_command(self, command, data):
		from flask import abort, jsonify
		from octoprint.server import admin_permission

		if not admin_permission.can():
			abort(403)

		if command == "power_on":
			self._poweron()

		elif command == "power_off":
			self._poweroff()

		return jsonify(**self._status())

	def _status(self):
		return dict(power=self._get_pb_power())

	##~~ EventHandlerPlugin

	def on_event(self, event, payload):
		if not event in self.__class__.EVENTS_NOCLIENTS and not event in self.__class__.EVENTS_DISCONNECT:
			return

		if event in self.__class__.EVENTS_NOCLIENTS:
			if event == Events.CLIENT_OPENED:
				if self._clients == 0 and self._settings.get_boolean(["power_on_clients"]):
					self._poweron()
				self._clients += 1

			elif event == Events.CLIENT_CLOSED:
				self._clients -= 1

			if self._clients <= 0:
				self._clients = 0
				self._client_poweroff_timer = threading.Timer(self._settings.get_float(["noclients_countdown"]), self._noclients_poweroff)
				self._client_poweroff_timer.start()
			elif self._client_poweroff_timer is not None:
				self._client_poweroff_timer.cancel()
				self._client_poweroff_timer = None

		elif event in self.__class__.EVENTS_DISCONNECT:
			self._poweroff(disconnect=False)

	##~~ Helpers

	def _poweron(self, connect=True):
		self._set_pb_power(True)
		if connect and self._connection_data is not None:
			state, port, baudrate, printer_profile = self._connection_data
			if state != "Operational":
				return
			self._printer.connect(port=port, baudrate=baudrate, printer_profile=printer_profile)

	def _poweroff(self, disconnect=True):
		self._connection_data = self._printer.get_current_connection()
		if disconnect:
			self._printer.disconnect()
		self._set_pb_power(False)

	def _noclients_poweroff(self):
		if self._printer.is_printing():
			return

		if not self._settings.get_boolean(["power_off_noclients"]):
			return

		self._logger.info("Powering off after not seeing any clients after {}s".format(self._settings.get_float(["noclients_countdown"])))
		self._poweroff()

	def _set_pb_power(self, enable):
		import sarge
		command = ["gpio", "-g", "write", "2"]
		if enable:
			self._logger.info("Enabling power supply for Printrboard")
			command.append("0")
		else:
			self._logger.info("Disabling power supply for Printrboard")
			command.append("1")

		try:
			sarge.run(command)
		except:
			self._logger.exception("{} failed".format(" ".join(command)))

	def _get_pb_power(self):
		import sarge
		command = ["gpio", "-g", "read", "2"]

		try:
			output = sarge.get_stdout(command)
		except:
			self._logger.exception("{} failed".format(" ".join(command)))
		else:
			if output.strip() == "1":
				return "off"
			elif output.strip() == "0":
				return "on"

		return "unknown"

	def _setup_gpio(self):
		import sarge
		command = ["gpio", "-g", "mode", "2", "out"]

		try:
			sarge.run(command)
		except:
			self._logger.exception("{} failed".format(" ".join(command)))

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PbPiLinkPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

