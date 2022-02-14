import os
import itertools

from enum import Enum, auto

from .option_file_data import (
    OF_BYTE_LENGTH,
    OF_BLOCK,
    OF_BLOCK_SIZE,
    OF_KEY_PC,
)

from .club import Club

from .utils.common_functions import bytes_to_int, zero_fill_right_shift

class OptionFile:
    of_byte_length = OF_BYTE_LENGTH
    of_block = OF_BLOCK
    of_block_size = OF_BLOCK_SIZE
    of_key_pc = OF_KEY_PC

    def __init__(self, file_location):
        self.file_location = file_location

        self.data = bytearray()
        self.file_name = ""
        self.game_type = None

        self.read_option_file()

        #self.set_clubs()

    def get_game_type(self, file_name):
        """
        Return game type from supplied filename string.
        """
        game_type_map = {
            "KONAMI-WIN32PES4OPT": GameType.pc_pes,
            "KONAMI-WIN32WE8UOPT": GameType.pc_pwe,
        }
        return game_type_map.get(file_name)

    def read_option_file(self):
        """
        Decrypt supplied file and set OF data.
        """
        of_file = open(self.file_location, "rb")
        file_name = os.path.basename(of_file.name)
        self.file_name = file_name
        self.game_type = self.get_game_type(file_name)

        file_contents = of_file.read()
        of_file.close()

        self.data = bytearray(file_contents)
        self.convert_data()

        return True

    def save_option_file(self, file_location=None):
        """
        Save OF data to supplied file.
        """
        file_location = self.file_location = file_location or self.file_location

        self.checksums()
        self.convert_data()

        of_file = open(file_location, "wb")
        of_file.write(self.data)
        of_file.close()

        self.convert_data()

        return True

    def convert_data(self):
        """
        Converts OF data based on PC key.
        """
        key = 0

        for i in range(self.of_byte_length):
            self.data[i] = self.data[i] ^ self.of_key_pc[key]

            if key < 255:
                key += 1
            else:
                key = 0

    def checksums(self):
        """
        Set checksums.
        """
        for i in range(len(self.of_block)):
            checksum = 0

            for a in range(self.of_block_size[i]):
                checksum += self.data[self.of_block[i] + a]
            self.data[self.of_block[i] - 4] = checksum & 0xFF

    def set_clubs(self):
        """
        Load all clubs from OF data and add to clubs list.
        """
        self.clubs = []
        for i in range(Club.total):
            club = Club(self, i)
            self.clubs.append(club)


class GameType(Enum):
    pc_pes = auto()
    pc_pwe = auto()
