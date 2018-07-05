from random import random
from utils import clean, sylco

from typing import List, Dict, Optional


class SongElement:
    """
    Song element object
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, opts, name: str, model, rhyme_dict, num_syllables: int, pattern: str):
        self.opts = opts
        self.name = name
        self.model = model
        self.rhyme_dict = rhyme_dict
        self.num_syllables = num_syllables
        self.pattern = pattern
        if self.name in ("C", "B"):
            self.title = self.opts[self.name]["title"]

        self.elem: List[str] = []
        self.stems: Dict[int, str] = {}
        self._write_elem()

    def get_elem(self) -> List[str]:
        """Get generated song element"""
        return self.elem

    def _write_elem(self):
        """Generate the song element. Generate lines
        that adhere to the rhyming pattern"""
        if hasattr(self, "title"):  # Add title
            self.elem.append(self.title)

        for idx, rhyme_type in enumerate(self.pattern):
            if idx > 0 and rhyme_type == self.pattern[idx - 1]:
                rhyme_line = self._gen_line(idx - 1)
            elif idx > 1 and rhyme_type == self.pattern[idx - 2]:
                rhyme_line = self._gen_line(idx - 2)
            line = rhyme_line if "rhyme_line" in locals() else self._gen_line()
            #  Add line stem to stems dict
            self.stems[idx] = clean(line.rsplit(None, 1)[-1])
            self.elem.append(line)

        if self.name == "B":  # If bridge add suffix
            self.elem.append(self._add_brige_suffix())

    def _gen_line(self, stem_index=None) -> Optional[str]:
        """Generates a line of the song. Returns a ryhming line
        if the index of previously generated stem to rhyme with
        is passed.
            Generates lines and checks whether they are valid up to
        a defined number of trials. If there is no valid line after
        the trials, returns None"""
        rhyme_stem = self.stems.get(stem_index)
        if rhyme_stem:
            rhyme_list = self._get_rhyming_words(rhyme_stem)
        else:
            raise IndexError("Stem does not exist!")

        for _ in range(self.opts["opts"]["iter"]):
            line = self.model.make_sentence()
            if line and self._in_syllable_range(line) and not self._is_duplicate(line):
                if not rhyme_list:
                    return line
                elif self._is_rhyme(line, rhyme_list) or random() > 0.9:
                    return line
        return None

    def _get_rhyming_words(self, stem: str) -> Optional[List[str]]:
        """Takes a line stem, returns its possible rhymes
        or, if it is unknown, returns None"""
        return self.rhyme_dict.get(stem)

    def _is_duplicate(self, line: str) -> bool:
        """Takes a generated song line. Returns true 90% of
        the time the line is already in SongElem, otherwise
        returns false"""
        return line in self.elem and random() > 0.05

    def _in_syllable_range(self, line: str) -> bool:
        """Takes a generated song line. Returns true if
        its syllable count is ±2 of a benchmark number
        of syllables"""
        return abs(sylco(line) - self.num_syllables) <= 2

    def _add_brige_suffix(self) -> str:
        """Return short line to end bridge"""
        while True:
            line = self.model.make_short_sentence(40)
            if line:
                return line + "..."

    @staticmethod
    def _is_rhyme(line: str, rhymes_list: List[str]) -> bool:
        """Takes a generated song line, a stem to rhyme with,
        and a list of rhymes for that stem. Returns true
        if its stem is in the rhyme list, otherwise returns
        false"""
        stem = clean(line.rsplit(None, 1)[-1])
        return stem in rhymes_list
