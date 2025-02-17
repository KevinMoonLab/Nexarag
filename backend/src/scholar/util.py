import time

class RateLimitExceededError(Exception):
    """Custom exception for rate limit errors."""
    pass

def retry(
    func,
    *args,
    max_retries=6,
    base_delay=1,
    max_delay=32,
    cb=None,
    **kwargs
):
    """
    Retries a function with exponential backoff.

    Args:
        func: A callable that may raise an exception.
        *args: Variable number of positional arguments to pass to the function.
        max_retries (int): Maximum number of retries before giving up. Defaults to 6.
        base_delay (float): Initial delay in seconds. Defaults to 1.
        max_delay (float): Maximum delay in seconds. Defaults to 32.
        **kwargs: Variable number of keyword arguments to pass to the function.

    Returns:
        The result of the function if successful.

    Raises:
        The last exception raised if all retries fail.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except RateLimitExceededError as e:
            if attempt == max_retries:
                cb(e)
                raise 
            else:
                delay = min(base_delay * 2**(attempt - 1), max_delay)
                time.sleep(delay)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

async def retry_async(
    func,
    *args,
    max_retries=6,
    base_delay=1,
    max_delay=32,
    cb=None,
    **kwargs
):
    """
    Retries a function with exponential backoff.

    Args:
        func: A callable that may raise an exception.
        *args: Variable number of positional arguments to pass to the function.
        max_retries (int): Maximum number of retries before giving up. Defaults to 6.
        base_delay (float): Initial delay in seconds. Defaults to 1.
        max_delay (float): Maximum delay in seconds. Defaults to 32.
        **kwargs: Variable number of keyword arguments to pass to the function.

    Returns:
        The result of the function if successful.

    Raises:
        The last exception raised if all retries fail.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except RateLimitExceededError as e:
            if attempt == max_retries:
                cb(e)
                raise 
            else:
                delay = min(base_delay * 2**(attempt - 1), max_delay)
                time.sleep(delay)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise