import nox


@nox.session(python=["3.13"], venv_backend="uv")
def run(session: nox.Session) -> None:
    # Install dependencies
    session.install("-r", "requirements.txt")
    session.install("-r", "requirements-dev.txt")

    # Run tests
    session.run("coverage", "run", "-m", "pytest", *session.posargs)
    session.run("coverage", "report", "-m")
    session.run("coverage", "html")
