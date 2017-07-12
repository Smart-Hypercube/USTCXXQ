# coding=utf-8

from .bot import QQBot
from .plugin import PluginManager

__all__ = ('bot',)

bot = QQBot()
plugin_manager = PluginManager(load_now=False)
