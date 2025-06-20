from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import Dict, List
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = {}
        
    def check_rate_limit(self, ip: str) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old requests
        if ip not in self.requests:
            self.requests[ip] = []
        self.requests[ip] = [req_time for req_time in self.requests[ip] if req_time > minute_ago]
        
        # Check if rate limit is exceeded
        if len(self.requests[ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later."
            )
        
        # Add new request
        self.requests[ip].append(now)
        return True