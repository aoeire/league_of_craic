import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from collections import Counter
import re
import math


def password_validation(password):
    reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*)[A-Za-z\d]{6,20}$"

    # compiling regex
    pattern = re.compile(reg)

    # searching regex
    match = re.search(pattern, password)

    # validating conditions
    if match:
        return True
    else:
        False


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(player):
    """Look up aoe2 player."""
    # Contact API
    try:
        url = f"https://aoe2.net/api/player/ratinghistory?game=aoe2de&leaderboard_id=3&profile_id={player}&count=1"
        response = requests.get(url)
        response.raise_for_status()

    except requests.RequestException:
        return None

    # Parse response
    try:
        player_stats = response.json()

        return {
            "rating": player_stats[0]["rating"],
            "wins": player_stats[0]["num_wins"],
            "losses": player_stats[0]["num_losses"],
        }

    except (KeyError, TypeError, ValueError, IndexError):
        return None


def match_finder(player, match_id):
    # Contact API
    try:
        url = f"https://aoe2.net/api/player/matches?game=aoe2de&profile_id={player}&count=100"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response

    try:
        game_stats = response.json()
        count = 0
        for i in game_stats:
            if i["match_id"] == match_id:
                return {
                    "player_1_id": i["players"][0]["profile_id"],
                    "player_2_id": i["players"][1]["profile_id"],
                    "player_1_name": i["players"][0]["name"],
                    "player_2_name": i["players"][1]["name"],
                    "player_1_civ": i["players"][0]["civ"],
                    "player_2_civ": i["players"][1]["civ"],
                    "player_1_rating": i["players"][0]["rating"],
                    "player_2_rating": i["players"][1]["rating"],
                }

        return None

    except (KeyError, TypeError, ValueError):
        return None


def set_checker(times):
    print(times)
    if times is not None:
        times_played_int = times[0]["COUNT(*)"]

        print(times_played_int)

        if times_played_int >= 6:
            return True
        else:
            return False
    else:
        return None


def add_match_to_db(player, matches, database):

     for match in matches:

        m = match_finder(player[0]["aoe2_id"], match)

        database.execute("INSERT INTO match_details (game_ref, player_1_id, player_2_id, player_1_name, player_2_name, player_1_civ, player_2_civ, player_1_rating, player_2_rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    match,
                    m["player_1_id"],
                    m["player_2_id"],
                    m["player_1_name"],
                    m["player_2_name"],
                    m["player_1_civ"],
                    m["player_2_civ"],
                    m["player_1_rating"],
                    m["player_2_rating"],
                    )

def elo_difference(winner_elo, loser_elo, BASE, MAX):

    elo_difference = (
        (loser_elo - winner_elo) / winner_elo * 100
    )

    points = BASE + ((elo_difference / 100) * MAX)

    if points < 1:
        points = 1
    elif points > 10:
        points = 10

    points = math.floor(points)

    return points

def check_match_duplicate(matches):
    # Count the number of occurrences of each variable using a Counter object
    count = Counter(matches)

    # Check if any variable occurs more than once
    for _, value in count.items():
        if value > 1:
            return True
    return False

def check_player(p):

    player = lookup(p)

    if player is not None:
        return True
    else:
        return False
