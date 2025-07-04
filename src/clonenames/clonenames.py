#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import pathlib
import random
import time
import typing


def load_wordlists(*path: pathlib.Path) -> typing.Iterable[tuple[str, list[str]]]:
    for _path in path:
        if not _path.is_file():
            continue

        text = _path.read_text(encoding="utf8")
        name, *words = [line for line in text.splitlines() if line]
        yield name, words


@dataclasses.dataclass
class Card:
    number: int
    word: str
    team: str

    remnant: int = dataclasses.field(default=0, init=False)
    shown: bool = dataclasses.field(default=False, init=False)

    def __repr__(self) -> str:
        return self.word

    def get(self) -> typing.Self:
        self.shown = True
        return self


class Board:
    """docstring for Board"""

    def __init__(self, source: list[str]) -> None:
        self.source = source

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

        elif (size**0.5) % 1 == 0:
            self.size = size if size > MIN else MIN

        elif size < MIN:
            self.size = MIN

        else:
            self.size = int(size**0.5) ** 2

        self.length = int(self.size**0.5)

    def load_words(self) -> None:
        random.seed(time.perf_counter())

        self.COLORS = ["red", "blue", "green", "yellow"]
        random.shuffle(self.COLORS)

        self.words: list[Card] = list()
        self.remnants: dict[str, int] = {"assassin": 1}

        source = list(enumerate(random.sample(self.source, self.size)))

        first_team_cards = int(self.size / (self.teams + 1)) + 1
        other_team_cards = first_team_cards - 1
        bystanders_cards = self.size - first_team_cards - (other_team_cards * (self.teams - 1)) - 1

        self.FIRST = self.COLORS.pop()

        self.order = [self.FIRST]
        self.turn = 0

        for _ in range(first_team_cards):
            self.words.append(Card(*source.pop(0), self.FIRST))

        self.remnants[self.FIRST] = first_team_cards

        for _ in range(self.teams - 1):
            color = self.COLORS.pop()
            self.order.append(color)
            for _ in range(other_team_cards):
                self.words.append(Card(*source.pop(0), color))

            self.remnants[color] = other_team_cards

        for _ in range(bystanders_cards):
            self.words.append(Card(*source.pop(0), "bystander"))

        self.remnants["bystander"] = bystanders_cards

        self.words.append(Card(*source.pop(0), "assassin"))

        random.shuffle(self.words)

        self.legend = {j.number: i for i, j in enumerate(self.words)}

    def table(self) -> list[list[Card]]:
        return [self.words[i : i + self.length] for i in range(0, self.size, self.length)]

    def get(self, id: int) -> Card:
        response = self.words[self.legend[id]].get()

        self.remnants[response.team] -= 1

        response.remnant = self.remnants[response.team]

        return response

    def advance_turn(self) -> str:
        if self.turn == 1200:
            self.turn = 1
        else:
            self.turn += 1

        return self.order[self.turn % self.teams]

    # def statistics(self):
    #     words = [pack for pack, file in wordlists.items() if file == self.wordlist][0]
    #     return [self.teams, len(self.words), words]
