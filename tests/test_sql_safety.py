from app.services.sql_safety import check_read_only_sql


def test_select_is_allowed():
    result = check_read_only_sql("SELECT id, name FROM users WHERE id = 1")
    assert result["allowed"] is True


def test_delete_is_blocked():
    result = check_read_only_sql("DELETE FROM users")
    assert result["allowed"] is False


def test_multiple_statements_are_blocked():
    result = check_read_only_sql("SELECT 1; DROP TABLE users;")
    assert result["allowed"] is False
