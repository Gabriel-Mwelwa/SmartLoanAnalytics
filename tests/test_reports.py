import csv

from modules import reports


def test_management_csv_export(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, "CSV_DIR", tmp_path)

    path = reports.export_management_csv()

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "KEY PERFORMANCE INDICATORS" in text
    assert "MANAGEMENT RECOMMENDATIONS" in text


def test_loan_records_csv_export(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, "CSV_DIR", tmp_path)

    path = reports.export_loan_records_csv()

    assert path.exists()
    with path.open(encoding="utf-8") as handle:
        header = next(csv.reader(handle))

    assert "loan_id" in header
    assert "customer_code" in header
    assert "status" in header


def test_repayment_records_csv_export(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, "CSV_DIR", tmp_path)

    path = reports.export_repayment_records_csv()

    assert path.exists()
    with path.open(encoding="utf-8") as handle:
        header = next(csv.reader(handle))

    assert "repayment_id" in header
    assert "loan_id" in header
    assert "amount" in header


def test_management_pdf_export(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, "PDF_DIR", tmp_path)

    path = reports.export_management_pdf()

    assert path.exists()
    assert path.stat().st_size > 500
    assert path.read_bytes()[:4] == b"%PDF"
