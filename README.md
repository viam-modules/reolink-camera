# Reolink Camera
Viam module to support Reolink cameras. This module supports PTZ controls via the RunCommand call.
For general image and stream processing, use the viam rtsp or ffmpeg modules. They provide better streaming support. Use this module if you need Reolink-specific control features such at PTZ control.

This module relies on the [Python Reolink API](https://github.com/ReolinkCameraAPI/reolinkapipy) library which wraps Reolink's HTTP API.
Official and unofficial documentation of the Reolink HTTP API can be found [here](https://github.com/mnpg/Reolink_api_documentations).

Model name: `viam:camera:reolink`

## Requirements
- Python 3.12+ is required.
- A Reolink camera that supports the HTTP API.

## Module Configuration

The module can be added to the machine configuration with the following snippet:
```
{
    "type": "registry",
    "name": "viam_reolink",
    "module_id": "viam:reolink",
    "version": "latest"
},
```

## Model Configuration
Prerequisite: Use the Reolink application to configure the username and password, RTSP streaming, and HTTP/HTTPS servers.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| host | string | yes | IP address or hostname of the Reolink camera |
| username | string | yes | Username for camera authentication |
| password | string | yes | Password for camera authentication |
| debug | boolean | no | Enable debug logging. Default is false. |
| https | boolean | no | Use HTTPS instead of HTTP. Default is false. |

Example:
```
{
  "host": "10.1.1.1",
  "username": "admin",
  "password": "admin"
}
```

## Camera Controls
Only select PTZ controls are currently supported for the `RunCommand` call.
Camera commands must be passed to the `RunCommand` via the `command` argument. The `command` argument must be a map where the key is one of the supported commands and the value is a map of arguments for that command. A map will be returned with the key being the command and value being the result of the command. Responses are raw json responses from Reolink's HTTP API.

Multiple commands can be passed at the same time. Commands will be executed in order without waiting for the previous command to complete.

Example Request:
```
{
    "ptz_stop_zooming": {},
    "ptz_move_right": {}
}
```

Example Response:
```
{
  "ptz_stop_zooming": {
    "result": [
      {
        "value": {
          "rspCode": 200
        },
        "code": 0,
        "cmd": "PtzCtrl"
      }
    ]
  },
  "ptz_move_right": [
    {
      "code": 0,
      "cmd": "PtzCtrl",
      "value": {
        "rspCode": 200
      }
    }
  ]
}
```

## Camera Control Commands

| Command | Description | Arguments |
|---------|-------------|-----------|
| ptz_move_right | Move camera right until stopped | {} |
| ptz_move_left | Move camera left until stopped | {} |
| ptz_stop | Stop camera movement | {} |
| ptz_move_up | Move camera up until stopped | {} |
| ptz_move_down | Move camera down until stopped | {} |
| ptz_move_right_up | Move camera right and up until stopped | {} |
| ptz_move_right_down | Move camera right and down until stopped | {} |
| ptz_move_left_up | Move camera left and up until stopped | {} |
| ptz_move_left_down | Move camera left and down until stopped | {} |
| ptz_go_to_preset | Go to preset position | {"id": int} |
| ptz_add_preset | Add current position as preset | {"id": int, "name": string} |
| ptz_remove_preset | Remove preset position | {"id": int, "name": string} |
| ptz_perform_calibration | Perform PTZ calibration | {} |
| ptz_get_presets | Get list of preset positions | {} |
| ptz_check_calibrationstate | Get PTZ state | {} |
| ptz_start_zooming_in | Start zooming in | {} |
| ptz_start_zooming_out | Start zooming out | {} |
| ptz_stop_zooming | Stop zooming | {} |
| ptz_start_focusing_in | Start focusing in | {} |
| ptz_start_focusing_out | Start focusing out | {} |
| ptz_stop_focusing | Stop focusing | {} |
| start_zoom_pos | Start zooming to position | {"position": int} |
| start_focus_pos | Start focusing to position | {"position": int} |
| get_auto_focus | Get auto focus | {} |
| set_auto_focus | Set auto focus | {"disable": bool} |
| get_zoom_focus | Get zoom and focus | {} |

## Supported Platforms
- Linux/arm64 (e.g. Raspberry Pi)
- Linux/amd64
- Darwin/arm64