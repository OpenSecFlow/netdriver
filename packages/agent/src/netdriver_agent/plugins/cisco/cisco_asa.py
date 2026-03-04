#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netdriver_agent.client.channel import ReadBuffer
from netdriver_core.dev.mode import Mode
from netdriver_core.exception.errors import ConfigFailed
from netdriver_core.plugin.plugin_info import PluginInfo
from netdriver_agent.plugins.cisco import CiscoBase
from netdriver_core.utils.asyncu import async_timeout


# pylint: disable=abstract-method
class CiscoASA(CiscoBase):
    """ Cisco ASA Plugin """

    info = PluginInfo(
            vendor="cisco",
            model="asa",
            version="base",
            description="Cisco ASA Plugin"
        )

    _CMD_CANCEL_MORE = "terminal pager 0"
    _CMD_MAX_TERMINAL_WIDTH = "terminal width 0"
    _is_set_max_terminal_width = False

    @async_timeout(5)
    async def config(self) -> str:
        """ Enter config mode

        @raise ConfigFailed: config failed
        """
        self._logger.info("Entering config mode")
        pattern_modes = self.get_mode_prompt_patterns()
        pattern_config = pattern_modes.get(Mode.CONFIG)
        pattern_enable = pattern_modes.get(Mode.ENABLE)

        await self.write_channel(self._CMD_CONFIG)
        output = ReadBuffer(cmd=self._CMD_CONFIG)
        try:
            while not self._channel.read_at_eof():
                ret = await self.read_channel()
                output.append(ret)
                if pattern_config and output.check_pattern(pattern_config, False):
                    self._mode = Mode.CONFIG
                    self._logger.info("Entered config mode")
                    break
                if pattern_enable and output.check_pattern(pattern_enable):
                    self._logger.info("Config failed, got enable prompt")
                    raise ConfigFailed("Config failed, got enable prompt", output=output.get_data())
        except ConfigFailed as e:
            raise e
        except Exception as e:
            raise ConfigFailed(msg=str(e), output=output.get_data()) from e
        if not self._is_set_max_terminal_width:
            ret = await self.set_max_terminal_width()
            output.append(ret)
            self._is_set_max_terminal_width = True
        return output.get_data()

    async def set_max_terminal_width(self):
        return await self.exec_cmd(self._CMD_MAX_TERMINAL_WIDTH)