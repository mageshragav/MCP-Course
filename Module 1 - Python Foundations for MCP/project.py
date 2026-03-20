import click
import asyncio
import httpx
import os
from typing import Optional
from datetime import datetime
from environs import env

env.read_env()


# step 1 : config load

class Config:
    """Centralized configuration"""
    API_KEY: str = env.str("OPENAI_API_KEY", "")
    BASE_URL: str = env.str("BASE_URL", "https://api.openai.com/v1")
    DEFAULT_MODEL: str = env.str("DEFAULT_MODEL", "gpt-3.5-turbo")
    TIMEOUT: int = env.int("TIMEOUT", 30)
    MAX_TOKENS: int = env.int("MAX_TOKENS", 1000)

# step 2 : LLM client
class LLMClient:
    """Async LLM API Client"""

    def __init__(self, api_key: str, base_url: str = Config.BASE_URL):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def send_prompt(
        self,
        prompt: str,
        model: str = Config.DEFAULT_MODEL,
        temperature: float = 0.7,
    ) -> str:
        """Send prompt to LLM and get response"""
        async with httpx.AsyncClient(timeout=Config.TIMEOUT) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful AI assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": temperature,
                        "max_tokens": Config.MAX_TOKENS,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPError as e:
                raise Exception(f"API Error: {str(e)}")
            except Exception as e:
                raise Exception(f"Request failed: {str(e)}")

# step 3 : CLI command
@click.group()
@click.version_option(version="1.0.0", prog_name="ai-cli")
def cli():
    """🤖 AI CLI Assistant - Your LLM Command Line Tool"""
    pass


@cli.command()
@click.option("--prompt", "-p", required=True, help="Your prompt for the AI")
@click.option("--model", "-m", default=Config.DEFAULT_MODEL, help="LLM model")
@click.option("--temperature", "-t", default=0.7, help="Temperature (0-1)")
@click.option("--output", "-o", default=None, help="Save response to file")
def ask(prompt: str, model: str, temperature: float, output: Optional[str]):
    """Send a prompt to the AI and get response"""

    # Validate API key
    if not Config.API_KEY:
        click.echo("❌ Error: OPENAI_API_KEY not set!")
        click.echo("💡 Set it: export OPENAI_API_KEY='your-key'")
        return

    click.echo(f"🤔 Processing your prompt...")
    click.echo(f"📡 Model: {model}")
    click.echo(f"🌡️  Temperature: {temperature}")
    click.echo("-" * 50)

    async def get_response():
        client = LLMClient(Config.API_KEY)
        return await client.send_prompt(prompt, model, temperature)

    try:
        # Show spinner while waiting
        with click.progressbar(length=100, label="Thinking", show_eta=False) as bar:
            async def fetch():
                response = await get_response()
                bar.update(100)
                return response

            response = asyncio.run(fetch())

        # Display response
        click.echo("\n" + "=" * 50)
        click.echo(click.style("🤖 AI Response:", fg="green", bold=True))
        click.echo("=" * 50)
        click.echo(response)
        click.echo("=" * 50)

        # Save to file if requested
        if output:
            with open(output, "w") as f:
                f.write(f"# AI Response - {datetime.now()}\n\n{response}")
            click.echo(f"💾 Response saved to: {output}")

        # Save to history
        save_to_history(prompt, response)

    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))


@cli.command()
def history():
    """Show conversation history"""
    history_file = ".ai_cli_history.json"
    if os.path.exists(history_file):
        import json

        with open(history_file, "r") as f:
            history = json.load(f)
        click.echo(f"\n📜 History ({len(history)} entries):")
        for i, entry in enumerate(history[-5:], 1):  # Show last 5
            click.echo(f"\n{i}. {entry['timestamp']}")
            click.echo(f"   Q: {entry['prompt'][:50]}...")
            click.echo(f"   A: {entry['response'][:50]}...")
    else:
        click.echo("📭 No history found")


@cli.command()
def config():
    """Show current configuration"""
    click.echo("\n⚙️  Configuration:")
    click.echo(f"   API Key: {'********' if Config.API_KEY else 'NOT SET'}")
    click.echo(f"   Base URL: {Config.BASE_URL}")
    click.echo(f"   Default Model: {Config.DEFAULT_MODEL}")
    click.echo(f"   Timeout: {Config.TIMEOUT}s")
    click.echo(f"   Max Tokens: {Config.MAX_TOKENS}")


# ============== HELPER FUNCTIONS ==============
def save_to_history(prompt: str, response: str):
    """Save conversation to history file"""
    import json
    history_file = ".ai_cli_history.json"

    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)

    history.append({
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response
    })

    # Keep last 100 entries
    history = history[-100:]

    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)


# ============== ENTRY POINT ==============
if __name__ == "__main__":
    cli()