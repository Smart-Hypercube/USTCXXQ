# coding=utf-8

import argparse
import logging
import os
import socket
import threading

from .config import COOKIE_FILE
from .logger import logger
from .app import bot, plugin_manager
from .handler import MessageObserver
from .messages import mk_msg
from .excpetions import ServerResponseEmpty, NeedRelogin
from .signals import bot_inited_registry


def clean_cookie():
    if os.path.isfile(COOKIE_FILE):
        os.remove(COOKIE_FILE)
    logger.info("Cookie file removed.")


def main_loop(new_user=False, debug=False):
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.info("Initializing...")
    plugin_manager.load_plugin()
    if new_user:
        clean_cookie()
    bot.login()
    observer = MessageObserver(bot)

    for name, func in bot_inited_registry.items():
        try:
            t = threading.Thread(target=func, args=(bot,))
            t.daemon = True
            t.start()
        except Exception:
            logging.exception(
                "Error occurs while loading plugin [%s]." % name
            )
    while True:
        try:
            msg_list = bot.check_msg()
            if msg_list is not None:
                observer.handle_msg_list(
                    [mk_msg(msg, bot) for msg in msg_list]
                )
        except ServerResponseEmpty:
            continue
        except (socket.timeout, IOError):
            logger.warning("Message pooling timeout, retrying...")
        except NeedRelogin:
            exit(0)
        except Exception:
            logger.exception("Exception occurs when checking msg.")


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--new-user",
        action="store_true",
        default=False,
        help="Logout old user first(by clean the cookie file.)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Switch to DEBUG mode for better view of requests and responses."
    )
    args = parser.parse_args()
    main_loop(**vars(args))


if __name__ == "__main__":
    run()
