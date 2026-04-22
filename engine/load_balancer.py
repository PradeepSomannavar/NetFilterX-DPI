"""
Simple round-robin load balancer for distributing flows across worker threads.
Python port of load_balancer.cpp / load_balancer.h.
"""

import threading
from typing import List, Callable, Any


class LoadBalancer:
    """
    Distributes work items across N worker slots using round-robin assignment.
    Mirrors the C++ LoadBalancer class.
    """

    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self._counter = 0
        self._lock = threading.Lock()

    def assign(self, item: Any) -> int:
        """Return the worker index this item should be assigned to."""
        with self._lock:
            idx = self._counter % self.num_workers
            self._counter += 1
        return idx

    def route(self, flow_key: str) -> int:
        """Deterministically assign a flow key to a worker by hash."""
        return hash(flow_key) % self.num_workers
