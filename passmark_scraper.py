#!/usr/bin/env python3
import requests

from bs4 import BeautifulSoup

# TODO: additional parameters from child rows


def get_page(url):
	r = requests.get(url)
	bs = BeautifulSoup(r.text, "html.parser")

	table = bs.find(id='cputable')		# for every benchmark hw it's the same, for gpu and hdd

	thead = ['ID'] + [next(e.strings) for e in table.find('thead').find('tr').find_all('th')]

	tbody = []
	for tr in table.find('tbody').find_all('tr', class_=False):
		tds = tr.find_all('td')
		tr_a = [tr['id'][3:],]
		tr_a.extend([e.text for e in tds])

		tbody.append(tr_a)

	return thead, tbody


if __name__ == '__main__':
	import argparse
	import csv

	urls = {
		"CPU": "https://www.cpubenchmark.net/CPU_mega_page.html",
		"GPU": "https://www.videocardbenchmark.net/GPU_mega_page.html",
		"HDD": "https://www.harddrivebenchmark.net/hdd-mega-page.html"
	}

	arg = argparse.ArgumentParser()
	arg.add_argument("--type", default="CPU", choices=["CPU", "GPU", "HDD"], type=str.upper)
	arg.add_argument('out', type=argparse.FileType('w', encoding='UTF-8'))
	args = arg.parse_args()

	print("Starting parsing Passmark", args.type, "category")

	csv_writer = csv.writer(args.out)

	thead, tbody = get_page(urls[args.type])
	csv_writer.writerow(thead)
	csv_writer.writerows(tbody)
	args.out.close()
