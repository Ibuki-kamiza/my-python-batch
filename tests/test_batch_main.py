from src.batch_main import process_records, validate_record


def test_process_records_calculates_amount_with_tax():
    input_data = [
        {"date": "2026-10-01", "name": "apple", "category": "fruit", "amount": "100"}
    ]
    processed, error_count = process_records(input_data)
    assert processed[0]["amount"] == 110.0
    assert error_count == 0


def test_process_records_skips_negative_amount():
    input_data = [
        {"date": "2026-10-01", "name": "chair", "category": "furniture", "amount": "-30"}
    ]
    processed, error_count = process_records(input_data)
    assert processed == []
    assert error_count == 1


def test_validate_record_requires_name():
    record = {"date": "2026-10-01", "name": "", "category": "fruit", "amount": "100"}
    assert validate_record(record) is not None
