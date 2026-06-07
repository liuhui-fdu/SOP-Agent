.PHONY: run test test2 coverage-test2 verify report

run:
	python3 main.py

test:
	python3 -m unittest discover -s tests

test2:
	python3 -m unittest discover -s test2

coverage-test2:
	python3 scripts/coverage_test2.py

verify:
	python3 scripts/verify.py

report:
	python3 scripts/generate_report.py
