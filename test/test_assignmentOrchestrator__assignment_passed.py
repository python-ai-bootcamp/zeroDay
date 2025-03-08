import pytest
from unittest.mock import patch, mock_open
from assignmentOrchestrator import assignment_passed

def test_assignment_passed___when_no_previous_submissions_exist():
    assert assignment_passed([]) == False
def test_assignment_passed___when_only_FAIL_results_exist():
    assert assignment_passed([{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}}]) == False
def test_assignment_passed___when_only_single_FAIL_results_exist():
    assert assignment_passed([{"result":{"status":"FAIL"}}]) == False
def test_assignment_passed___when_only_PASS_results_exist():
    assert assignment_passed([{"result":{"status":"PASS"}},{"result":{"status":"PASS"}},{"result":{"status":"PASS"}},{"result":{"status":"PASS"}}]) == True
def test_assignment_passed___when_only_single_PASS_results_exist():
    assert assignment_passed([{"result":{"status":"PASS"}}]) == True
def test_assignment_passed___when_at_least_single_PASS_results_exist():
    assert assignment_passed([{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}}]) == True
    assert assignment_passed([{"result":{"status":"PASS"}},{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}}]) == True
    assert assignment_passed([{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}},{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}}]) == True
    assert assignment_passed([{"result":{"status":"PASS"}},{"result":{"status":"PASS"}},{"result":{"status":"FAIL"}},{"result":{"status":"FAIL"}}]) == True
    assert assignment_passed([{"result":{"status":"FAIL"}},{"result":{"status":"PASS"}},{"result":{"status":"PASS"}},{"result":{"status":"FAIL"}}]) == True
