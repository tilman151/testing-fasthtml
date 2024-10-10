import os

import ollama
from fasthtml import ft, pico
from fasthtml.common import fast_app, serve

from app import utils, database


bootstrap_icons = (
    "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css"
)
bootstrap_icons_link = ft.Link(rel="stylesheet", href=bootstrap_icons)
database_url = os.environ.get("APP_DATABASE_URL", "sqlite:///history.db")
app, rt = fast_app(
    hdrs=(bootstrap_icons_link,),
    on_startup=[utils.pull_llm, lambda: database.connect(database_url), database.init],
    on_shutdown=[database.disconnect],
)


@rt("/")
def home():
    return ft.Main(
        ft.Form(
            ft.Label(
                "Question",
                pico.Group(
                    ft.Input(name="question", required=True),
                    ft.Button(
                        id="history-button",
                        cls="bi bi-clock-history",
                        type="button",
                        hx_get="/history",
                        hx_target="#history-container",
                    ),
                ),
            ),
            ft.Span(id="history-container"),
            ft.Button("Ask"),
            id="question-form",
            hx_post="/ask",
            hx_validate=True,
        ),
        cls="container",
    )


@rt("/ask")
def post(question: str):
    answer = ollama.generate(model="llama3.2:1b", prompt=question)["response"]
    database.append_to_history(question, answer)

    return (
        ft.Label("Question", ft.Input(name="question", value=question, disabled=True)),
        ft.Label("Answer", ft.Input(name="answer", value=answer, disabled=True)),
        ft.Button("Reset", hx_get="/", hx_target="body"),
    )


@rt("/history")
def get():
    return ft.Table(
        ft.Thead(ft.Tr(ft.Th("Question"), ft.Th("Asked at"))),
        ft.Tbody(*database.get_recent_questions(), hx_target="#question-form"),
    ), ft.Button(
        id="history-button",
        cls="bi bi-clock-history",
        type="button",
        hx_get="/",
        hx_target="body",
        hx_swap_oob="outerHTML",
    )


if __name__ == "__main__":
    serve()
