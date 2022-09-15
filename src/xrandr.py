#!/usr/bin/env python3
import subprocess
import shlex
import re

class XRandr:
    def __init__(self):
        self.list_active_monitors = ""

    def _update_list_active_monitors(self) -> None:
        command = "xrandr --listactivemonitors"
        output = subprocess.run(shlex.split(command), capture_output=True, encoding="utf-8")
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

    def split_primary_monitor(self, split_ratio) -> bool:
        # TODO: 
        #   Verify split_ratio is equal to 100 if exits
        #
        #  xrandr --setmonitor DP-0-1 1280/597x1440/336+0+0     DP-0
        #  xrandr --setmonitor DP-0-2 1280/597x1440/336+1280+0  none
        self._update_list_active_monitors()
        primary_monitor_info = self._get_primary_monitor_raw()
        try:
            primary_monitor_name = self._get_monitor_name(primary_monitor_info)
        except IndexError:
            print("Error: If you are in split mode restore and split again")
            return False

        primary_monitor_res = self._get_monitor_res(primary_monitor_info)
        width_px: int = self._get_monitor_width_px(monitor_name = primary_monitor_name)
        x_offset = self._get_monitor_x_offset(monitor_name = primary_monitor_name)
        
        vmonitor_name = primary_monitor_name
        vmonitor_offset = 0
        for ratio in split_ratio:
            new_width_px = int(width_px * ratio/100)
            x_offset += vmonitor_offset
            #  print(new_width_px, x_offset)
            primary_monitor_res = self._set_monitor_width_px(primary_monitor_res, new_width_px)
            primary_monitor_res = self._set_monitor_x_offset(primary_monitor_res, x_offset)
            command = f"xrandr --setmonitor V-{primary_monitor_name}-{ratio} {primary_monitor_res} {vmonitor_name}"
            print(command)
            subprocess.run(shlex.split(command), capture_output=True, encoding="utf-8")
            
            # Prepare for next stage
            vmonitor_offset = new_width_px
            vmonitor_name = "none"
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
        return vmonitor_list

    def _get_monitor_name(self, monitor_info: str) -> str:
        return re.sub(r"^\W+", "", monitor_info.split()[1])
    
    def _get_monitor_res(self, monitor_info) -> str:
        return monitor_info.split()[2]

    def _get_monitor_width_px(self, monitor_name: str):
        monitor_info = self._get_monitor_info_by_name(monitor_name)
        return int(monitor_info.split()[2].split("/")[0])

    def _set_monitor_width_px(self, monitor_res: str, width_px: int):
        monitor_res_tmp = monitor_res.split("/")
        monitor_res_tmp[0] = str(width_px)
        monitor_res = "/".join(monitor_res_tmp)
        return monitor_res

    def _set_monitor_x_offset(self, monitor_res: str, x_offset: int):
        monitor_res_tmp =  monitor_res.split("+")
        monitor_res_tmp[1] = str(x_offset)
        monitor_res = "+".join(monitor_res_tmp)
        return monitor_res

    def _get_monitor_x_offset(self, monitor_name: str = ""):
        monitor_info = self._get_monitor_info_by_name(monitor_name)
        return int(monitor_info.split()[2].split("+")[1])

    def get_monitor_list(self):
        subprocess.run("xrandr")

    



        
        
