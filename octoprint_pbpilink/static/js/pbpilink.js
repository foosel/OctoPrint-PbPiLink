$(function() {
    function PbPiLinkViewModel(parameters) {
        var self = this;

        self.loginState = parameters[0];

        self.powerState = ko.observable();

        self.powerOn = function() {
            self._sendCommand("power_on");
        };

        self.powerOff = function() {
            self._sendCommand("power_off");
        };

        self.powerButtonState = ko.computed(function() {
            if (self.powerState() == "on") {
                return true;
            } else if (self.powerState() == "off") {
                return false;
            }

            return undefined;
        });

        self.powerButtonEnabled = ko.computed(function() {
            return (self.powerState() == "on" || self.powerState() == "off");
        });

        self.togglePower = function() {
            if (!self.powerButtonEnabled()) return;

            if (self.powerState() == "on") {
                self._sendCommand("power_off");
            } else if (self.powerState() == "off") {
                self._sendCommand("power_on");
            }
        };

        self.requestData = function() {
            $.ajax({
                url: API_BASEURL + "plugin/pbpilink",
                type: "GET",
                success: self.fromResponse
            })
        };

        self.fromResponse = function(response) {
            self.powerState(response.power);
        };

        self.onUserLoggedIn = function(user) {
            if (user.admin) {
                self.requestData();
            }
        };

        self._sendCommand = function(command) {
            if (!self.loginState.isAdmin()) return;

            $.ajax({
                url: API_BASEURL + "plugin/pbpilink",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({command: command}),
                contentType: "application/json; charset=UTF-8",
                success: self.fromResponse
            });
        };
    }

    // view model class, parameters for constructor, container to bind to
    ADDITIONAL_VIEWMODELS.push([PbPiLinkViewModel, ["loginStateViewModel"], ["#navbar_plugin_pbpilink"]]);
});
