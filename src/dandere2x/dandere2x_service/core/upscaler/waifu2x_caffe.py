"""
    This file is part of the Dandere2x project.
    Dandere2x is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    Dandere2x is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Dandere2x.  If not, see <https://www.gnu.org/licenses/>.
""""""
========= Copyright aka_katto 2018, All rights reserved. ============
Original Author: aka_katto 
Purpose: Caffe implementation of abstract_upscaler
 
====================================================================="""
import copy
import os
import subprocess
from threading import Thread

from dandere2x.dandere2xlib.utils.dandere2x_utils import get_operating_system
from dandere2x.dandere2xlib.utils.yaml_utils import load_executable_paths_yaml, get_options_from_section
from ..upscaler.abstract_upscaler import AbstractUpscaler
from dandere2x.dandere2x_service.dandere2x_service_context import Dandere2xServiceContext
from dandere2x.dandere2x_service.dandere2x_service_controller import Dandere2xController

class Waifu2xCaffe(AbstractUpscaler, Thread):

    def __init__(self, context: Dandere2xServiceContext, controller: Dandere2xController):
        # implementation specific
        self.active_waifu2x_subprocess = None
        self.waifu2x_caffe_path = load_executable_paths_yaml()['waifu2x_caffe']

        assert get_operating_system() != "win32" or os.path.exists(self.waifu2x_caffe_path), \
            "%s does not exist!" % self.waifu2x_caffe_path

        super().__init__(context, controller)
        Thread.__init__(self, name="Waifu2x Thread")

    # override
    def repeated_call(self) -> None:
        exec_command = copy.copy(self.upscale_command)
        console_output = open(self.context.console_output_dir + "caffe_upscale_frames.txt", "w")

        # replace the exec command with the files we're concerned with
        for x in range(len(exec_command)):
            if exec_command[x] == "[input_file]":
                exec_command[x] = self.context.residual_images_dir

            if exec_command[x] == "[output_file]":
                exec_command[x] = self.context.residual_upscaled_dir

        console_output.write(str(exec_command))
        self.active_waifu2x_subprocess = subprocess.Popen(exec_command, shell=False, stderr=console_output,
                                                          stdout=console_output)
        self.active_waifu2x_subprocess.wait()

    # override
    def upscale_file(self, input_image: str, output_image: str) -> None:

        exec_command = copy.copy(self.upscale_command)
        console_output = open(self.context.console_output_dir + "caffe_upscale_frames.txt", "w")

        # replace the exec command with the files we're concerned with
        for x in range(len(exec_command)):
            if exec_command[x] == "[input_file]":
                exec_command[x] = input_image

            if exec_command[x] == "[output_file]":
                exec_command[x] = output_image

        console_output.write(str(exec_command))
        self.active_waifu2x_subprocess = subprocess.Popen(exec_command, shell=False, stderr=console_output,
                                                          stdout=console_output)
        self.active_waifu2x_subprocess.wait()

    # override
    def _construct_upscale_command(self) -> list:
        upscale_command = [self.waifu2x_caffe_path,
                           "-i", "[input_file]",
                           "-n", str(self.context.service_request.denoise_level),
                           "-s", str(self.context.service_request.scale_factor)]

        optional_paramaters = get_options_from_section(
            self.context.service_request.output_options["waifu2x_caffe"]["output_options"])

        # add optional paramaters to upscaling command.
        for element in optional_paramaters:
            upscale_command.append(element)

        upscale_command.extend(["-o", "[output_file]"])
        return upscale_command
