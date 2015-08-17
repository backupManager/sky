#!/usr/bin/env python3.4

"""A simple web crawler -- main driver program."""

import asyncio
import logging
import sys

from .crawling import Crawler
from .reporting import report
import os

def get_loop(select = False):
    if os.name == 'nt':
        from asyncio.windows_events import ProactorEventLoop
        loop = ProactorEventLoop()
    elif select:
        loop = asyncio.SelectorEventLoop()
    else:
        loop = asyncio.get_event_loop()
    return loop

def get_config(config, loop): 
    for i in range(len(config['seed_urls'])):
        if '://' not in config['seed_urls'][i]:
            config['seed_urls'][i] = 'http://' + config['seed_urls'][i]

    config['loop'] = loop
    
    return config
    
    
def start(config, crawler_class = Crawler, save_data_fn = None, logging_level = 2):
    """Main program.

    Parse arguments, set up event loop, run crawler, print report.
    """

    logging_levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level = logging_levels[min(logging_level, len(logging_levels)-1)])

    loop = asyncio.SelectorEventLoop()

    asyncio.set_event_loop(loop)
    conf = get_config(config, loop) 

    crawler = crawler_class(conf) 

    if save_data_fn is not None:
        crawler.save_data = save_data_fn

    if crawler.login_url:
        loop.run_until_complete(crawler.login())
    
    try:
        loop.run_until_complete(crawler.crawl())  # Crawler gonna crawl.
    except KeyboardInterrupt:
        sys.stderr.flush()
        print('\nInterrupted\n')
    finally:
        result = crawler.finish_leftovers()
        report(crawler) 
        crawler.close()
        loop.close()
    return result