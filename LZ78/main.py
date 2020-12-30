''''LZ78 algorithm'''

from math import log2

from bitarray import bitarray
from bitarray.util import ba2int


# 5 PIRMI BITAI - K (0 - 31) (0 - inf)


def encode(dict_size: int):
    pass


def decode(file: str):
    dict_size = 0
    dictionary = [bytearray()]
    output_buffer = bytearray()
    with open(file, mode='rb') as f:
        input_buffer = bitarray()
        input_buffer.fromfile(f)
        k = ba2int(input_buffer[0:4])
        n = 2 ** k
        while len(input_buffer) > 0:
            index_len = int(log2(dict_size if dict_size > 0 else 1))

            index = ba2int(input_buffer[:index_len])
            word = input_buffer[index_len:index_len + 8]

            entry = bytearray()
            entry.extend(dictionary[index])
            entry.append(word)

            if len(dictionary) < n:
                dictionary.append(entry)
            output_buffer.extend(entry)

            input_buffer = input_buffer[index_len + 8:]
    pass


if __name__ == "__main__":
    pass
