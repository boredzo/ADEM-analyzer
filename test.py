#!/usr/bin/python3

import os
import sys
import re
import pathlib
import fnmatch
import itertools
import bs4

district_heading_exp = re.compile('Assembly District ([0-9]+)')
district_href_exp = re.compile('/ad-([0-9]+)')

sys.intern('SIF')
sys.intern('OSIF')

output_mode_text = 'text'
output_mode_csv = 'csv'

def find_container(h2):
	"Find an element that contains this h2 and a table. The table should be the list of results described by the h2."
	container = h2.parent
	while container and not container.find('table'):
		container = container.parent
	return container

def extract_names_and_vote_counts(trs, gender_category):
	for row in trs[1:]:
		name_td, vote_count_td = row.find_all('td')
		name_strongs = name_td.find('strong')
		if name_strongs:
			name = next(name_strongs.children)
			is_winner = True
		else:
			name = next(name_td.children)
			is_winner = False

		vote_count_strong = vote_count_td.find('strong')
		if vote_count_strong:
			vote_count_str = vote_count_strong.string
		else:
			vote_count_str = vote_count_td.string

		if name == 'Name' and vote_count_str == 'SUM of Vote':
			continue

		try:
			vote_count = int(vote_count_str)
		except:
			print(row)
			raise

		yield (name, gender_category, vote_count, is_winner)

def sort_key_for_result(row, _categories=[ 'SIF', 'OSIF' ]):
	name, gender_category, vote_count, is_winner = row
	if is_winner:
		return 0 if is_winner else 1, _categories.index(gender_category), -vote_count
	else:
		return 0 if is_winner else 1, len(_categories), -vote_count

def ingest(path, output_mode):
	soup = bs4.BeautifulSoup(open(path, 'r'), 'lxml')

	later_h3 = soup.find('h3')
	if later_h3 and later_h3.string == 'Results will be made public on February 15th, 2021.':
		# AD 59 got an extension because of a ballot snafu.
		return

	h2s = soup.find_all('h2')
	district_h2 = h2s[0]
	try:
		eboard_h2 = h2s[1]
	except IndexError:
		strongs = soup.find_all('strong')
		for x in strongs:
			contents = next(x.children)
			if contents == 'Executive Board':
				eboard_strong = x

		eboard_td = eboard_strong.find_parent('td')
	else:
		tds = find_container(eboard_h2).find_all('td')
		for x in tds:
			contents = next(x.children)
			if contents == 'Winner':
				continue
			eboard_td = x

	eboard_winner_name = eboard_td.string

	try:
		sif_h2 = h2s[2]
		osif_h2 = h2s[3]
	except IndexError:
		strongs = soup.find_all('strong')
		for x in strongs:
			contents = next(x.children)
			if contents == 'Self Identified Female':
				sif_strong = x
			elif contents == 'Other Than Self Identified Female':
				osif_strong = x
		sif_td = sif_strong.find_parent('td')
		osif_td = osif_strong.find_parent('td')
		sif_trs = sif_td.parent.parent.find_all('tr')
		osif_trs = osif_td.parent.parent.find_all('tr')
	else:
		sif_trs = find_container(sif_h2).find_all('tr')
		osif_trs = find_container(osif_h2).find_all('tr')

	district_long = next(district_h2.children)
	try:
		district_number_str = district_heading_exp.match(district_long).group(1)
	except AttributeError:
		# Page heading is simply 'Assembly District ' with no number.
		# Use the canonical link, which should end in something like /ad-99.
		canonical_link = soup.find('link', rel='canonical')
		href = canonical_link['href']
		district_number_str = district_href_exp.search(href).group(1)

	sif_results = extract_names_and_vote_counts(sif_trs, 'SIF')
	osif_results = extract_names_and_vote_counts(osif_trs, 'OSIF')
	all_results = itertools.chain(sif_results, osif_results)
	all_results = list(sorted(all_results, key=sort_key_for_result))

	if output_mode == output_mode_text:
		print('AD-{0}'.format(district_number_str))
		print()
		print(len(all_results), 'candidates')
		for name, gender_category, vote_count, is_winner in all_results:
			print("{0}{1}\t{2}\t{3}".format('*' if is_winner else '', name, gender_category, vote_count))
	elif output_mode == output_mode_csv:
		import csv
		writer = csv.writer(sys.stdout)
		for name, gender_category, vote_count, is_winner in all_results:
			values = [
				str(path),
				district_number_str,
				name,
				gender_category,
				vote_count,
				'won' if is_winner else 'lost',
				'eboard' if (eboard_winner_name == name) else '',
			]
			writer.writerow(values)
	else:
		sys.exit('Unknown output mode: ' + output_mode)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--output-mode', default=output_mode_csv, choices=[ output_mode_csv, output_mode_text ], metavar='MODE', help='Comma-separated values (default) or text (readable plain-text output).')
	parser.add_argument('paths', action='append', default=[], help='Paths to Assembly District results webpage files to process for results.')
	opts = parser.parse_args()

	results_filename_exp = re.compile('^ad-([0-9]+).html$')
	def sort_key_for_filename(filename):
		match = results_filename_exp.match(filename)
		if not match:
			return (9999, filename)
		else:
			return (int(match.group(1)), filename)
	for path_str in opts.paths:
		src_path = pathlib.Path(path_str)
		del path_str

		if src_path.is_dir():
			for dir_path, subdir_names, file_names in os.walk(src_path):
				dir_path = pathlib.Path(dir_path)
				file_names.sort(key=sort_key_for_filename)
				for name in file_names:
					if results_filename_exp.match(name):
						file_path = dir_path.joinpath(name)
						ingest(file_path, opts.output_mode)
		else:
			ingest(src_path, opts.output_mode)
