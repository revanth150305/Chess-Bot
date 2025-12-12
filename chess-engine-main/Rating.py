import json
import os
from datetime import datetime

RATINGS_FILE = "ratings.json"

class PlayerRating:
    def __init__(self, rating: float = 1200.0):
        self.rating = rating

    def get_rating(self) -> int:
        return round(self.rating)

    def update(self, opponent_rating: float, result: float):
        K = 64
        expected_score = 1 / (1 + 10 ** ((opponent_rating - self.rating) / 400))
        self.rating += K * (result - expected_score)

    def __repr__(self):
        return f"PlayerRating({self.get_rating()})"


def save_ratings(white_player: PlayerRating, black_player: PlayerRating, white_name="White", black_name="Black"):
    """Save current ratings to ratings.json with timestamp and game index"""
    game_data = {
        "game": None,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "white_name": white_name,
        "black_name": black_name,
        "white": white_player.get_rating(),
        "black": black_player.get_rating()
    }

    if os.path.exists(RATINGS_FILE):
        try:
            with open(RATINGS_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    game_data["game"] = f"Game{len(data) + 1}"

    data.append(game_data)
    with open(RATINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_ratings():
    if os.path.exists(RATINGS_FILE):
        try:
            with open(RATINGS_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                last = data[-1]
                white_rating = last.get("white", 1200)
                black_rating = last.get("black", 1200)
                return {
                    "white": PlayerRating(white_rating),
                    "black": PlayerRating(black_rating)
                }
        except (json.JSONDecodeError, KeyError):
            pass
    return {
        "white": PlayerRating(),
        "black": PlayerRating()
    }
