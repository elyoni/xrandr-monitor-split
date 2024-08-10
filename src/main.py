#!/usr/bin/env python3
import os
import typer
from rich import print
from rich.prompt import Confirm
from src.xrandr import XRandr
from src.config import parse_yaml_to_tree, verify_tree, yaml_data_example
from pathlib import Path
import subprocess

app = typer.Typer(
    context_settings=dict(help_option_names=["-h", "--help"]),
    no_args_is_help=True,
)
config_app = typer.Typer(no_args_is_help=True)
app.add_typer(config_app, name="configs")

CONFIG_DIR = Path("~/.config/x-screen-split").expanduser()
if not CONFIG_DIR.exists():
    CONFIG_DIR.mkdir(parents=True)
DEFAULT_CONFIG = CONFIG_DIR / "configs.yaml"
if not DEFAULT_CONFIG.exists():
    with open(DEFAULT_CONFIG, "w") as file:
        file.write(yaml_data_example)


def complete_configs_list():
    files = []
    for file in os.listdir(CONFIG_DIR):
        if file.endswith("yaml") or file.endswith("yml"):
            files.append(file)

    configs_list = []
    if len(files) == 0:
        return configs_list

    for conf_file in files:
        try:
            configs_list.append(conf_file.split(".")[0])
        except IndexError:
            print(f"Failed to get the profile name from the file: {conf_file}")
    return configs_list


# Function to split primary monitor based on config file
@app.command()
def split(
    config_file: str = typer.Argument(
        "configs",
        help="Name of the config file to print",
        autocompletion=complete_configs_list,
    )
):
    config_file = f"{config_file}.yaml"
    config_path = CONFIG_DIR / config_file
    if not config_path.exists():
        print(
            f"[bold red]Config file {config_file} not found in {CONFIG_DIR}[/bold red]"
        )
        raise typer.Exit(code=1)

    with open(config_path, "r") as file:
        yaml_data = file.read()

    tree = parse_yaml_to_tree(yaml_data)
    if verify_tree(tree):
        xrandr = XRandr()
        xrandr.split_primary_monitor(tree)
    else:
        print("[bold red]The tree is invalid.[/bold red]")


# Function to restore the primary monitor to the original state
@app.command()
def restore():
    xrandr = XRandr()
    xrandr.restore_primary_monitor()
    print("[green]Primary monitor restored to original state.[/green]")


# Function to verify the tree in the config file
@config_app.command()
def verify(
    config_file: str = typer.Argument(
        "configs",
        help="Name of the config file to verify",
        autocompletion=complete_configs_list,
    )
):
    config_file = f"{config_file}.yaml"
    config_path = CONFIG_DIR / config_file
    if not config_path.exists():
        print(
            f"[bold red]Config file {config_file} not found in {CONFIG_DIR}[/bold red]"
        )
        raise typer.Exit(code=1)

    with open(config_path, "r") as file:
        yaml_data = file.read()

    tree = parse_yaml_to_tree(yaml_data)
    if verify_tree(tree):
        print("[green]The tree is valid.[/green]")
    else:
        print("[bold red]The tree is invalid.[/bold red]")


@config_app.command()
def edit(
    config_file: str = typer.Argument(
        "configs",
        help="Name of the config file to edit",
        autocompletion=complete_configs_list,
    )
):
    config_file = f"{config_file}.yaml"
    config_path = CONFIG_DIR / config_file
    if not config_path.exists():
        print(
            f"[bold red]Config file {config_file} not found in {CONFIG_DIR}[/bold red]"
        )
        raise typer.Exit(code=1)

    editor = os.getenv(
        "EDITOR", "nano"
    )  # Use the system default editor or 'nano' as fallback
    subprocess.run([editor, config_path])


# Create a new configuration file
@config_app.command()
def new(config_file: str):
    config_file = f"{config_file}.yaml"
    config_path = CONFIG_DIR / config_file
    if config_path.exists():
        print(f"[bold yellow]Config file {config_file} already exists.[/bold yellow]")
    else:
        with open(config_path, "w") as file:
            file.write(yaml_data_example)
        print(f"[green]Config file {config_file} created.[/green]")


# Print the contents of a configuration file
@config_app.command(name="print")
def print_conf(
    config_file: str = typer.Argument(
        "configs",
        help="Name of the config file to print",
        autocompletion=complete_configs_list,
    )
):
    config_file = f"{config_file}.yaml"
    config_path = CONFIG_DIR / config_file
    if not config_path.exists():
        print(
            f"[bold red]Config file {config_file} not found in {CONFIG_DIR}[/bold red]"
        )
        raise typer.Exit(code=1)

    with open(config_path, "r") as file:
        content = file.read()
        print(f"[bold green]Contents of {config_file}:[/bold green]\n{content}")


# Delete a configuration file
@config_app.command()
def delete(
    config_file: str = typer.Argument(
        "configs",
        help="Name of the config file to print",
        autocompletion=complete_configs_list,
    )
):
    config_file = f"{config_file}.yaml"
    config_path = CONFIG_DIR / config_file
    if not config_path.exists():
        print(
            f"[bold red]Config file {config_file} not found in {CONFIG_DIR}[/bold red]"
        )
        raise typer.Exit(code=1)

    with open(config_path, "r") as file:
        content = file.read()

    print(f"[bold yellow]Contents of {config_file}:[/bold yellow]\n{content}")
    confirm = Confirm.ask(
        "[bold red]Are you sure you want to delete this file?[/bold red]"
    )
    if confirm:
        config_path.unlink()
        print(f"[green]Config file {config_file} deleted.[/green]")


def main():
    app()


if __name__ == "__main__":
    app()
