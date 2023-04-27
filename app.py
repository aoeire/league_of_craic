import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import (
    apology,
    login_required,
    check_player,
    password_validation,
    match_finder,
    set_checker,
    add_match_to_db,
    elo_difference,
    check_match_duplicate
)

# Points
MAX = 10
MIN = 1
BASE = 5

CIVS = {
    14: "spanish",
    26: "malians",
    3: "goths",
    10: "turks",
    7: "byzantines",
    33: "tatars",
    29: "malay",
    19: "italians",
    2: "franks",
    13: "celts",
    10: "turks",
    22: "magyars",
    17: "huns",
    35: "lithuanians",
    41: "bengalis",
    9: "saracens",
    40: "dravidians",
    4: "tuetons",
    6: "chinese",
    36: "burgundians",
    30: "burmese",
    25: "ethiopians",
    21: "incas",
    23: "slavs",
    34: "cumans",
    18: "koreans",
    28: "khmer",
    20: "hindustanis",
    42: "gurjaras",
    37: "sicilians",
    1: "britons",
    11: "vikings",
    5: "japanese",
    24: "portuguese",
    27: "berbers",
    38: "poles",
    8: "persians",
    16: "mayans",
    15: "aztecs",
    12: "mongols",
    39: "bohemiens",
    32: "bulgarians",
    31: "vietnamese",
}

# database path
db = SQL("sqlite:///player.db")

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        id = request.form.get("aoe2_profile")

        if not check_player(id):
            message ="aoe2.net ID provided does not exist"
            return apology(message)


        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return apology("Username or Password cannot be empty")

        elif not password_validation(password):
            return apology("Invalid Password")

        elif password != confirmation:
            return apology("Password matching error")

        else:
            password_hash = generate_password_hash(password)

            if db.execute(
                "SELECT username FROM player_details WHERE username = ?", username
            ):
                return apology("User already exists")

            db.execute(
                "INSERT INTO player_details (aoe2_id, username, hash, losses, wins, points) VALUES(?, ?, ?, ?, ?, ?)",
                id,
                username,
                password_hash,
                0,
                0,
                0,
            )

        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM player_details WHERE username = ?",
            request.form.get("username"),
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["db_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/")
def index():
    standings = db.execute("SELECT * FROM player_details ORDER BY points DESC")

    return render_template("history.html", standings=standings)


@app.route("/look_up", methods=["GET", "POST"])
# @login_required
def look_up():
    """Home page"""
    if request.method == "POST":
        try:
            id = request.form.get("player")
            player = lookup(id)

            return render_template("test.html", fact=player["rating"])
        except:
            message = "Not found"

            return apology(message)

    else:
        return render_template("index.html")


@app.route("/match", methods=["GET", "POST"])
@login_required
def match():
    players = db.execute("SELECT username FROM player_details")

    if request.method == "POST":
        try:
            # get match details
            match1 = request.form.get("match1")
            match2 = request.form.get("match2")
            match3 = request.form.get("match3")

            if check_match_duplicate([match1,match2,match3]):
                message = "Cannot have duplicate match IDs"
                return apology(message)

            player1 = request.form.get("player1")
            player2 = request.form.get("player2")

            winner = request.form.get("winner")

            times_played = db.execute(
                "SELECT COUNT(*) FROM match_details WHERE player_1_name = ? AND player_2_name = ?",
                player1,
                player2,
            )

            if set_checker(times_played):
                message = "These players have already logged 2 match sets"
                return apology(message)

            player1_stats = db.execute(
                "SELECT * FROM player_details WHERE username = ?", player1
            )

            player2_stats = db.execute(
                "SELECT * FROM player_details WHERE username = ?", player2
            )

            winning_player_elo = None
            losing_player_elo = None

            p1 = lookup(player1_stats[0]["aoe2_id"])
            p2 = lookup(player2_stats[0]["aoe2_id"])

            if winner == "player1":
                winning_player_elo = p1["rating"]
                losing_player_elo = p2["rating"]
            else:
                winning_player_elo = p2["rating"]
                losing_player_elo = p1["rating"]

            points = elo_difference(winning_player_elo, losing_player_elo, BASE, MAX)

            if winner == "player1":
                wins = 1 + int(player1_stats[0]["wins"])
                losses = 1 + int(player2_stats[0]["losses"])
                total_points = points + int(player1_stats[0]["points"])
            else:
                wins = 1 + int(player2_stats[0]["wins"])
                losses = 1 + int(player1_stats[0]["losses"])
                total_points = points + int(player2_stats[0]["points"])

            try:
                # start a database transaction
                with db.transaction():
                    # update player 1 stats
                    db.execute(
                        "UPDATE player_details SET points= :new_value, wins= :new_wins, losses= :new_losses WHERE username = :name",
                        new_value=total_points,
                        new_wins=wins,
                        new_losses=losses,
                        name=player1 if winner == "player1" else player2,
                    )

                    # update player 2 stats
                    db.execute(
                        "UPDATE player_details SET wins= :new_wins, losses= :new_losses WHERE username = :name",
                        new_wins=losses,
                        new_losses=wins,
                        name=player2 if winner == "player1" else player1,
                    )

                    # add match to database
                    if winner == "player1":
                        add_match_to_db(player1_stats, [match1, match2, match3], db)
                    else:
                        add_match_to_db(player2_stats, [match1, match2, match3], db)

            except Exception as e:
                message("Error, database transaction rolled back")
                return apology(message)

            return render_template("history.html", standings=standings)

        except:

            message = "Error"

            return apology(message)

    else:
        return render_template("match.html", players=players)


@app.route("/match_history")
@login_required
def match_history():
    matches = db.execute("SELECT * FROM match_details")

    return render_template("match_history.html", matches=matches, CIVS=CIVS)

@app.route("/handbook")
def handbook():
    return render_template("handbook.html")

@app.route("/maps")
def maps():
    return render_template("maps.html")