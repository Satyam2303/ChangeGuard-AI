from config import MAX_RETRIES, PAYMENT_TIMEOUT


def get_payment_config() -> dict[str, int]:
    return {
        "timeout": PAYMENT_TIMEOUT,
        "max_retries": MAX_RETRIES,
    }

