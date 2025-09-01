from __future__ import annotations
from typing import List, Optional
from collections import deque
from .models import TriageCase


class CounselorQueue:
    def __init__(self):
        self._q: deque[TriageCase] = deque()

    def enqueue(self, case: TriageCase):
        self._q.append(case)

    def dequeue(self) -> Optional[TriageCase]:
        if self._q:
            return self._q.popleft()
        return None

    def list(self) -> List[TriageCase]:
        return list(self._q)


queue = CounselorQueue()
