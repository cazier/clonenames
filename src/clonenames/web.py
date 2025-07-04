#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib.resources
import random

from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO, join_room
from werkzeug import Response

import clonenames
import clonenames.wordlists

wordlists = dict(clonenames.load_wordlists(*importlib.resources.files(clonenames.wordlists).iterdir()))

app = Flask(__name__)
socketio = SocketIO(app)

games: dict[str, clonenames.Board] = dict()


@app.route("/")
def home_page() -> str:
    return render_template("index.html")


@app.route("/start", methods=["GET", "POST"])
def start_page() -> str | Response:
    if request.method == "POST":
        game = clonenames.Board(wordlists[request.form["words"]])

        success = game.load_settings(teams=int(request.form["number"]), size=int(request.form["size"]))

        if success:
            room = generate_room_code()

            games[room] = game

            return redirect(url_for("game_page", room=room))

        else:
            return render_template(
                "start.html",
                words=clonenames.wordlists,
                alert="The word list selected must be played on a smaller game board... Sorry!",
            )

    return render_template("start.html", words=wordlists)


@app.route("/game", methods=["GET", "POST"])
def game_page() -> str | Response:
    if room := request.args.get("room"):
        return render_template(
            "game.html",
            show_input=False,
            room=room,
            host=True,
            words=games[room].table(),
            start=games[room].order[0],
            remnants=games[room].remnants,
        )

    try:
        if request.method == "GET":
            return render_template("game.html", show_input=True)

        room = request.form["room"].upper()
        if check_room_code(room):
            return render_template(
                "game.html",
                show_input=False,
                room=room,
                host=request.form["host"] == "on",
                words=games[room].table(),
                start=games[room].order[0],
                remnants=games[room].remnants,
            )

        else:
            return render_template(
                "game.html",
                show_input=True,
                alert="The room code you entered does not exist. Please try again!",
            )

    except AttributeError:
        return redirect(url_for("home_page"))


# @app.route(u'/statistics')
# def stats_page():
#     return render_template(u'statistics.html',
#         rooms = [games[game].statistics() for game in games])


@socketio.on("join")
def join(data: dict[str, str]) -> None:
    join_room(data["room"])


@socketio.on("clicked")
def handle_host_click(json: dict[str, str]) -> None:
    response = games[json["room"]].get(int(json["id"]))
    socketio.emit(
        "revealed",
        {
            "text": "Host clicked on {word}".format(word=response.word),
            "id": "#{id}".format(id=json["id"]),
            "remnant": response.remnant,
            "class": "btn-{team}".format(team=response.team),
        },
        to=json["room"],
    )


@socketio.on("ended_turn")
def handle_end_turn(json: dict[str, str]) -> None:
    team = games[json["room"]].advance_turn()

    alert = "alert {team}-start alert-start".format(team=team)
    button = "btn btn-{team} float-right".format(team=team)

    socketio.emit(
        "change_turn",
        {"alert": alert, "text": team, "button": button},
        to=json["room"],
    )


def generate_room_code() -> str:
    letters = "".join(random.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 5))
    while check_room_code(letters):
        return generate_room_code()

    return letters


def check_room_code(code: str) -> bool:
    return code in games.keys()


def run() -> None:
    socketio.run(app, debug=False, host="0.0.0.0", port=12345)
