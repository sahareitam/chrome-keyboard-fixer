import threading
import time
from flask import jsonify, request
from functools import wraps


class APILimiter:
    """
    API limiter that restricts concurrent API calls and implements rate limiting
    """

    def __init__(self, max_concurrent_calls=40):
        # Maximum allowed concurrent API calls
        self.max_concurrent_calls = max_concurrent_calls
        # Counter for active API calls
        self.active_calls = 0
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        # Dictionary to store request history by IP
        self.rate_limits = {}  # IP -> [timestamp, timestamp, ...]

    def _is_rate_limited(self, ip, max_per_minute=30):
        """
        Check if an IP address exceeds the rate limit

        Args:
            ip: Client IP address
            max_per_minute: Maximum allowed requests per minute

        Returns:
            True if rate limited, False otherwise
        """
        now = time.time()

        # Clean up old records (older than one minute)
        if ip in self.rate_limits:
            self.rate_limits[ip] = [t for t in self.rate_limits[ip] if now - t < 60]
        else:
            self.rate_limits[ip] = []

        # Check if limit reached
        if len(self.rate_limits[ip]) >= max_per_minute:
            return True

        # Add new timestamp to history
        self.rate_limits[ip].append(now)
        return False

    def limit_api(self, max_calls_per_minute=30):
        """
        Decorator to limit API calls

        Args:
            max_calls_per_minute: Maximum requests per minute per IP

        Returns:
            Decorated function
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Get client IP address
                ip = request.remote_addr
                if request.headers.get('X-Forwarded-For'):
                    ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()

                # Check rate limiting by IP
                if self._is_rate_limited(ip, max_calls_per_minute):
                    return jsonify({
                        'error': 'Too many requests. Please try again later.',
                        'status': 429
                    }), 429

                # Check system load
                with self.lock:
                    if self.active_calls >= self.max_concurrent_calls:
                        return jsonify({
                            'error': 'Server is busy. Please try again later.',
                            'status': 503
                        }), 503
                    self.active_calls += 1

                # Execute the function
                try:
                    return func(*args, **kwargs)
                finally:
                    # Decrease active calls counter
                    with self.lock:
                        self.active_calls -= 1

            return wrapper

        return decorator


def initialize_api_limiter(app, max_concurrent_calls=40):
    """
    Initialize the API limiter

    Args:
        app: Flask application
        max_concurrent_calls: Maximum concurrent API calls

    Returns:
        Initialized API limiter instance
    """
    return APILimiter(max_concurrent_calls=max_concurrent_calls)