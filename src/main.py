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
        ModelFamily("stevebriskin", "reolink-camera"), "reolink"
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
            
        start_time = time.time()
        viam_image = pil_to_viam_image(image_data, CameraMimeType.JPEG)
        
        if self.debug:
            self.LOGGER.warning(f"pil_to_viam_image() took {time.time() - start_time:.2f} seconds")
            self.LOGGER.warning(f"viam_image size: {len(viam_image.data)} bytes")


        if self.debug:
            # Save both original PIL image and converted Viam image with timestamps
            timestamp = int(time.time())
            
            # Save PIL image
            pil_path = f"/tmp/reolink_pil_{timestamp}.{image_data.format.lower()}"
            image_data.save(pil_path)
            
            # Save Viam image 
            viam_path = f"/tmp/reolink_viam_{timestamp}.jpg"
            with open(viam_path, "wb") as f:
                f.write(viam_image.data)
            
        return viam_image

    async def get_images(
        self, *, timeout: Optional[float] = None, **kwargs
    ) -> Tuple[List[NamedImage], ResponseMetadata]:
        image = await self.get_image()
        return [NamedImage("main", image.data, image.mime_type)], ResponseMetadata()

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

