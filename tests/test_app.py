import lxml.html
import pytest
from playwright.sync_api import Page

from app import database


@pytest.mark.integration
def test_ask_mocked_answer(client, mocker):
    """It should return HTML with the question and the mocked answer."""
    mock_generate = mocker.patch("ollama.generate")
    mock_generate.return_value = {"response": "answer0"}

    response = client.post("/ask", data={"question": "question0"})

    assert response.status_code == 200
    html = lxml.html.fromstring(response.text)
    assert html.xpath("//input[@name='question' and @disabled and @value='question0']")
    assert html.xpath("//input[@name='answer' and @disabled and @value='answer0']")


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
    html = lxml.html.fromstring(response.text)
    assert html.xpath("//table")
    assert html.xpath("//table/thead/tr/th[text()='Question']")
    assert html.xpath("//table/thead/tr/th[text()='Asked at']")
    assert len(html.xpath("//table/tbody/tr")) == 0


@pytest.mark.integration
def test_history(client):
    """It should return a table with the most recent questions."""
    database.append_to_history("question0", "answer0")
    database.append_to_history("question1", "answer1")

    response = client.get("/history")

    assert response.status_code == 200
    html = lxml.html.fromstring(response.text)
    assert html.xpath("//table")
    assert html.xpath("//table/thead/tr/th[text()='Question']")
    assert html.xpath("//table/thead/tr/th[text()='Asked at']")
    assert len(html.xpath("//table/tbody/tr")) == 2


@pytest.mark.integration
def test_history_swaps_button(client):
    """It should swap the history button oob."""
    response = client.get("/history")

    assert response.status_code == 200
    html = lxml.html.fromstring(response.text)
    assert html.xpath("//button[@hx-swap-oob='outerHTML' and @id='history-button']")


@pytest.mark.e2e
def test_ask_question(server, page: Page):
    """When I ask a question, it should show the question and answer."""
    page.goto("http://localhost:5001")
    page.get_by_label("Question").type("How are you doing?")
    page.get_by_text("Ask").click()
    page.wait_for_selector("input[name='answer']")

    assert page.get_by_label("Question").input_value() == "How are you doing?"
    assert page.get_by_label("Answer").input_value()
    assert page.get_by_text("Reset").is_visible()


@pytest.mark.e2e
def test_ask_question_history(server, page: Page):
    """When I ask a question,
    I should be able to ask again from the history by clicking it."""
    page.goto("http://localhost:5001")
    page.get_by_label("Question").type("How are you doing?")
    page.get_by_text("Ask").click()
    page.wait_for_selector("input[name='answer']")
    page.get_by_text("Reset").click()
    page.wait_for_selector("#history-button")

    page.locator("css=#history-button").click()
    page.wait_for_selector("table")
    assert page.locator("css=table tbody tr").count() == 1
    page.locator("css=table tbody tr").click()
    page.wait_for_selector("input[name='answer']")


@pytest.mark.e2e
def test_toggle_history(server, page: Page):
    """When I click the history button, I should be able to toggle the history."""
    page.goto("http://localhost:5001")
    page.locator("css=#history-button").click()
    page.wait_for_selector("table")
    page.locator("css=#history-button").click()

    assert page.locator("css=table").count() == 0
