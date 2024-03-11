#!/usr/bin/env python3
import math
import re
import time

import requests


base_urls = {
    "CPU": "https://www.cpubenchmark.net/CPU_mega_page.html",
    "GPU": "https://www.videocardbenchmark.net/GPU_mega_page.html",
    "HDD": "https://www.harddrivebenchmark.net/hdd-mega-page.html",
}

ts = int(time.time())
data_urls = {
    "CPU": f"https://www.cpubenchmark.net/data/?_={ts}",
    "GPU": f"https://www.videocardbenchmark.net/data/?_={ts}",
    "HDD": f"https://www.harddrivebenchmark.net/data/?_={ts}",
}

part_urls = {
    'CPU': 'https://www.cpubenchmark.net/cpu.php?id=',
    'GPU': 'https://www.videocardbenchmark.net/gpu.php?id=',
    'HDD': 'https://www.harddrivebenchmark.net/hdd.php?id=',
    # 'RAM': 'https://www.memorybenchmark.net/ram.php?id=',
    # No mega page for memory
}

nan = re.compile(r'[^\d.]+')


def get_table(type):
    base_url = base_urls[type]
    part_url = part_urls[type]
    data_url = data_urls[type]

    sess = requests.session()
    sess.get(base_url)
    data = sess.get(data_url, headers={
            "X-Requested-With": "XMLHttpRequest"
    }).json()

    d = data['data'][0]
    head = ('rank', 'name', 'id', *sorted(k for k in d if k not in ('rank', 'name', 'id', 'href')), 'url')
    print("head:", head)

    items = []
    for i in data['data']:
        for numeric in ('id', 'rank', 'cpumark', 'thread', 'samples', 'tdp', 'speed', 'turbo', 'cpuCount', 'cores', 'logicals', 'secondaryCores', 'secondaryLogicals'):
            if numeric in i:
                v = i[numeric]
                if not v or v == 'NA':
                    i[numeric] = None
                elif v == 'Insufficient data':
                    i[numeric] = math.inf
                elif not isinstance(v, (int, float)):
                    stripped = nan.sub('', v)
                    i[numeric] = float(stripped) if '.' in stripped else int(stripped)

        i['url'] = f"{part_url}{i['id']}"

        line = tuple(i[k] for k in head)
        # print("line:", line)
        items.append(line)

    items.sort(key=lambda line: line[0])

    return head, items


if __name__ == '__main__':
    import argparse
    import csv

    arg = argparse.ArgumentParser()
    arg.add_argument('-t', '--type', default="CPU", choices=["CPU", "GPU", "HDD"], type=str.upper)
    arg.add_argument('-o', '--output_file', type=argparse.FileType('w', encoding='UTF-8'))
    args = arg.parse_args()

    print("Starting parsing Passmark", args.type, "category")

    csv_writer = csv.writer(args.output_file)

    head, items = get_table(args.type)
    csv_writer.writerow(head)
    csv_writer.writerows(items)
    args.output_file.close()
