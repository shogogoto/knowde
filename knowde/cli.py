"""cli root."""
import typer

cli = typer.Typer()

__version__ = "0.0.0"

@cli.command()
def main(name: str) -> None:
    """Hello world."""
    typer.echo(f"hello {name}")
    typer.echo(f"version={__version__}")


if __name__ == "__main__":
    cli()
