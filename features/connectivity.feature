Feature: Validating the connectivity of all application components

  Scenario Outline: Sending a MQTT message results in the right API request response
    Given the MQTT messages <message> are sent to the IoT Core
    When querying the API with a <method> request
    Then then the response is: <response>

    Examples: Messages
      | message | method | response |
      | [{"device": "test","timestamp": 10,"temperature": 21,"humidity": 50}] | GET  | {"data": {"humidity": [50.0], "temperature": [21.0], "device": ["test"], "timestamp": [10]}} |
      | [{"device": "test","timestamp": 10,"temperature": 21,"humidity": 50}] | GET  | {"data": {"humidity": [50.0], "temperature": [21.0], "device": ["test"], "timestamp": [10]}} |
      | [{}] | GET  | {"data": {}} |
      | [{}] | POST | {"data": {}} |