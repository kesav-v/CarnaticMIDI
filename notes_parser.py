import lark
from typing import Any


CARNATIC_GRAMMAR_PATH = "carnatic_notation_grammar.lark"


class NotesParser:
    _grammar: str | None = None

    def __init__(self) -> None:
        self._lark = lark.Lark(self.grammar, start="start")

    @property
    def grammar(self) -> str:
        if self._grammar is None:
            with open(CARNATIC_GRAMMAR_PATH) as f:
                self._grammar = f.read()
        return self._grammar

    def parse(self, str) -> Any:
        return self._lark.parse(str)


if __name__ == "__main__":
    parser = NotesParser()
    with open("notation_files/globe/democratic_republic_of_the_congo.txt") as f:
        content = f.read()
    print(parser.parse(content).pretty())
