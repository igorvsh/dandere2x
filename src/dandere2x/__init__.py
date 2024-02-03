import os
from threading import Thread
from typing import Type

from dandere2x.dandere2x_logger import set_dandere2x_logger
from dandere2x.dandere2x_service.service_types.dandere2x_service_interface import Dandere2xServiceInterface
from dandere2x.dandere2x_service_request import Dandere2xServiceRequest, ProcessingType


class Dandere2x(Thread):
    """
    Accepts a "root"-level request and will handle all the logic in spawning the child-dandere2x sessions.

    This folder is a very generic wrapper in that it's mostly there to handle superficial logic in how dandere2x
    should go about processing a service request.
    """

    def __init__(self, service_request: Dandere2xServiceRequest):
        super().__init__()
        self._service_request = service_request

        # discover which dandere2x-process the user wants to use.
        anonymous_dandere2x_service = self._determine_process_type(self._service_request)

        # start a child-thread of the selected process.
        self._root_service_thread = anonymous_dandere2x_service(service_request=self._service_request)

    @staticmethod
    def _determine_process_type(request) -> Type[Dandere2xServiceInterface]:
        """
        A wrapper to determine what the root service should be - i.e a logical set of operations to determine what
        the user was intending for dandere2x to return given the initial service request.

        :param request: The root service request.
        :return: A Dandere2xInterface-inherited subclass.
        """

        if os.path.isdir(request.input_file):
            from dandere2x.dandere2x_service.service_types.folder_service import FolderService
            return FolderService

        if request.input_file.endswith("gif"):
            from dandere2x.dandere2x_service.service_types.gif_service import GifService
            return GifService

        if request.processing_type == ProcessingType.MULTI_PROCESS:
            from dandere2x.dandere2x_service.service_types.multiprocess_service import MultiProcessService
            return MultiProcessService

        if request.processing_type == ProcessingType.SINGLE_PROCESS:
            from dandere2x.dandere2x_service.service_types.singleprocess_service import SingleProcessService
            return SingleProcessService

        raise Exception("Could not find selected upscaler type. ")

    def run(self) -> None:
        self._root_service_thread.run()
