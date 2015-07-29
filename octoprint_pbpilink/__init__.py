# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin

class PbPiLinkPlugin(octoprint.plugin.TemplatePlugin,
                     octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.StartupPlugin,
                     octoprint.plugin.ShutdownPlugin,
                     octoprint.plugin.SimpleApiPlugin,
                     octoprint.plugin.AssetPlugin):

	##~~ Settings

	def get_settings_defaults(self):
		return dict(
			power_on_startup=True,
			power_off_shutdown=True
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		return dict(
			requestspinner=dict(
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

	##~~ Startup

	def on_startup(self, host, port):
		import fnmatch
		additional_ports = self._settings.global_get(["serial", "additionalPorts"])
		if not any(map(lambda x: fnmatch.fnmatch("/dev/ttyAMA0", x), additional_ports)):
			self._logger.info("Raspberry Pi Serial Port not yet in additional ports, adding it")
			additional_ports.append("/dev/ttyAMA*")
			self._settings.global_set(["serial", "additionalPorts"], additional_ports)
			self._settings.save()

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
			self._set_pb_power(True)
		elif command == "power_off":
			self._set_pb_power(False)

		return jsonify(**self._status())

	def _status(self):
		return dict(power=self._get_pb_power())

	##~~ Helpers

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

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PbPiLinkPlugin()

	# global __plugin_hooks__
	# __plugin_hooks__ = {
	#    "some.octoprint.hook": __plugin_implementation__.some_hook_handler
	# }

