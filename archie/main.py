import typer
from archie.database import initialize_db


app = typer.Typer()


@app.command()
def bootsrap():
    initialize_db()


if __name__ == "__main__":
    app()
