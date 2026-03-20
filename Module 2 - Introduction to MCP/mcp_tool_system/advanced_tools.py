# advanced_tools.py
import asyncio
import random
from typing import Dict, Any, List
from models import ToolParameter, ToolParameterType
from tools import tool_registry


# ============== Calculator Tools ==============

def calculator_add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b


def calculator_subtract(a: float, b: float) -> float:
    """Subtract b from a"""
    return a - b


def calculator_multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return a * b


def calculator_divide(a: float, b: float) -> float:
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def calculator_power(base: float, exponent: float) -> float:
    """Calculate base raised to exponent"""
    return base ** exponent


# Register calculator tools
for name, func, desc in [
    ("calc_add", calculator_add, "Add two numbers"),
    ("calc_subtract", calculator_subtract, "Subtract second number from first"),
    ("calc_multiply", calculator_multiply, "Multiply two numbers"),
    ("calc_divide", calculator_divide, "Divide first number by second"),
    ("calc_power", calculator_power, "Calculate power of a number"),
]:
    tool_registry.register(
        name=name,
        description=desc,
        parameters={
            "a": ToolParameter(
                type=ToolParameterType.NUMBER,
                description="First number",
                required=True
            ),
            "b": ToolParameter(
                type=ToolParameterType.NUMBER,
                description="Second number",
                required=True
            )
        },
        handler=func
    )


# ============== Weather Tools ==============

class WeatherData:
    """Simulated weather data"""
    
    CITIES = {
        "new york": {"temp": 22, "condition": "Sunny", "humidity": 45},
        "london": {"temp": 15, "condition": "Cloudy", "humidity": 70},
        "tokyo": {"temp": 25, "condition": "Rainy", "humidity": 80},
        "paris": {"temp": 18, "condition": "Partly Cloudy", "humidity": 55},
        "sydney": {"temp": 28, "condition": "Sunny", "humidity": 40},
    }
    
    @classmethod
    def get_weather(cls, city: str) -> Dict[str, Any]:
        city_lower = city.lower()
        if city_lower in cls.CITIES:
            return cls.CITIES[city_lower]
        # Generate random weather for unknown cities
        return {
            "temp": random.randint(10, 35),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]),
            "humidity": random.randint(30, 90)
        }


async def get_weather(city: str) -> Dict[str, Any]:
    """Get weather information for a city"""
    await asyncio.sleep(0.1)  # Simulate API call
    weather = WeatherData.get_weather(city)
    return {
        "city": city,
        "temperature_celsius": weather["temp"],
        "condition": weather["condition"],
        "humidity_percent": weather["humidity"]
    }


async def get_weather_forecast(city: str, days: int = 3) -> List[Dict[str, Any]]:
    """Get weather forecast for multiple days"""
    await asyncio.sleep(0.2)  # Simulate API call
    base_weather = WeatherData.get_weather(city)
    forecast = []
    
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "temperature_celsius": base_weather["temp"] + random.randint(-3, 3),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]),
            "humidity_percent": base_weather["humidity"] + random.randint(-10, 10)
        })
    
    return forecast


tool_registry.register(
    name="get_weather",
    description="Get current weather for a city",
    parameters={
        "city": ToolParameter(
            type=ToolParameterType.STRING,
            description="City name",
            required=True
        )
    },
    handler=get_weather
)

tool_registry.register(
    name="get_weather_forecast",
    description="Get weather forecast for multiple days",
    parameters={
        "city": ToolParameter(
            type=ToolParameterType.STRING,
            description="City name",
            required=True
        ),
        "days": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Number of days (default: 3)",
            required=False
        )
    },
    handler=get_weather_forecast
)


# ============== Text Summarizer Tools ==============

async def summarize_text(text: str, max_length: int = 100) -> str:
    """Summarize text to a maximum length"""
    await asyncio.sleep(0.1)  # Simulate processing
    
    if len(text) <= max_length:
        return text
    
    # Simple summarization (take first sentences)
    sentences = text.split('.')
    summary = ""
    
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + ". "
        else:
            break
    
    return summary.strip() + "..." if len(summary) < len(text) else summary.strip()


async def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """Extract key words from text"""
    await asyncio.sleep(0.1)
    
    # Simple keyword extraction (remove common words)
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
                  "being", "have", "has", "had", "do", "does", "did", "will",
                  "would", "could", "should", "may", "might", "must", "shall"}
    
    words = text.lower().replace(".", "").replace(",", "").split()
    keywords = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Return most frequent keywords
    from collections import Counter
    keyword_counts = Counter(keywords)
    return [word for word, count in keyword_counts.most_common(max_keywords)]


async def count_words(text: str) -> Dict[str, int]:
    """Count words, characters, and sentences in text"""
    await asyncio.sleep(0.05)
    
    words = text.split()
    sentences = text.split('.')
    
    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": len([s for s in sentences if s.strip()])
    }


tool_registry.register(
    name="summarize_text",
    description="Summarize text to a maximum length",
    parameters={
        "text": ToolParameter(
            type=ToolParameterType.STRING,
            description="Text to summarize",
            required=True
        ),
        "max_length": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Maximum length of summary",
            required=False
        )
    },
    handler=summarize_text
)

tool_registry.register(
    name="extract_keywords",
    description="Extract key words from text",
    parameters={
        "text": ToolParameter(
            type=ToolParameterType.STRING,
            description="Text to analyze",
            required=True
        ),
        "max_keywords": ToolParameter(
            type=ToolParameterType.NUMBER,
            description="Maximum number of keywords",
            required=False
        )
    },
    handler=extract_keywords
)

tool_registry.register(
    name="count_words",
    description="Count words, characters, and sentences in text",
    parameters={
        "text": ToolParameter(
            type=ToolParameterType.STRING,
            description="Text to analyze",
            required=True
        )
    },
    handler=count_words
)