import ollama
from fasthtml import ft
from fasthtml.common import fast_app, serve

from app import utils

app, rt = fast_app(on_startup=[utils.pull_llm])


@rt("/")
def home():
    return ft.Main(
        ft.Form(
            ft.Label("Question", ft.Input(name="question")),
            ft.Button("Submit"),
            hx_post="/ask",
        ),
        cls="container",
    )


@rt("/ask")
def post(question: str):
    return (
        ft.Label("Question", ft.Input(name="question", value=question, disabled=True)),
        ft.Label(
            "Answer",
            ft.Input(
                name="answer",
                value=ollama.generate(model="gemma2:2b", prompt=question)["response"],
                disabled=True,
            ),
        ),
        ft.Button("Reset", hx_get="/", hx_target="body"),
    )


if __name__ == "__main__":
    serve()
