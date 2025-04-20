from pathlib import Path
from typing import Annotated
import rich
import rich.markdown
import typer

from mcp_dic.database.sqlite import SQLiteDatabase
from mcp_dic.dictionary.lookup import get_inflection_by_type, lookup_stem, lookup_stem_by_surface_form


def create_app():
  app = typer.Typer(
    name="mcp_dic.cli",
    help="MCP Dictionary CLI",
    rich_markup_mode="rich",
  )

  @app.command()
  def stem(
    stem: Annotated[
      str,
      typer.Option(
        "-s",
        help="stem to lookup",
      ),
    ],
    database_path: Annotated[
      str,
      typer.Option(
        "-d",
        exists=True,
        dir_okay=False,
        resolve_path=True,
      ),
    ] = "dictionary.sqlite3",
  ):

    if not Path(database_path).exists():
      rich.print(
        rich.markdown.Markdown(
          f"Database file not found: {database_path}",
        ),
      )
      raise typer.Exit(1)

    with SQLiteDatabase(database_path) as db:
      stems = lookup_stem(
        db=db,
        stem=stem,
      )

    formatted = '\n\n---\n'.join(stem.format_stem(human_readable=True) for stem in stems)

    if not formatted:
      formatted = "No results found."

    rich.print(rich.markdown.Markdown(formatted))

  @app.command('infer-stems')
  def get_stem_by_surface_form(
    surface_form: Annotated[
      str,
      typer.Option(
        "-s",
        help="surface form to lookup",
      ),
    ],
    database_path: Annotated[
      str,
      typer.Option(
        "-d",
        exists=True,
        dir_okay=False,
        resolve_path=True,
      ),
    ] = "dictionary.sqlite3",
  ):
    if not Path(database_path).exists():
      rich.print(
        rich.markdown.Markdown(
          f"Database file not found: {database_path}",
        ),
      )
      raise typer.Exit(1)

    with SQLiteDatabase(database_path) as db:
      stems = lookup_stem_by_surface_form(
        db=db,
        surface_form=surface_form,
      )

    formatted = '\n\n---\n'.join(stem.format_stem(human_readable=True) for stem in stems)

    if not formatted:
      formatted = "No results found."

    rich.print(rich.markdown.Markdown(formatted))

  @app.command('inflection')
  def get_inflection(
    stem: Annotated[
      str,
      typer.Option(
        "-s",
        help="stem to lookup",
      ),
    ],
    inflection_types: Annotated[
      list[str],
      typer.Option(
        "-i",
        help="inflection types to lookup",
        show_default=False,
      ),
    ],
    database_path: Annotated[
      str,
      typer.Option(
        "-d",
        exists=True,
        dir_okay=False,
        resolve_path=True,
      ),
    ] = "dictionary.sqlite3",
  ):
    if not Path(database_path).exists():
      rich.print(
        rich.markdown.Markdown(
          f"Database file not found: {database_path}",
        ),
      )
      raise typer.Exit(1)

    with SQLiteDatabase(database_path) as db:
      inflections = get_inflection_by_type(
        db=db,
        stem=stem,
        inflection_types=inflection_types,
      )

    formatted = '\n'.join(f'- {i}' for i in inflections)

    if not formatted:
      formatted = "No results found."

    rich.print(rich.markdown.Markdown(formatted))

  return app
