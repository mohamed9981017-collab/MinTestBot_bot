"""Entrypoint for the RSS -> Telegram job hunter bot.

Usage:
    python main.py --once      # run a single poll cycle and exit
    python main.py             # poll forever every POLL_INTERVAL seconds
    python main.py --once --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from jobhunter.config import Config
from jobhunter.hunter import run_once

logger = logging.getLogger("jobhunter")


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        level=logging.DEBUG if verbose else logging.INFO,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RSS -> Telegram job hunter bot")
    parser.add_argument("--once", action="store_true", help="run one poll cycle and exit")
    parser.add_argument("--dry-run", action="store_true", help="log matches without sending")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable debug logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_logging(args.verbose)

    try:
        config = Config.from_env()
    except ValueError as exc:
        logger.error("configuration error: %s", exc)
        return 2

    if args.dry_run:
        config.dry_run = True

    if not config.feeds:
        logger.error("no feeds configured; set RSS_FEEDS or RSS_FEEDS_FILE")
        return 2

    if config.dry_run:
        logger.info("dry-run enabled; nothing will be sent to Telegram")

    try:
        if args.once:
            logger.info("run once: %s", run_once(config))
            return 0

        logger.info("starting poll loop every %ss", config.poll_interval)
        while True:
            logger.info("cycle: %s", run_once(config))
            time.sleep(config.poll_interval)
    except KeyboardInterrupt:
        logger.info("interrupted, exiting")
        return 0


if __name__ == "__main__":
    sys.exit(main())
