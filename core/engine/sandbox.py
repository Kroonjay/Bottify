from core.worker import bottify_worker


@bottify_worker.task(acks_late=True)
def test_task(word: str) -> str:
    return f"Test Task Resturn {str(word)}"
