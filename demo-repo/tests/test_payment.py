from app import get_payment_config


def test_payment_config() -> None:
    config = get_payment_config()

    assert config["timeout"] > 0
    assert config["timeout"] <= 10
    assert config["max_retries"] <= 5

