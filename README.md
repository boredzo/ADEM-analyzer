# ADEM ballot analyzer

## Goal

This tool's purpose is to independently audit the 2021 [ADEM](https://adem.cadem.org/) election.

ADEM is the California Democratic Party's Assembly District Election Meeting. Every year, people in every Assembly District run to be an Assembly District Delegate (ADD) to the Democratic Party. Candidates and voters must be registered Democrats.

In 2021, the ADEM was all-vote-by-mail because of the covid pandemic, and it was… kind of a mix. The overall design was good, but overly-ambitious deadlines and ballots that arrived in some voters' hands after the deadline to return them have disenfranchised an unknown number of voters, and some folks have found results in their AD to be surprising, even questionable.

The Party is posting all of the scanned ballots as PDFs. This tool will analyze the distribution of ballots and, with an appropriate ballot scanner, the votes therein. It will generate a searchable index of voter ID numbers so voters can see whether their ballot was received and whether it was counted.

This tool will also compare its own results to the results posted by the Party.

## Usage

analyze.py expects a variety of input files in a certain layout, in the same directory/folder as the tool.

- ballots/
  - ballots/AD 99
    - ballots/AD 99/AD 99 Invalid Ballots
    - ballots/AD 99/AD 99 Valid Ballots
- posted-results/
  - ad-99.html

analyze.py will create as output:

- output/report.txt: A plain-text report of its findings, based at minimum upon the distribution of files in the ballots/ directory, and comparison of the votes found in those ballots to the posted results if possible.
- output/ballot-index.csv: A comma-separated values file containing a list of every ballot found, with the following columns:
  - relative pathname (e.g., `ballots/AD 99/AD 99 Valid Ballots/CADEM_…_99.pdf`)
  - Assembly district
  - voter ID number (note: ? will be present in place of each digit that couldn't be scanned or wasn't marked)
  - `valid`, `invalid-overvote`, `invalid-no-voter-ID`, or `invalid-unknown`

## How can I help?

Take a look at [the issues](https://github.com/boredzo/ADEM-analyzer/issues/) and see what needs working on. 

This suite is written in Python 3.