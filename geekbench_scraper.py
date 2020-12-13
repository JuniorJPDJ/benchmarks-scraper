#!/usr/bin/env python3
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# https://browser.geekbench.com/processor-benchmarks
# https://browser.geekbench.com/vulkan-benchmarks
# https://browser.geekbench.com/opencl-benchmarks
# https://browser.geekbench.com/cuda-benchmarks


def parse_table(table, url):
	thead = ["ID", "URL", "NAME", "SCORE"]
	tbody = []
	thead_names = ["ID", "URL"]

	for tr in table.find_all("tr"):
		tds = tr.find_all('td')
		if not tds:
			continue

		cpu = tds[0].find('a')
		tbody.append([cpu['href'].split('/')[-1], urljoin(url, cpu['href']), cpu.text, tds[1].text])

	return thead, tbody


if __name__ == '__main__':
	url = "https://browser.geekbench.com/processor-benchmarks"
	r = requests.get(url)
	bs = BeautifulSoup(r.text, "html.parser")

	sc = bs.find(id="single-core")
	mc = bs.find(id="multi-core")

	sc_parsed = parse_table(sc, url)
	mc_parsed = parse_table(mc, url)

	print(sc_parsed, mc_parsed)
