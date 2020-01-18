#!/usr/bin/env python3
import json

import cloudscraper
from bs4 import BeautifulSoup


class UserBenchmarkScraper(object):
	def __init__(self, base_url, tdsubtype, sess=None):
		self.base_url = base_url
		self.tdsubtype = tdsubtype
		self.sess = sess if sess is not None else cloudscraper.create_scraper()
		self.main_page = self.sess.get(base_url).text
		self.view_state = self.main_page.split('id="j_id1:javax.faces.ViewState:0" value="', 1)[1].split('"', 1)[0]

	def send_action(self, tda_options:dict=None, options:dict=None):
		tdahinid = {"fn": "tda", "tdtype": "TD_MC", "tdsubtype": self.tdsubtype}

		if tda_options is not None:
			tdahinid.update(tda_options)

		data = {
			'tableDataForm': 'tableDataForm',
			'tableDataForm:tdahinid': json.dumps(tdahinid),
			'javax.faces.ViewState': self.view_state,
			'javax.faces.partial.ajax': 'true',
		}

		if options is not None:
			data.update(options)

		ret = self.sess.post(f"{self.base_url}/pages/mctablep.jsf", data)
		self.view_state = ret.text.split('<update id="j_id1:javax.faces.ViewState:0"><![CDATA[', 1)[1].split(']]', 1)[0]

		return ret

	# def prepare_expert_view(self):
	# 	resp = self.send_action({"action": "benchconfview"},
	# 													{'javax.faces.behavior.event': 'action', 'javax.faces.source': 'tableDataForm:tdaid'})
	# 	return resp.status_code == 200

	def add_column(self, column):
		resp = self.send_action({"action": "unhidecol", "th": column},
														{'javax.faces.behavior.event': 'action', 'javax.faces.source': 'tableDataForm:tdaid'})
		return resp.status_code == 200

	def sort_by(self, column):
		resp = self.send_action({"action": "sort", "th": column},
														{'javax.faces.behavior.event': 'action', 'javax.faces.source': 'tableDataForm:tdaid'})
		return resp.status_code == 200

	def get_page(self, pgnr=1):
		body = self.send_action(options={'PGMP': pgnr, 'javax.faces.partial.render': 'tableDataForm:mhtddyntac'}).text

		bs = BeautifulSoup(body, "html.parser")
		bs = BeautifulSoup(bs.find('update', id="tableDataForm:mhtddyntac").text, "html.parser")
		table = bs.find_all('table', limit=2)[1]

		thead = table.find('thead').find_all('th')
		thead_text = [" ".join(e.text.split()) for e in thead]
		thead_id = [e['data-mhth'] if 'data-mhth' in e.attrs else '' for e in thead]

		thead_text[0] = '#'
		thead_text[1] = 'Userbenchmark ID'
		thead_id[0] = 'NUM'
		thead_id[1] = 'ID'

		thead_text.append("Userbenchmark Part URL")
		thead_id.append("URL")


		tbody = [tr.find_all('td') for tr in table.find('tbody').find_all('tr')]
		tbody_text = []
		for row in tbody:
			part_id = row[1].find(attrs={'data-id': True})['data-id']
			row_text = [row[0].text.strip(), part_id]
			for col in row[2:]:
				col_tc = col.find(class_='mh-tc')
				col = col_tc if col_tc else col
				row_text.append(" ".join(col.get_text(" ").split()))
			row_text.append(f"{self.base_url}/SpeedTest/{part_id}/")
			tbody_text.append(row_text)

		return thead_id, thead_text, tbody_text


if __name__ == '__main__':
	import re
	import argparse
	import csv

	arg = argparse.ArgumentParser()
	arg.add_argument("--type", default="CPU", choices=["CPU", "GPU", "SSD", "HDD", "RAM", "USB"], type=str.upper)
	arg.add_argument("--describe", '-d', default=0, action='store_const', const=1, help="Human readable headers in CSV file")
	arg.add_argument('out', type=argparse.FileType('w', encoding='UTF-8'))
	args = arg.parse_args()

	print("Starting parsing userbenchmark", args.type, "category")
	s = UserBenchmarkScraper(f"https://{args.type.lower()}.userbenchmark.com", "MC"+args.type)

	for col in re.finditer("{action:'unhidecol',th:'(.*?)'}", s.main_page):
		# show all possible columns
		print("Unhiding column:", col[1])
		s.add_column(col[1])

	print("Sorting by best benchmark scores")
	s.sort_by('MC_BENCH')		# sort by benchmark score

	cpu_writer = csv.writer(args.out)

	pages = int(s.main_page.split('<a>Page 1 of ', 1)[1].split('</a>', 1)[0])
	print("Found", pages, "pages.")

	for pg in range(1, pages+1):
		print('Loading page', pg)
		page = s.get_page(pgnr=pg)
		if pg <= 1:
			print(page[1])
			print(page[0])
			cpu_writer.writerow(page[args.describe])
		for row in page[2]:
			cpu_writer.writerow(row)

	args.out.close()
