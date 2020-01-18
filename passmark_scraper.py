#!/usr/bin/env python3
import requests

from bs4 import BeautifulSoup

# TODO: additional parameters from child rows


def get_page(base_url, part_url):
	r = requests.get(base_url)
	bs = BeautifulSoup(r.text, "html.parser")

	table = bs.find(id='cputable')		# for every benchmark hw it's the same, for gpu and hdd

	thead = ['ID', 'URL'] + [next(e.strings) for e in table.find('thead').find('tr').find_all('th')]

	tbody = []
	for tr in table.find('tbody').find_all('tr', class_=False):
		tds = tr.find_all('td')
		part_id = tr['id'][3:]
		tr_a = [part_id, part_url+part_id]
		tr_a.extend([e.text for e in tds])

		tbody.append(tr_a)

	return thead, tbody


if __name__ == '__main__':
	import argparse
	import csv

	base_urls = {
		"CPU": "https://www.cpubenchmark.net/CPU_mega_page.html",
		"GPU": "https://www.videocardbenchmark.net/GPU_mega_page.html",
		"HDD": "https://www.harddrivebenchmark.net/hdd-mega-page.html"
	}
	
	part_urls = {
		'CPU': 'https://www.cpubenchmark.net/cpu.php?id=',
		'GPU': 'https://www.videocardbenchmark.net/gpu.php?id=',
		'HDD': 'https://www.harddrivebenchmark.net/hdd.php?id='
	}

	arg = argparse.ArgumentParser()
	arg.add_argument("--type", default="CPU", choices=["CPU", "GPU", "HDD"], type=str.upper)
	arg.add_argument('out', type=argparse.FileType('w', encoding='UTF-8'))
	args = arg.parse_args()

	print("Starting parsing Passmark", args.type, "category")

	csv_writer = csv.writer(args.out)

	thead, tbody = get_page(base_urls[args.type], part_urls[args.type])
	csv_writer.writerow(thead)
	csv_writer.writerows(tbody)
	args.out.close()
