import click
import asyncio
from typing import Optional

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """MCP CLI Assistant - Foundation Tool"""
    pass

@cli.command()
@click.option("--name", default="World", help="Name to greet")
def greet(name: str):
    """Simple greeting command"""
    click.echo(f"👋 Hello, {name}!")

@cli.command()
@click.option("--prompt", required=True, help="Your prompt for the LLM")
@click.option("--model", default="gpt-3.5-turbo", help="LLM model to use")
def ask(prompt: str, model: str):
    """Send prompt to LLM (Project 1 preview)"""
    click.echo(f"🤔 Processing: {prompt}")
    click.echo(f"📡 Model: {model}")
    # In Project 1, we'll add actual API call here
    click.echo("✅ Response will appear here after API integration")

@cli.command()
def config():
    """Show current configuration"""
    config = {
        "api_key": "********",
        "model": "gpt-3.5-turbo",
        "timeout": 30
    }
    click.echo("⚙️  Configuration:")
    for key, value in config.items():
        click.echo(f"   {key}: {value}")

@cli.command()
@click.argument("task")
def run(task: str):
    """Run a task through MCP"""
    click.echo(f"🚀 Running task: {task}")
    # Async task execution
    asyncio.run(execute_task(task))

async def execute_task(task: str):
    await asyncio.sleep(1)
    click.echo(f"✅ Task '{task}' completed")

if __name__ == "__main__":
    cli()