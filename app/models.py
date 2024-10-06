import datetime
from dataclasses import dataclass

from fasthtml import ft


@dataclass
class Question:
    question: str
    created_at: datetime.datetime

    def __ft__(self):
        return ft.Tr(
            ft.Td(self.question),
            ft.Td(self.created_at),
            hx_post="/ask",
            hx_vals={"question": self.question},
        )
