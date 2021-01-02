''''LZ78 algorithm'''

from math import log2, inf
from pathlib import Path

from bitarray import bitarray
from bitarray.util import ba2int


# 5 PIRMI BITAI - K (0 - 31) (0 - inf)


def encode(dict_size: int):
    pass


def decode(file: str):
    entry_index = 1
    dictionary = [bytearray()]
    output_buffer = bytearray()
    with open(file, mode='rb') as f:
        input_buffer = bitarray()
        input_buffer.fromfile(f)
        k = ba2int(input_buffer[:5])
        n = 2 ** k if k > 0 else inf
        input_buffer = input_buffer[5:]
        while len(input_buffer) > 8:
            index_len = int(log2(entry_index)) + 1

            index = ba2int(input_buffer[:index_len])
            word = input_buffer[index_len:index_len + 8]

            entry = bytearray()
            entry.extend(dictionary[index])
            entry.append(word)

            if n is inf or len(dictionary) < n:
                dictionary.append(entry)
            output_buffer.extend(entry)

            input_buffer = input_buffer[index_len + 8:]
            entry_index = entry_index + 1

    file_path = Path(file)

    if file_path.suffix == '.compressed':
        with open(file_path.stem, mode='wb') as out:
            out.write(output_buffer)


if __name__ == "__main__":
    pass
