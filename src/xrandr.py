#!/usr/bin/env python3
import subprocess
import shlex
import re
from src.config import Node


class XRandr:
    def __init__(self):
        self.list_active_monitors = ""

    def _update_list_active_monitors(self) -> None:
        command = "xrandr --listactivemonitors"
        output = subprocess.run(
            shlex.split(command), capture_output=True, encoding="utf-8"
        )
        self.list_active_monitors = output.stdout.split("\n")

    def _get_primary_monitor_raw(self) -> str:
        for monitor in self.list_active_monitors:
            if "+*" in monitor:
                return monitor
        return ""

    #  def _get_primary_monitor_res(self) -> str:
    #      monitor_info = self._get_primary_monitor_raw()

    def _get_monitor_info_by_name(self, name) -> str:
        for monitor_info in self.list_active_monitors:
            if name in monitor_info:
                return monitor_info
        return ""

    # Returns the resolution of the monitor
    def _get_monitor_res(self, name) -> str:
        loc_res_info = 2
        for monitor_info in self.list_active_monitors:
            if name in monitor_info:
                return monitor_info.split()[loc_res_info]
        return ""

    # """Recursively split the primary monitor based on the provided node configuration."""
    def split_primary_monitor(
        self,
        node: Node,
        x_offset: int = 0,
        y_offset: int = 0,
        width_px: int = None,
        height_px: int = None,
        monitor_physical_width: int = None,
        monitor_physical_height: int = None,
    ) -> bool:
        # Initial setup, only for the root node
        if width_px is None or height_px is None:
            self._update_list_active_monitors()
            primary_monitor_info = self._get_primary_monitor_raw()
            try:
                primary_monitor_name = self._get_monitor_name(primary_monitor_info)
            except IndexError:
                print("Error: If you are in split mode restore and split again")
                return False

            primary_monitor_res = self._get_monitor_res(primary_monitor_info)
            width_px = self._get_monitor_width_px(primary_monitor_res)
            height_px = self._get_monitor_height_px(primary_monitor_res)
            monitor_physical_width = self._get_monitor_physical_width(
                primary_monitor_res
            )
            monitor_physical_height = self._get_monitor_physical_height(
                primary_monitor_res
            )
            x_offset = self._get_monitor_x_offset(primary_monitor_res)
            y_offset = self._get_monitor_y_offset(primary_monitor_res)
            monitor_name = primary_monitor_name
        else:
            monitor_name = "none"

        current_x_offset = x_offset
        current_y_offset = y_offset

        if node.type == "vertical":
            for index, child in enumerate(node.nodes):
                new_width_px = int(width_px * child.width / 100)
                new_monitor_name = f"V-{monitor_name}-{child.width}"
                # Generate the command directly using pixel values for width and height
                if index != 0:
                    monitor_name = "none"

                # Recursively split if the node is not a window
                if child.type != "window":
                    self.split_primary_monitor(
                        child,
                        current_x_offset,
                        current_y_offset,
                        new_width_px,
                        height_px,
                        monitor_physical_width,
                        monitor_physical_height,
                    )
                else:
                    command = (
                        f"xrandr --setmonitor {new_monitor_name} "
                        f"{new_width_px}/{monitor_physical_width}"
                        "x"
                        f"{height_px}/{monitor_physical_height}"
                        "+"
                        f"{current_x_offset}+{current_y_offset} {monitor_name}"
                    )
                    # print(command)
                    subprocess.run(
                        shlex.split(command), capture_output=True, encoding="utf-8"
                    )
                current_x_offset += new_width_px

        elif node.type == "horizontal":
            for index, child in enumerate(node.nodes):
                new_height_px = int(height_px * child.width / 100)
                new_monitor_name = f"H-{monitor_name}-{child.width}"
                # Generate the command directly using pixel values for width and height
                if index != 0:
                    monitor_name = "none"

                # Recursively split if the node is not a window
                if child.type != "window":
                    self.split_primary_monitor(
                        child,
                        current_x_offset,
                        current_y_offset,
                        width_px,
                        new_height_px,
                        monitor_physical_width,
                        monitor_physical_height,
                    )
                else:
                    command = (
                        f"xrandr --setmonitor {new_monitor_name} "
                        f"{width_px}/{monitor_physical_width}"
                        "x"
                        f"{new_height_px}/{monitor_physical_height}"
                        "+"
                        f"{current_x_offset}+{current_y_offset} {monitor_name}"
                    )
                    # print(command)
                    subprocess.run(
                        shlex.split(command), capture_output=True, encoding="utf-8"
                    )
                current_y_offset += new_height_px

        return True

    def restore_primary_monitor(self) -> bool:
        self._update_list_active_monitors()
        for vmonitor in self._get_virtual_monitors():
            monitor_name = self._get_monitor_name(vmonitor)
            command = f"xrandr --delmonitor {monitor_name}"
            subprocess.run(shlex.split(command), capture_output=True, encoding="utf-8")
        return True

    def _get_virtual_monitors(self):
        vmonitor_list = []
        for monitor_info in self.list_active_monitors:
            if " V-" in monitor_info:
                vmonitor_list.append(monitor_info)
            elif " H-" in monitor_info:
                vmonitor_list.append(monitor_info)
        return vmonitor_list

    def _get_monitor_name(self, monitor_info: str) -> str:
        return re.sub(r"^\W+", "", monitor_info.split()[1])

    def _get_monitor_width_px(self, monitor_res: str) -> int:
        # Split the string at 'x' to separate the resolution parts
        resolution_part = monitor_res.split("x")

        print("resolution_part", resolution_part)
        # Further split the first part at '/' to extract the width (2560)
        width = resolution_part[0].split("/")[0]
        print("width", width)
        return int(width)

    def _get_monitor_height_px(self, monitor_res: str):
        resolution_part = monitor_res.split("x")

        # Split the second part at '/' to extract the height (1440)
        height = resolution_part[1].split("/")[0]
        print("height", height)
        return int(height)

    def _set_monitor_width_px(self, monitor_res: str, width_px: int):
        monitor_res_tmp = monitor_res.split("/")
        monitor_res_tmp[0] = str(width_px)
        monitor_res = "/".join(monitor_res_tmp)
        return monitor_res

    def _set_monitor_x_offset(self, monitor_res: str, x_offset: int):
        monitor_res_tmp = monitor_res.split("+")
        monitor_res_tmp[1] = str(x_offset)
        monitor_res = "+".join(monitor_res_tmp)
        return monitor_res

    def _get_monitor_physical_height(self, monitor_res: str):
        resolution_part = monitor_res.split("x")
        height = resolution_part[0].split("+")[0].split("/")[1]
        return int(height)

    def _get_monitor_physical_width(self, monitor_res: str):
        resolution_part = monitor_res.split("x")
        width = resolution_part[1].split("+")[0].split("/")[1]
        return int(width)

    def _get_monitor_x_offset(self, monitor_res: str = ""):
        resolution_part = monitor_res.split("+")
        x = resolution_part[1]
        return int(x)

    def _get_monitor_y_offset(self, monitor_res: str = ""):
        resolution_part = monitor_res.split("+")
        y = resolution_part[2]
        return int(y)

    def get_monitor_list(self):
        subprocess.run("xrandr")
