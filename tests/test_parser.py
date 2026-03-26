import pytest

from services.parser import parse_expense


@pytest.mark.parametrize(
    "text, expected_amount, expected_currency, expected_desc",
    [
        ("500 lidl", 500.0, None, "lidl"),
        ("50€ lidl", 50.0, "EUR", "lidl"),
        ("50 eur lidl", 50.0, "EUR", "lidl"),
        ("1200.50 leroy merlin", 1200.50, None, "leroy merlin"),
        ("200 pln бензин", 200.0, "PLN", "бензин"),
        ("200zł бензин", 200.0, "PLN", "бензин"),
        ("500₽ продукты", 500.0, "RUB", "продукты"),
        ("500 rub продукты", 500.0, "RUB", "продукты"),
        ("lidl 50€", 50.0, "EUR", "lidl"),
        ("lidl 50", 50.0, None, "lidl"),
        ("500", 500.0, None, ""),
        ("500€", 500.0, "EUR", ""),
        ("12,50 кафе", 12.50, None, "кафе"),
        ("32.99 zara", 32.99, None, "zara"),
    ],
)
def test_parse_expense(text, expected_amount, expected_currency, expected_desc):
    result = parse_expense(text)
    assert result is not None
    assert result.amount == pytest.approx(expected_amount)
    assert result.currency == expected_currency
    assert result.description == expected_desc


def test_parse_rejects_commands():
    assert parse_expense("/report") is None


def test_parse_rejects_empty():
    assert parse_expense("") is None


def test_parse_rejects_no_number():
    assert parse_expense("just some text") is None
