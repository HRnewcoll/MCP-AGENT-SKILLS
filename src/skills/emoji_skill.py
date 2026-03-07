"""Emoji skill – look up, search, and suggest emoji by name or keyword.

Covers the "Communication" and "CLI Utilities" categories.
Pure Python, no external libraries.

Supported actions
-----------------
find            Find emoji by name or keyword.
random          Return a random emoji.
list_categories List available emoji categories.
by_category     Return all emoji in a category.
info            Show details about a specific emoji by name.
"""

from __future__ import annotations

import secrets

_EMOJI_DB: list[dict[str, str]] = [
    # Faces & emotions
    {"emoji": "😀", "name": "grinning face", "keywords": "happy smile laugh", "category": "faces"},
    {"emoji": "😂", "name": "face with tears of joy", "keywords": "laugh cry funny lol", "category": "faces"},
    {"emoji": "🥹", "name": "face holding back tears", "keywords": "sad moved touched", "category": "faces"},
    {"emoji": "😍", "name": "smiling face with heart-eyes", "keywords": "love heart adore", "category": "faces"},
    {"emoji": "🤔", "name": "thinking face", "keywords": "think consider hmm", "category": "faces"},
    {"emoji": "😎", "name": "smiling face with sunglasses", "keywords": "cool sunglasses", "category": "faces"},
    {"emoji": "🥳", "name": "partying face", "keywords": "party celebrate birthday", "category": "faces"},
    {"emoji": "😭", "name": "loudly crying face", "keywords": "cry sob sad tears", "category": "faces"},
    {"emoji": "😤", "name": "face with steam from nose", "keywords": "angry frustrated mad", "category": "faces"},
    {"emoji": "🙄", "name": "face with rolling eyes", "keywords": "eye roll bored", "category": "faces"},
    {"emoji": "🤯", "name": "exploding head", "keywords": "mind blown shocked wow", "category": "faces"},
    {"emoji": "🥺", "name": "pleading face", "keywords": "pleading puppy eyes sad", "category": "faces"},
    # Nature
    {"emoji": "🌟", "name": "glowing star", "keywords": "star shining sparkle", "category": "nature"},
    {"emoji": "🌸", "name": "cherry blossom", "keywords": "flower pink spring japan", "category": "nature"},
    {"emoji": "🌊", "name": "water wave", "keywords": "wave ocean sea surf", "category": "nature"},
    {"emoji": "🔥", "name": "fire", "keywords": "fire hot flame burn", "category": "nature"},
    {"emoji": "⭐", "name": "star", "keywords": "star yellow", "category": "nature"},
    {"emoji": "🌈", "name": "rainbow", "keywords": "rainbow colorful pride", "category": "nature"},
    {"emoji": "❄️", "name": "snowflake", "keywords": "cold snow ice winter", "category": "nature"},
    {"emoji": "🌙", "name": "crescent moon", "keywords": "moon night sleep", "category": "nature"},
    # Animals
    {"emoji": "🐱", "name": "cat face", "keywords": "cat kitten meow pet", "category": "animals"},
    {"emoji": "🐶", "name": "dog face", "keywords": "dog puppy woof pet", "category": "animals"},
    {"emoji": "🦊", "name": "fox", "keywords": "fox animal cunning", "category": "animals"},
    {"emoji": "🦁", "name": "lion", "keywords": "lion king wild animal", "category": "animals"},
    {"emoji": "🐧", "name": "penguin", "keywords": "penguin bird cold ice", "category": "animals"},
    {"emoji": "🦋", "name": "butterfly", "keywords": "butterfly insect beautiful", "category": "animals"},
    {"emoji": "🐉", "name": "dragon", "keywords": "dragon fantasy fire", "category": "animals"},
    # Food
    {"emoji": "🍕", "name": "pizza", "keywords": "pizza food italian", "category": "food"},
    {"emoji": "🍔", "name": "hamburger", "keywords": "burger fast food", "category": "food"},
    {"emoji": "🍣", "name": "sushi", "keywords": "sushi japanese fish", "category": "food"},
    {"emoji": "🍦", "name": "soft ice cream", "keywords": "ice cream sweet dessert", "category": "food"},
    {"emoji": "☕", "name": "hot beverage", "keywords": "coffee tea hot drink", "category": "food"},
    {"emoji": "🎂", "name": "birthday cake", "keywords": "cake birthday celebrate", "category": "food"},
    {"emoji": "🍩", "name": "doughnut", "keywords": "donut sweet dessert", "category": "food"},
    # Activities
    {"emoji": "🎮", "name": "video game", "keywords": "gaming controller play", "category": "activities"},
    {"emoji": "📚", "name": "books", "keywords": "book read study learn", "category": "activities"},
    {"emoji": "🎵", "name": "musical note", "keywords": "music note song", "category": "activities"},
    {"emoji": "🏋️", "name": "person lifting weights", "keywords": "gym workout fitness strong", "category": "activities"},
    {"emoji": "🚀", "name": "rocket", "keywords": "rocket space launch fast", "category": "activities"},
    {"emoji": "🎨", "name": "artist palette", "keywords": "art paint color creative", "category": "activities"},
    {"emoji": "⚽", "name": "soccer ball", "keywords": "football soccer sport", "category": "activities"},
    # Symbols
    {"emoji": "❤️", "name": "red heart", "keywords": "love heart red", "category": "symbols"},
    {"emoji": "💯", "name": "hundred points", "keywords": "perfect 100 score", "category": "symbols"},
    {"emoji": "✅", "name": "check mark button", "keywords": "check done ok yes", "category": "symbols"},
    {"emoji": "❌", "name": "cross mark", "keywords": "no wrong error cancel", "category": "symbols"},
    {"emoji": "⚡", "name": "lightning", "keywords": "lightning fast energy electric", "category": "symbols"},
    {"emoji": "🔑", "name": "key", "keywords": "key lock access password", "category": "symbols"},
    {"emoji": "💡", "name": "light bulb", "keywords": "idea light think bright", "category": "symbols"},
    {"emoji": "🎯", "name": "direct hit", "keywords": "target goal aim bullseye", "category": "symbols"},
    {"emoji": "🏆", "name": "trophy", "keywords": "trophy win award champion", "category": "symbols"},
    {"emoji": "💎", "name": "gem stone", "keywords": "diamond gem jewel valuable", "category": "symbols"},
    # Tech
    {"emoji": "💻", "name": "laptop", "keywords": "computer laptop code work", "category": "tech"},
    {"emoji": "📱", "name": "mobile phone", "keywords": "phone mobile smartphone", "category": "tech"},
    {"emoji": "🤖", "name": "robot", "keywords": "robot ai machine android", "category": "tech"},
    {"emoji": "🔒", "name": "locked", "keywords": "lock secure private", "category": "tech"},
    {"emoji": "📡", "name": "satellite antenna", "keywords": "satellite signal wifi network", "category": "tech"},
    {"emoji": "🖥️", "name": "desktop computer", "keywords": "desktop computer monitor", "category": "tech"},
]


class EmojiSkill:
    """Look up, search, and suggest emoji by name or keyword."""

    name = "emoji"
    description = (
        "Emoji lookup and search. "
        "Supported actions: 'find' (query); 'random'; "
        "'list_categories'; 'by_category' (category); "
        "'info' (name)."
    )

    def run(
        self,
        action: str,
        query: str = "",
        category: str = "",
        name: str = "",
    ) -> str:
        action = action.strip().lower()

        if action == "find":
            return self._find(query)
        if action == "random":
            e = secrets.choice(_EMOJI_DB)
            return f"{e['emoji']}  {e['name']}"
        if action == "list_categories":
            cats = sorted(set(e["category"] for e in _EMOJI_DB))
            return "Categories: " + ", ".join(cats)
        if action == "by_category":
            return self._by_category(category)
        if action == "info":
            return self._info(name or query)
        return (
            f"Error: unknown action {action!r}. "
            "Use find, random, list_categories, by_category, or info."
        )

    @staticmethod
    def _find(query: str) -> str:
        if not query:
            return "Error: query is required for find"
        q = query.lower()
        results = [
            e for e in _EMOJI_DB
            if q in e["name"].lower() or q in e["keywords"].lower()
        ]
        if not results:
            return f"No emoji found for {query!r}"
        return " ".join(f"{e['emoji']} ({e['name']})" for e in results[:10])

    @staticmethod
    def _by_category(category: str) -> str:
        if not category:
            return "Error: category is required"
        cat = category.lower().strip()
        results = [e for e in _EMOJI_DB if e["category"] == cat]
        if not results:
            cats = sorted(set(e["category"] for e in _EMOJI_DB))
            return f"No emoji in category {category!r}. Available: {', '.join(cats)}"
        return " ".join(f"{e['emoji']} {e['name']}" for e in results)

    @staticmethod
    def _info(name: str) -> str:
        if not name:
            return "Error: name is required for info"
        n = name.lower().strip()
        match = next((e for e in _EMOJI_DB if e["name"].lower() == n or n in e["name"].lower()), None)
        if match is None:
            return f"No emoji found with name {name!r}"
        return (
            f"Emoji    : {match['emoji']}\n"
            f"Name     : {match['name']}\n"
            f"Category : {match['category']}\n"
            f"Keywords : {match['keywords']}"
        )
