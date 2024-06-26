#!/usr/bin/env python3
import copy
import csv
import json
from pathlib import Path

from aiohttp import web
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


async def handle_request(request):
	# far from optimal, but datasets are small and I wanted to keep it simple and small
	filename = request.match_info.get('filename', None)

	if filename not in data:
		return web.Response(status=404)

	out = data[filename][:]
	for k, v in request.rel_url.query.items():
		print(f'{k}: {v}')

		if k not in out[0]:
			out = []
			break

		if v.startswith(">="):
			cmp = lambda o, v: o >= v
			v = v[2:]
		elif v.startswith("<="):
			cmp = lambda o, v: o <= v
			v = v[2:]
		elif v.startswith(">"):
			cmp = lambda o, v: o > v
			v = v[1:]
		elif v.startswith('<'):
			cmp = lambda o, v: o < v
			v = v[1:]
		else:
			cmp = lambda o, v: o == v

		# to make comparsions work on numbers, not strings, if possible
		try:
			v = float(v)
		except ValueError:
			pass

		for i in out[:]:
			o = i[k]

			try:
				o = float(o)
			except ValueError:
				pass

			try:
				if not cmp(o, v):
					out.remove(i)
			except Exception as e:
					print("Error happened:", e)
					out.remove(i)

	return web.Response(text=json.dumps(out), content_type="application/json")


def load_csv_files(in_dir: Path):
	out = {}

	for f in in_dir.iterdir():
		if f.is_file() and f.name.endswith('.csv'):
			with open(f, newline='') as csvfile:
				reader = csv.DictReader(csvfile)
				out[f.name[:-4]] = list(reader)

	return out


class FileReloadEventHandler(FileSystemEventHandler):
	def on_any_event(self, event):
		print("Datafiles changed, reloading")
		global data
		data = load_csv_files(csv_path)


if __name__ == '__main__':
	app = web.Application()
	app.add_routes([web.get('/{filename}', handle_request)])

	print("Loading datafiles")
	csv_path = Path("data")
	data = load_csv_files(csv_path)

	fs_event_handler = FileReloadEventHandler()
	observer = Observer()
	observer.schedule(fs_event_handler, str(csv_path), recursive=True)
	observer.start()

	print("Webserver starting")
	web.run_app(app, port=9999)
	print("Webserver stopping")

	observer.stop()
	observer.join()

	print("Webserver stopped")
