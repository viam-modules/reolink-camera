import asyncio
import logging
import time
from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple)

from typing_extensions import Self
from viam.components.camera import *
from viam.media.video import NamedImage, ViamImage, CameraMimeType
from viam.media.utils.pil import pil_to_viam_image
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName, ResponseMetadata
from viam.proto.component.camera import GetPropertiesResponse
from viam.components.component_base import ValueTypes
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from logging import getLogger
from reolinkapi import Camera as ReolinkCamera
from viam.utils import struct_to_dict
from PIL import Image
from viam.resource.registry import Registry, ResourceCreatorRegistration


class Reolink(Camera, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("viam", "camera"), "reolink"
    )
    LOGGER: Final[logging.Logger] = logging.getLogger(__name__)
    
    camera: ReolinkCamera = None
    debug: bool = False
    
    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        my_class = cls(config.name)
        my_class.reconfigure(config, dependencies)
        return my_class

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        attributes = struct_to_dict(config.attributes)
        if 'host' not in attributes or 'username' not in attributes or 'password' not in attributes:
            raise ValueError("Missing required fields in config: 'host', 'username', and 'password' are required.")
        
        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        if self.camera is not None:
            self.camera.logout()
            self.camera = None
        
        attributes = struct_to_dict(config.attributes)
        self.debug = attributes['debug']
        
        try:
            self.camera = ReolinkCamera(attributes['host'], 
                                      attributes['username'], 
                                      attributes['password'], 
                                      attributes.get('https', False))
            # Test the connection
            self.camera.login()
        except Exception as e:
            self.LOGGER.error(f"Failed to connect to Reolink camera: {str(e)}")
            raise RuntimeError(f"Failed to initialize Reolink camera: {str(e)}")
        
        return self

    async def get_image(
        self,
        mime_type: str = "",
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> ViamImage:
        # TODO: check if camera is connected? not sure if this is needed of the library handles it
        
        start_time = time.time()
        image_data: Image.Image = self.camera.get_snap()
        
        if self.debug:
            self.LOGGER.warning(f"get_snap() took {time.time() - start_time:.2f} seconds")
            self.LOGGER.warning(f"Received image mime type: {image_data.format}, mode: {image_data.mode}, data size: {len(image_data.tobytes())} bytes")
            
        viam_image = pil_to_viam_image(image_data, CameraMimeType.JPEG)

        return viam_image

    async def get_images(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Tuple[List[NamedImage], ResponseMetadata]:
        image = await self.get_image()
        return [NamedImage("main", image.data, image.mime_type)], ResponseMetadata()

    # Exposes select commands from Reolink API as documented at https://drive.google.com/file/d/1KvPbjRVqsgCEzJsUS--zEyxw6cP-pkSI/view?usp=sharing.
    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:

        result = {}

        for cmd_name, cmd_args in command.items():
            self.logger.info(f"command: {cmd_name}, args: {cmd_args}")
            result[cmd_name] = {}
            
            parsed_args = {}
            if isinstance(cmd_args, Mapping):
                parsed_args = cmd_args
            else:
                self.logger.warning(f"received non-map do_command arguments for {cmd_name}, skipping this command.")
                result[cmd_name]["error"] = "Non-map argument provided. Ignored."
                continue;

            # TODO: add more commands and arguments for commands that take them.
            match cmd_name:
                # Movement. From https://github.com/ReolinkCameraAPI/reolinkapipy/blob/master/reolinkapi/mixins/ptz.py
                case "ptz_move_right":
                    ret = self.camera.move_right()
                    result[cmd_name] = ret
                case "ptz_move_left":
                    ret = self.camera.move_left()
                    result[cmd_name] = ret
                case "ptz_stop":
                    ret = self.camera.stop_ptz()
                    result[cmd_name] = ret
                case "ptz_move_up":
                    ret = self.camera.move_up()
                    result[cmd_name] = ret
                case "ptz_move_down":
                    ret = self.camera.move_down()
                    result[cmd_name] = ret
                case "ptz_move_right_up":
                    ret = self.camera.move_right_up()
                    result[cmd_name] = ret
                case "ptz_move_right_down":
                    ret = self.camera.move_right_down()
                    result[cmd_name] = ret
                case "ptz_move_left_up":
                    ret = self.camera.move_left_up()
                    result[cmd_name] = ret
                case "ptz_move_left_down":
                    ret = self.camera.move_left_down()
                    result[cmd_name] = ret
                case "ptz_go_to_preset":
                    ret = self.camera.go_to_preset(index=int(parsed_args["id"]))
                    time.sleep(4)
                    result[cmd_name] = ret
                case "ptz_add_preset":
                    ret = self.camera.add_preset(preset=int(parsed_args["id"]), name=int(parsed_args["name"]))
                    result[cmd_name] = ret
                case "ptz_remove_preset":
                    ret = self.camera.remove_preset(preset=int(parsed_args["id"]), name=int(parsed_args["name"]))
                    result[cmd_name] = ret
                case "ptz_perform_calibration":
                    ret = self.camera.perform_calibration()
                    result[cmd_name] = ret
                case "ptz_get_presets":
                    ret = self.camera.get_ptz_presets()
                    result[cmd_name] = ret
                case "ptz_check_calibrationstate":
                    ret = self.camera.get_ptz_check_state()
                    result[cmd_name] = ret

                # Zoom and Focus. From https://github.com/ReolinkCameraAPI/reolinkapipy/blob/master/reolinkapi/mixins/zoom.py
                case "ptz_start_zooming_in":
                    ret = self.camera.start_zooming_in()
                    result[cmd_name]["result"] = ret
                case "ptz_start_zooming_out":
                    ret = self.camera.start_zooming_out()
                    result[cmd_name]["result"] = ret
                case "ptz_stop_zooming":
                    ret = self.camera.stop_zooming()
                    result[cmd_name]["result"] = ret
                case "ptz_start_focusing_in":
                    ret = self.camera.start_focusing_in()
                    result[cmd_name]["result"] = ret
                case "ptz_start_focusing_out":
                    ret = self.camera.start_focusing_out()
                    result[cmd_name]["result"] = ret
                case "ptz_stop_focusing":
                    ret = self.camera.stop_focusing()
                    result[cmd_name]["result"] = ret
                case "get_zoom_focus":
                    ret = self.camera.get_zoom_focus()
                    result[cmd_name]["result"] = ret
                case "start_zoom_pos":
                    ret = self.camera.start_zoom_pos(position=int(parsed_args["position"]))
                    result[cmd_name]["result"] = ret
                case "start_focus_pos":
                    ret = self.camera.start_focus_pos(position=int(parsed_args["position"]))
                    result[cmd_name]["result"] = ret
                case "get_auto_focus":
                    ret = self.camera.get_auto_focus()
                    result[cmd_name]["result"] = ret
                case "set_auto_focus":
                    ret = self.camera.set_auto_focus(disable=bool(parsed_args["disable"]))
                    result[cmd_name]["result"] = ret
        

                case _:
                    result[cmd_name]["error"] = f"Unknown command: {command}"

        return result

    async def get_point_cloud(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Tuple[bytes, str]:
        raise NotImplementedError()

    async def get_properties(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Camera.Properties:
        raise NotImplementedError()

if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())

