#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib.resources
import sys

if sys.version_info[0] < 3:
    print("Sorry, but Clonenames requires Python 3. Please install it to play!")
    print("Exiting now...")
    sys.exit()

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room

import random

import clonenames
import clonenames.wordlists

wordlists = dict(clonenames.load_wordlists(*importlib.resources.files(clonenames.wordlists).iterdir()))

app = Flask(__name__)
socketio = SocketIO(app)

games = dict()


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route("/start", methods=["GET", "POST"])
def start_page():
    if request.method == "POST":
        game = clonenames.Board(request.form.get("words"))

        success = game.load_settings(
            teams=int(request.form.get("number")), size=int(request.form.get("size"))
        )

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

    elif request.method == "GET":
        return render_template("start.html", words=wordlists)


@app.route("/game", methods=["GET", "POST"])
def game_page():
    if request.args.get("room"):
        room = request.args.get("room")
        return render_template(
            "game.html",
            show_input=False,
            room=room,
            host=True,
            words=games[room].table(),
            start=games[room].order[0],
            remnants=games[room].remnants,
        )

    else:
        try:
            if request.method == "GET":
                return render_template("game.html", show_input=True)

            elif request.method == "POST":
                room = request.form.get("room", False).upper()
                if check_room_code(room):
                    return render_template(
                        "game.html",
                        show_input=False,
                        room=room,
                        host=request.form.get("host", False) == "on",
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
def join(data):
    join_room(data["room"])


@socketio.on("clicked")
def handle_host_click(json):
    response = games[json["room"]].get(json["id"])
    socketio.emit(
        "revealed",
        {
            "text": "Host clicked on {word}".format(word=response["word"]),
            "id": "#{id}".format(id=json["id"]),
            "remnant": response["remnant"],
            "class": "btn-{team}".format(team=response["team"]),
        },
        room=json["room"],
    )


@socketio.on("ended_turn")
def handle_end_turn(json):
    team = games[json["room"]].advance_turn()

    alert = "alert {team}-start alert-start".format(team=team)
    button = "btn btn-{team} float-right".format(team=team)

    socketio.emit(
        "change_turn",
        {"alert": alert, "text": team, "button": button},
        room=json["room"],
    )


def generate_room_code():
    letters = "".join(random.sample(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), 5))
    while letters in games.keys():
        return generate_room_code()

    return letters


def check_room_code(code):
    return code in games.keys()


if __name__ == "__main__":
    socketio.run(app, debug=False, host="0.0.0.0")
