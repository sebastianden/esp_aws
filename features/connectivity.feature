Feature: Validating the connectivity of all application components

  Scenario Outline: Sending a MQTT message results in the right API request response
    Given the MQTT messages <message> are sent to the IoT Core
    When querying the API with a <method> request
    Then then the response is: <response>

    Examples: Messages
      | message        | method | response |
      | [{"measurement":"temperature","value":21,"timestamp":10,"uom":"°C"},{"measurement":"humidity","value":50,"timestamp":10,"uom":"%"}] | GET  | {"data": [[10, 21.0, 50.0]]} |
      | [{"measurement":"temperature","value":21,"timestamp":10,"uom":"°C"},{"measurement":"humidity","value":50,"timestamp":10,"uom":"%"}] | GET  | {"data": [[10, 21.0, 50.0]]} |
      | {} | GET  | {"data": []} |
      | {} | POST | {"data": []} |