from fasthtml.common import fast_app, serve

app, rt = fast_app()


@rt("/")
def home():
    return "Hello, world!"


if __name__ == "__main__":
    serve()
