''''LZ78 algorithm'''

from math import log2, inf
from pathlib import Path
from bitarray import bitarray
from bitarray.util import ba2int, int2ba

# 5 PIRMI BITAI - K (0 - 31) (0 - inf)
# K | Dictionary size
# 0 | INF
# 1 | 2
# 2 | 4
# 3 | 8
# ...


def encode(dict_size: int, file: str):
    with open(file, mode='rb') as input_file:
        input_buffer = bitarray()
        input_buffer.fromfile(input_file)

    dictionary = []
    output_buffer = bitarray()
    output_buffer.extend(int2ba(dict_size, length=5))
    entries_added = 0

    while len(input_buffer) > 0:
        bits_read = 0
        while True:
            bits_read += 8
            if bits_read > len(input_buffer):
                entry_symbol = None
                entry_index = dictionary.index(input_buffer.tobytes()) + 1
                break
            elif input_buffer[0 : bits_read].tobytes() not in dictionary:
                entry_symbol = input_buffer[bits_read - 8:bits_read]
                entry_index = 0 if bits_read == 8 else dictionary.index(input_buffer[0:bits_read - 8].tobytes()) + 1
                break

        if dict_size == 0 or len(dictionary) < 2 ** dict_size:
            dictionary_entry = input_buffer[:bits_read].tobytes()
            dictionary.append(dictionary_entry)

        # Add entries to output
        length_of_index = 1 if entries_added == 0 else int(log2(entries_added)) + 1
        output_buffer.extend(int2ba(entry_index, length=length_of_index))
        if entry_symbol != None:
            output_buffer.extend(entry_symbol)
        entries_added += 1

        # Shrink the input buffer
        input_buffer = input_buffer[bits_read:] if entry_symbol != None else bitarray()

    with open(file + '.compressed' + str(dict_size), mode='wb') as out:
        output_buffer.fill()
        out.write(output_buffer)
        print("FILE <" + file + "> COMPRESSED TO <" + file + '.compressed' + str(dict_size) + ">")


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
        input_len = len(input_buffer)
        current_index = 0
        while input_len - current_index > 0:
            index_len = int(log2(entry_index - 1 if entry_index > 1 else 1)) + 1  # 1 - 0, 2 - 0,1, 3-0,1,2, 4-0,1,2,3.
            # 1,2 - 1 bit, 3,4 - 2 bits, 5,6,7,8-3 bits, 9,10,11,12,13,14,15,16 - 4 bits

            index = ba2int(input_buffer[current_index:current_index + index_len])

            entry = bytearray()
            entry.extend(dictionary[index])

            if (input_len - current_index) - index_len > 8:
                word = input_buffer[current_index + index_len:current_index + index_len + 8]
                entry.append(ba2int(word))
                current_index = current_index + index_len + 8
                entry_index = entry_index + 1
            else:
                current_index = input_len

            if n is inf or len(dictionary) <= n:
                dictionary.append(entry)
            output_buffer.extend(entry)

    file_path = Path(file)

    if file_path.suffix.startswith('.compressed'):
        out_filename = file_path.stem + '.uncompressed'
        with open(out_filename, mode='wb') as out:
            out.write(output_buffer)
            print(f"FILE <{file}> DECOMPRESSED TO <{out_filename}>")


if __name__ == "__main__":
    print('\n')
    # encode(0, 'test_text.txt')
    # encode(0, 'test_text_longer.txt')
    # encode(0, 'test_image.bmp')
    # encode(1, 'test_text.txt')
    # encode(1, 'test_text_longer.txt')
    # encode(1, 'test_image.bmp')
    # encode(2, 'test_text.txt')
    # encode(2, 'test_text_longer.txt')
    # encode(2, 'test_image.bmp')
    # decode('test_text.txt.compressed0')
    # decode('test_text.txt.compressed1')
    # decode('test_text.txt.compressed2')
    # decode('test_text_longer.txt.compressed0')
    # decode('test_text_longer.txt.compressed1')
    # decode('test_text_longer.txt.compressed2')
    # decode('test_image.bmp.compressed0')
    # decode('test_image.bmp.compressed1')
    # decode('test_image.bmp.compressed2')
