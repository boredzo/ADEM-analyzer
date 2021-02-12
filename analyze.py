#!/usr/bin/python3

import os
import sys
import re
import pathlib
import argparse
import itertools

parser = argparse.ArgumentParser()
opts = parser.parse_args()

def analyze_ballots():
	num_ballots_valid_overall = 0
	num_ballots_invalid_overall = 0
	district_number_strings = []
	num_ballots_valid_by_district = {}
	num_ballots_invalid_by_district = {}

	num_ballots_requested = 169_743
	ballot_pdf_glob_pattern_fmt = 'CADEM_???_??????_%s.pdf'
	has_ballot_analysis = False #TODO

	dir_path, subdir_names, file_names = next(iter(os.walk('ballots')))
	dir_path = pathlib.Path(dir_path)
	district_subdir_exp = re.compile('^AD ([0-9]{2})$')
	for subdir in subdir_names:
		match = district_subdir_exp.match(subdir)
		if not match:
			# This is some other subdirectory, not a subdirectory of ballots from an Assembly District.
			continue
		district_name = subdir
		district_number_str = match.group(1)
		district_number_strings.append(district_number_str)
		ballot_pdf_glob_pattern = ballot_pdf_glob_pattern_fmt % (district_number_str,)

		district_path = dir_path.joinpath(subdir)
		district_valid_dir_path = district_path.joinpath(district_name + ' Valid Ballots')
		district_invalid_dir_path = district_path.joinpath(district_name + ' Invalid Ballots')

		valid_ballot_subpaths = list(district_valid_dir_path.glob(ballot_pdf_glob_pattern))
		num_ballots_valid_by_district[district_number_str] = len(valid_ballot_subpaths)
		num_ballots_valid_overall += len(valid_ballot_subpaths)
		invalid_ballot_subpaths = list(district_invalid_dir_path.glob(ballot_pdf_glob_pattern))
		num_ballots_invalid_by_district[district_number_str] = len(invalid_ballot_subpaths)
		num_ballots_invalid_overall += len(invalid_ballot_subpaths)

	num_ballots_total_overall = num_ballots_valid_overall + num_ballots_invalid_overall

	try: os.mkdir('output')
	except FileExistsError: pass
	with open('output/report.txt', 'w') as f:
		print('Ballots requested: {0:,}'.format(num_ballots_requested), file=f)
		print('Ballots received: {0:,}'.format(num_ballots_total_overall), '({0:.2%} of requested)'.format(num_ballots_total_overall / num_ballots_requested), file=f)
		print('Ballots determined to be valid: {0:,}'.format(num_ballots_valid_overall), '({0:.2%} of received)'.format(num_ballots_valid_overall / num_ballots_total_overall), file=f)
		print('Ballots determined to be invalid: {0:,}'.format(num_ballots_invalid_overall), '({0:.2%} of received)'.format(num_ballots_invalid_overall / num_ballots_total_overall), file=f)

		if has_ballot_analysis:
			print(file=f)
			# TODO: Print the figures for things like under- and over-votes.

		for district_number_str in district_number_strings:
			print(file=f)
			print('## AD-%s breakdown' % (district_number_str,), file=f)
			print(file=f)

			num_ballots_valid_in_district = num_ballots_valid_by_district[district_number_str]
			num_ballots_invalid_in_district = num_ballots_invalid_by_district[district_number_str]
			num_ballots_total_in_district = num_ballots_valid_in_district + num_ballots_invalid_in_district
			print('Ballots received: {0:,}'.format(num_ballots_total_in_district), '({0:.2%} of overall)'.format(num_ballots_total_in_district / num_ballots_total_overall), file=f)
			print('Ballots determined to be valid: {0:,}'.format(num_ballots_valid_in_district), '({0:.2%} of received)'.format(num_ballots_valid_in_district / num_ballots_total_in_district), file=f)
			print('Ballots determined to be invalid: {0:,}'.format(num_ballots_invalid_in_district), '({0:.2%} of received)'.format(num_ballots_invalid_in_district / num_ballots_total_in_district), file=f)
	
			if has_ballot_analysis:
				print(file=f)
				# TODO: Print the figures for things like under- and over-votes.

	return bool(num_ballots_total_overall)

def analyze_posted_results():
	try: import bs4
	except ImportError, e:
		print(e, file=sys.stderr)
		return False
	def generate_won_lost():
		return itertools.chain(itertools.repeat('won', 7), itertools.repeat('lost'))
	posted_results_dir_path = pathlib.Path('posted-results')
	for page_file_path in posted_results_dir_path.glob('ad-??.html'):
		soup = bs4.BeautifulSoup(open(page_file_path, 'r'))
	return False

def main(opts):
	returncode = 0
	if not analyze_ballots():
		print('Failed to analyze ballots', file=sys.stderr)
		returncode = 1
	if not analyze_posted_results():
		print('Failed to analyze posted results', file=sys.stderr)
		returncode = 2
	return returncode

if __name__ == '__main__':
	sys.exit(main(opts))
