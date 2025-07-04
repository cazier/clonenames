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


@app.route(u'/')
def home_page():
    return render_template(u'index.html')


@app.route(u'/start', methods = [u'GET', u'POST'])
def start_page():
    if request.method == u'POST':
        game = clonenames.Board(request.form.get(u'words'))

        success = game.load_settings(
            teams = int(request.form.get(u'number')),
            size = int(request.form.get(u'size')))

        if success:
            room = generate_room_code()

            games[room] = game

            return redirect(url_for(u'game_page', room = room))

        else:
            return render_template(
                u'start.html',
                words = clonenames.wordlists,
                alert = u'The word list selected must be played on a smaller game board... Sorry!')

    elif request.method == u'GET':
        return render_template(u'start.html', words = wordlists)


@app.route(u'/game', methods = [u'GET', u'POST'])
def game_page():
    if request.args.get(u'room'):
        room = request.args.get(u'room')
        return render_template(
            u'game.html',
            show_input = False,
            room = room,
            host = True,
            words = games[room].table(),
            start = games[room].order[0],
            remnants = games[room].remnants)

    else:
        try:
            if request.method == u'GET':
                return render_template(
                    u'game.html',
                    show_input = True)

            elif request.method == u'POST':
                room = request.form.get(u'room', False).upper()
                if check_room_code(room):
                    return render_template(
                        u'game.html',
                        show_input = False,
                        room = room,
                        host = request.form.get(u'host', False) == u'on',
                        words = games[room].table(),
                        start = games[room].order[0],
                        remnants = games[room].remnants)

                else:
                    return render_template(
                        u'game.html',
                        show_input = True,
                        alert = u'The room code you entered does not exist. Please try again!')

        except AttributeError:
            return redirect(url_for(u'home_page'))

# @app.route(u'/statistics')
# def stats_page():
#     return render_template(u'statistics.html',
#         rooms = [games[game].statistics() for game in games])


@socketio.on(u'join')
def join(data):
    join_room(data[u'room'])


@socketio.on(u'clicked')
def handle_host_click(json):
    response = games[json[u'room']].get(json[u'id'])
    socketio.emit(u'revealed', {
        u'text': u'Host clicked on {word}'.format(
            word = response[u'word']),
        u'id': u'#{id}'.format(id = json[u'id']),
        u'remnant': response[u'remnant'],
        u'class': u'btn-{team}'.format(
            team = response[u'team'])}, room = json['room'])


@socketio.on(u'ended_turn')
def handle_end_turn(json):
    team = games[json[u'room']].advance_turn()

    alert = u'alert {team}-start alert-start'.format(team = team)
    button = u'btn btn-{team} float-right'.format(team = team)

    socketio.emit(u'change_turn', {
        u'alert': alert,
        u'text': team,
        u'button': button}, room = json[u'room'])


def generate_room_code():
    letters = u''.join(random.sample(list(u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 5))
    while letters in games.keys():
        return generate_room_code()

    return letters


def check_room_code(code):
    return code in games.keys()


def run():
    socketio.run(app, debug=True, host=u'0.0.0.0', port=12345)
