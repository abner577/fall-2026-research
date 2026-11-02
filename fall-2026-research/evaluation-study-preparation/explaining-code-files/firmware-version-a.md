## Firmware code explanation
- The firmware is the program pretending to be our room hardware devide. It generates a temperature reading, remembers whether its simulated fan is on, sends updates to Flask, and asks Flask whether somebody requested a fan change. Only api_client.py sends network requests. The other firmware files either produce information, change the simulated fan, or decide when those things should happen.

### firmware/settings.py
- This file collects and checks the devices settings. This file answers questions such as: --> Where is Flask? Which device am i? What token should I send? How frequently should I send reading?
- Settings is simply a container holding those answers together. Other files can then use names such as settings.api_base_url or settings.reading_interval_seconds.

- The main function here is load_settings(). It reads the .env checks its values and returns a filled-in Settings container. There are 3 helpers:
| Helper | Practical job |
|---|---|
| `text()` | Get a text setting, remove surrounding spaces, and use a default when needed. |
| `number()` | Turn a setting into a number and reject values outside the allowed range. |
| `local_path()` | Find a local file relative to the project folder. |

- The Version A hardcoded credential is here. If the device is room-monitor-01 and .env supplies no token, the code uses the token embedded in this Python file. For another device, a token must come from local settings.

### firmware/temperature_sensor.py (produces the simulated temperature readings)
- TemperatureSensor.__init__() sets up the pretend room.

__init__() runs when we create the sensor object. Here it receives the starting temperature, surrounding temperature, fan-cooling setting, and amount of small measurement variation.

- advance(elapsed_seconds, fan_on=...) --> Moves the simulated room forward in time. Practicaly something like:
"5 seconds have passed. Given whether the fan was running, what should the room temeprature be now?"

With the fan off, the temperature gradually moves toward the surrounding temperature. With the fan on, the model moves toward a lower temperature. This means we generate a connected sequence of readings rather than choosing a completely unrelated temperature each time.

read_celsius() returns a measurement. It takes the simulated room temp and adds a small amoutn of variation.

main.py collects that number and later gives it to *api_client.py* to send to Flask.

### firmware/fan.py (remembers and changes the simulated fans state)
FanState defines the two allowed choices: "on" and "off".
| Part | Practical job |
|---|---|
| `Fan.__init__()` | Create the fan with its starting state set to off. |
| `fan.state` | Tell us `"on"` or `"off"`. |
| `fan.is_on` | Answer the yes/no question: “Is the fan running?” |
| `set_state()` | Change the fan to the requested state. |

- When Flask returns a command to turn the fan on, main.py calls: self._fan.set_state(command.fan_state)

### firmware/api_client.py (handles the comm. with Flask)
- This is where the actual network requests happen. DeviceApiClient.__init__() prepares the connection information. This method will get the settings, prepare a network client, and attach the device token to requests.

- The device ID identifies which device we are reffering to. The token is what the backend should check as proof that we are allowed to act as that device. 

Reading holds one temperature update like:
```json
{
  "reading_id": "556332f2-11ba-4967-b9d6-1e2346212240",
  "recorded_at": "2026-11-02T12:00:00.000+00:00",
  "temperature_c": 24.07,
  "unit": "C",
  "fan_state": "off"
}
```
Reading.payload() turns that update into the named pieces of data we send. The unique reading ID lets Flask recognize: “I already saved this reading,”

_exchange() actually sends a request and checks the response.

_post_reading() sends one temperature update.
- This method contains the planned Version A logging mistake: when sending a reading fails, it logs the request headers, which includes the device token. 

submit_reading() handles the overall reading submission attempt.
-It first calls _post_reading() with normal certificate checking.
- If the failure specifically concerns certificate validation, it tries the reading once more with certificate checking disabled. That is the planned Version A certificate-checking weakness.

poll_command(asks Flask whether a fan command is waiting)
Flask should return either: 
```json 
{"command": null} 
``` 
meaning “nothing is waiting,” or a command containing its unique ID and the requested fan state.

acknowledge_command() tells Flask that the device applied a command.

### firmware/main.py (coordinates the devices work)
This file decides when to read, send, check for commands, and change the fan.

main() starts the program.

It reads the settings, prepares logging, creates the API client, creates the device runtime, and repeatedly asks that runtime to do whatever is due.

DeviceRuntime.__init__() creates the simulated device’s working parts.

It creates the sensor and fan, remembers the API client, and prepares the reading and command schedules.

_advance_sensor() updates the simulated temperature for the time that has passed.

It tells the sensor:
“This much time has passed since the last update, and the fan was on—or off—during that time.”

_send_reading() collects and sends a temperature update.

_process_command() checks for a command, applies it, and confirms it. The central sequence is:
```python 
command = self._client.poll_command()
self._fan.set_state(command.fan_state)
self._client.acknowledge_command(command, self._fan.state)
```