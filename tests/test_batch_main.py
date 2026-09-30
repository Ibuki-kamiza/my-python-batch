from src.batch_main import process_records


def test_process_records_calculates_amount():
    input_data = [{"amount": "100"}]
    result = process_records(input_data)
    assert result[0]["amount"] == 110.0


def test_process_records_skips_invalid_amount():
    input_data = [{"amount": "not_a_number"}]
    result = process_records(input_data)
    assert result == []
