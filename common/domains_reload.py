from requests import get
from ujson import loads, dump
from time import sleep

import config

def reload_domain_info():
    while True:
        api_url = f'https://api.evernode.network/support/domains'
        api_req = get(api_url)
        data = loads(api_req.text)

        with open("data\domains.json", "w") as outfile:
            dump(data, outfile)

        time = config.domains_reload_time
        sleep(time)