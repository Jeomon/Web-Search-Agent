from dataclasses import dataclass
from typing import List, Literal
from pathlib import Path
from os import getcwd

@dataclass
class BrowserConfig:
    headless:bool=False
    user_data_dir:str=None
    wss_url:str=None
    downloads_path:str=Path(getcwd()).joinpath('./downloads').as_posix()
    browser:Literal['chrome','firefox','edge']='edge'
    slow_mo:int=300

SECURITY_ARGS = [
	'--disable-web-security',
	'--disable-site-isolation-trials',
	'--disable-features=IsolateOrigins,site-per-process',
]

BROWSER_ARGS=[
	'--no-sandbox',
	'--disable-blink-features=AutomationControlled',
	'--disable-infobars',
	'--disable-background-timer-throttling',
	'--disable-popup-blocking',
	'--disable-backgrounding-occluded-windows',
	'--disable-renderer-backgrounding',
	'--disable-window-activation',
	'--disable-focus-on-load',
	'--no-first-run',
	'--no-default-browser-check',
	'--no-startup-window',
	'--window-position=0,0',
]