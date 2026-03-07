"""Joke skill – a built-in collection of clean, family-friendly jokes.

Covers the "Entertainment" and "Personal Development" categories.
Pure Python, no external libraries.

Supported actions
-----------------
random          Return a random joke.
by_category     Return a random joke from a specific category.
list_categories List available joke categories.
setup           Return just the setup of a random joke (for testing).
pun             Return a random pun.
"""

from __future__ import annotations

import secrets

_JOKES: list[dict[str, str]] = [
    # Programming
    {"setup": "Why do programmers prefer dark mode?",
     "punchline": "Because light attracts bugs!", "category": "programming"},
    {"setup": "Why did the programmer quit his job?",
     "punchline": "Because he didn't get arrays!", "category": "programming"},
    {"setup": "How many programmers does it take to change a light bulb?",
     "punchline": "None — that's a hardware problem.", "category": "programming"},
    {"setup": "Why do Java developers wear glasses?",
     "punchline": "Because they don't C#!", "category": "programming"},
    {"setup": "A SQL query walks into a bar, walks up to two tables and asks…",
     "punchline": "'Can I JOIN you?'", "category": "programming"},
    {"setup": "Why do Python programmers have low self esteem?",
     "punchline": "Because they're constantly comparing themselves to others!", "category": "programming"},

    # Science
    {"setup": "I would tell you a chemistry joke, but I know I wouldn't get a reaction.",
     "punchline": "(It was sodium funny.)", "category": "science"},
    {"setup": "Why can't you trust atoms?",
     "punchline": "Because they make up everything!", "category": "science"},
    {"setup": "What do you call an acid with attitude?",
     "punchline": "A-mean-o acid!", "category": "science"},

    # Math
    {"setup": "Why was the equal sign so humble?",
     "punchline": "Because it knew it wasn't less than or greater than anyone else.", "category": "math"},
    {"setup": "Why was the math book sad?",
     "punchline": "It had too many problems.", "category": "math"},
    {"setup": "What do you call a number that can't keep still?",
     "punchline": "A roamin' numeral!", "category": "math"},

    # Food
    {"setup": "Why did the scarecrow win an award?",
     "punchline": "Because he was outstanding in his field!", "category": "general"},
    {"setup": "What do you call fake spaghetti?",
     "punchline": "An impasta!", "category": "food"},
    {"setup": "Why did the banana go to the doctor?",
     "punchline": "It wasn't peeling well!", "category": "food"},

    # Animals
    {"setup": "What do you call a sleeping dinosaur?",
     "punchline": "A dino-snore!", "category": "animals"},
    {"setup": "Why don't elephants use computers?",
     "punchline": "Because they're afraid of the mouse!", "category": "animals"},
    {"setup": "What do you call a fish without eyes?",
     "punchline": "A fsh!", "category": "animals"},

    # General
    {"setup": "I'm reading a book on anti-gravity.",
     "punchline": "It's impossible to put down!", "category": "general"},
    {"setup": "Why don't scientists trust atoms?",
     "punchline": "Because they make up everything!", "category": "general"},
    {"setup": "What do you call someone with no body and no nose?",
     "punchline": "Nobody knows!", "category": "general"},
    {"setup": "Did you hear about the claustrophobic astronaut?",
     "punchline": "He just needed a little space!", "category": "general"},
    {"setup": "Why can't Elsa have a balloon?",
     "punchline": "Because she'll let it go!", "category": "general"},
]

_PUNS: list[str] = [
    "I used to hate facial hair, but then it grew on me.",
    "Time flies like an arrow. Fruit flies like a banana.",
    "I'm on a seafood diet. I see food and I eat it.",
    "I stayed up all night to see where the sun went, then it dawned on me.",
    "The bicycle couldn't stand on its own — it was two-tired.",
    "I tried to make a pencil with an eraser, but it was pointless.",
    "I used to be a banker, but I lost interest.",
    "Never trust an atom. They make up everything.",
    "A boiled egg in the morning is really hard to beat.",
    "I'm great at multitasking. I can waste time, be unproductive, and procrastinate all at once.",
]


class JokeSkill:
    """Deliver a built-in collection of clean, family-friendly jokes."""

    name = "joke"
    description = (
        "Tell jokes from a built-in collection. "
        "Supported actions: 'random'; 'by_category' (category); "
        "'list_categories'; 'setup'; 'pun'."
    )

    def run(self, action: str, category: str = "") -> str:
        """
        Tell a joke.

        Parameters
        ----------
        action:
            One of ``"random"``, ``"by_category"``,
            ``"list_categories"``, ``"setup"``, ``"pun"``.
        category:
            Joke category for ``"by_category"``.

        Returns
        -------
        str
            The joke or error message prefixed with ``"Error: "``.
        """
        action = action.strip().lower()

        if action == "random":
            return self._format(secrets.choice(_JOKES))
        if action == "by_category":
            return self._by_category(category)
        if action == "list_categories":
            cats = sorted(set(j["category"] for j in _JOKES))
            return "Categories: " + ", ".join(cats)
        if action == "setup":
            j = secrets.choice(_JOKES)
            return j["setup"]
        if action == "pun":
            return secrets.choice(_PUNS)
        return (
            f"Error: unknown action {action!r}. "
            "Use random, by_category, list_categories, setup, or pun."
        )

    @staticmethod
    def _format(joke: dict[str, str]) -> str:
        return f"{joke['setup']}\n— {joke['punchline']}"

    @staticmethod
    def _by_category(category: str) -> str:
        if not category:
            return "Error: category is required for by_category"
        cat = category.lower().strip()
        matches = [j for j in _JOKES if j["category"] == cat]
        if not matches:
            cats = sorted(set(j["category"] for j in _JOKES))
            return f"Error: no jokes in category {category!r}. Available: {', '.join(cats)}"
        return JokeSkill._format(secrets.choice(matches))
