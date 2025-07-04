#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

wordlists = {
    u'Codenames': u'codenames',
    u'Cards Against Humanity': u'cardsagainsthumanity',
    u'Pokemon (Generation 1)': u'pokemon_gen1',
    u'__builtins__': u'builtin_functions'}


class Board(object):
    """docstring for Board"""
    def __init__(self, wordlist: str = u'codenames') -> None:
        # self.wordlist = wordlist
        with open(u'wordlists/{wordlist}'.format(wordlist = wordlist), u'r') as text_file:
            self.source = [line for line in text_file.read().split(u'\n') if line != u'']

    def load_settings(self, teams: int = 2, size: int = 25) -> bool:
        self.check_size(size)

        if self.size > len(self.source):
            return False

        self.teams = teams

        self.load_words()

        return True

    def check_size(self, size: int) -> None:
        MIN = 25
        MAX = 100

        if size > MAX:
            self.size = MAX

        elif (size ** 0.5) % 1 == 0:
            self.size = size if size > MIN else MIN

        elif size < MIN:
            self.size = MIN

        else:
            self.size = int(size ** 0.5) ** 2

        self.length = int(self.size ** 0.5)

    def load_words(self) -> None:
        from time import clock
        random.seed(clock())

        self.COLORS = [u'red', u'blue', u'green', u'yellow']
        random.shuffle(self.COLORS)

        self.words: list = list()
        self.remnants: dict = {'assassin': 1}

        source = list(enumerate(random.sample(self.source, self.size)))

        first_team_cards = int(self.size / (self.teams + 1)) + 1
        other_team_cards = first_team_cards - 1
        bystanders_cards = self.size - first_team_cards - (other_team_cards * (self.teams - 1)) - 1

        self.FIRST = self.COLORS.pop()

        self.order = [self.FIRST]
        self.turn = 0

        for _ in range(first_team_cards):
            self.words.append(Card(source.pop(0), self.FIRST))

        self.remnants[self.FIRST] = first_team_cards

        for team in range(self.teams - 1):
            color = self.COLORS.pop()
            self.order.append(color)
            for _ in range(other_team_cards):
                self.words.append(Card(source.pop(0), color))

            self.remnants[color] = other_team_cards

        for _ in range(bystanders_cards):
            self.words.append(Card(source.pop(0), u'bystander'))

        self.remnants[u'bystander'] = bystanders_cards

        self.words.append(Card(source.pop(0), u'assassin'))

        random.shuffle(self.words)

        self.legend = {j.number: i for i, j in enumerate(self.words)}

    def table(self) -> list:
        return [self.words[i: i + self.length] for i in range(0, self.size, self.length)]

    def get(self, entry):
        response = self.words[self.legend[int(entry)]].get()

        self.remnants[response[u'team']] -= 1

        response[u'remnant'] = self.remnants[response[u'team']]

        return response

    def advance_turn(self):
        if self.turn == 1200:
            self.turn = 1
        else:
            self.turn += 1

        return self.order[self.turn % self.teams]

    # def statistics(self):
    #     words = [pack for pack, file in wordlists.items() if file == self.wordlist][0]
    #     return [self.teams, len(self.words), words]


class Card(object):
    def __init__(self, word: tuple, team: str) -> None:
        self.word = word[1]
        self.number = word[0]
        self.team = team
        self.shown = False

    def __repr__(self) -> str:
        return self.word

    def get(self) -> dict:
        self.shown = True
        return {u'word': self.word, u'team': self.team}
