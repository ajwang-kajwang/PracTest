#!/bin/bash
#
# run_showcase.sh - the three showcase runs used in the report
#
# Student Name : ajwang-kajwang
# Student ID   : 6789998212
#
# Every run below uses the same code and differs only in its scenario
# file and command line switches - no source file is edited between
# them.  Each writes its report, results CSV and plots into results/.
#
set -e
cd "$(dirname "$0")"

echo "### Showcase 1 of 3: small club night, one mat, two event types"
python3 compSim.py --scenario scenarios/club_night.json \
        --no-animation --quiet

echo
echo "### Showcase 2 of 3: regional titles, two mats in parallel, four types"
python3 compSim.py --scenario scenarios/regional_titles.json \
        --no-animation --quiet

echo
echo "### Showcase 3 of 3: national grading, roster from CSV, seven belts"
python3 compSim.py --scenario scenarios/national_grading.json \
        --no-animation --quiet

echo
echo "### Bonus: parameter sweep over the size of the regional field"
python3 compSim.py --scenario scenarios/regional_titles.json \
        --sweep competitors.count=12,24,36 --repeats 3 --seed 1 --quiet

echo
echo "All showcase output is in results/"
