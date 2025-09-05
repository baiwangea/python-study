import typer

app = typer.Typer()

@app.command()
def greet(name: str):
    """向用户问好"""
    typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()