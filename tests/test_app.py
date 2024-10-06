import re

import pytest
import htmlmin

from app import database


@pytest.mark.integration
def test_ask_mocked_answer(client, mocker):
    """It should return HTML with the question and the mocked answer."""
    mock_generate = mocker.patch("ollama.generate")
    mock_generate.return_value = {"response": "answer0"}

    response = client.post("/ask", data={"question": "question0"})

    assert response.status_code == 200
    assert '<input name="question" value="question0" disabled>' in response.text
    assert '<input name="answer" value="answer0" disabled>' in response.text


@pytest.mark.integration
def test_ask_question_added_to_history(client, mocker):
    """It should add the question and answer to the history."""
    mock_generate = mocker.patch("ollama.generate")
    mock_generate.return_value = {"response": "answer0"}

    client.post("/ask", data={"question": "question0"})

    history = database.get_recent_questions()
    assert len(history) == 1
    assert history[0].question == "question0"


@pytest.mark.integration
def test_history_empty(client):
    """It should return a table with header and empty body."""
    response = client.get("/history")

    assert response.status_code == 200
    html = htmlmin.minify(response.text, remove_empty_space=True)
    assert re.search("<table>.+?</table>", html)
    assert "<thead><tr><th>Question</th><th>Asked at</th></tr></thead>" in html
    assert "<tbody hx-target=#question-form></tbody>" in html


@pytest.mark.integration
def test_history(client):
    """It should return a table with the most recent questions."""
    database.append_to_history("question0", "answer0")
    database.append_to_history("question1", "answer1")

    response = client.get("/history")

    assert response.status_code == 200
    html = htmlmin.minify(response.text, remove_empty_space=True)
    assert re.search("<table>.+?", html)
    assert "<thead><tr><th>Question</th><th>Asked at</th></tr></thead>" in html
    assert re.search(
        "<tbody hx-target=#question-form>(<tr.+?>.+?</tr>){2}</tbody>", html
    )


@pytest.mark.integration
def test_history_swaps_button(client):
    """It should swap the history button oob."""
    response = client.get("/history")

    assert response.status_code == 200
    html = htmlmin.minify(response.text, remove_empty_space=True)
    assert re.search(
        "<button.+hx-swap-oob=outerHTML.+id=history-button.*>.*?</button>", html
    )


@pytest.mark.e2e
def test_e2e_dummy(server):
    assert True
