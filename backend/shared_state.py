# This file holds shared state to avoid circular imports.

# For idempotency: Idempotency-Key -> { "status": int, "response": dict }
idem_store = {}

# For rate limiting: ip -> { "count": int, "timestamp": float }
rate_limit_store = {}
