Feature: Validating the connectivity of all application components

  Scenario Outline: Sending a MQTT message results in the right API request response
    Given the MQTT messages <message> are sent to the <topic>
    When querying the API with a <method> request
    Then then the response is: <response>

    Examples: Messages
      | message | topic | method | response |
      | [{"timestamp": 10,"temperature": 21,"humidity": 50}] | "iot/test/data" | GET  | {"data": {"humidity": [50.0], "temperature": [21.0], "device": ["test"], "timestamp": [10]}} |
      | [{"timestamp": 10,"temperature": 21,"humidity": 50}] | "iot/test/data" | POST  | {"data": {"humidity": [50.0], "temperature": [21.0], "device": ["test"], "timestamp": [10]}} |
      | [{}] | "iot/test/data" | GET  | {"data": {}} |
      | [{}] | "iot/test/data" | POST | {"data": {}} |