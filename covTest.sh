#!/bin/bash   
coverage erase;
python -m pytest --cov --cov-report term-missing;
coverage html;
start htmlcov/index.html
