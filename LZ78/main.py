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
    output_buffer = bitarray()
    output_buffer.extend(int2ba(dict_size, length=5))

    dictionary = [0]
    elements_added = 0
    elements_added_bits = 0  # used to determine if we should increase the lenght for index

    with open(file, mode='rb') as f:
        input_buffer = bitarray()
        input_buffer.fromfile(f)
        print("input:", input_buffer.to01())

    entry_index_len = 0  # Used to calculate bit lenght for dictionary entry
    end_reached = False
    while len(input_buffer) > 0:
        index_in_dic = 0

        # Read bytes and search for a match in a dictionary
        bytes_read = 0
        while True:
            bytes_read += 1
            # End of input buffer reached
            if input_buffer[0: 8 * bytes_read].tobytes() not in dictionary:
                # Symbol that is going to be encoded into the entry
                entry_symbol = input_buffer[8 * (bytes_read - 1): 8 * bytes_read]
                if bytes_read != 1:
                    entry_to_extend = input_buffer[0: 8 * (bytes_read - 1)].tobytes()
                    index_in_dic = dictionary.index(entry_to_extend)
                break
            elif len(input_buffer) < 8 * (bytes_read):
                end_reached = True
                break

        # if the end of input buffer reached, simply put the index from dictionary
        if end_reached:
            output_to_add = bitarray(2 ** entry_index_len)  # Maximum amount of bits needed
            output_to_add.setall(False)
            entry_to_extend = input_buffer.tobytes()
            pointer_to_entry = int2ba(dictionary.index(entry_to_extend))  # Index to be added
            # After the index is added, we remove overflow zeros
            zeros_to_remove = len(pointer_to_entry)
            output_to_add.extend(pointer_to_entry)
            output_to_add = output_to_add[zeros_to_remove:]
            print("last", output_to_add, 2 ** entry_index_len)
            output_buffer.extend(output_to_add)
            break

        # Adding entries to the dictionary
        if dict_size == 0 or len(dictionary) - 1 < 2 ** dict_size:
            byte_to_add = input_buffer[0: 8 * bytes_read].tobytes()
            dictionary.append(byte_to_add)

        # To save space, we add only needed number of bits to output
        output_to_add = bitarray(2 ** entry_index_len)  # Maximum amount of bits needed
        output_to_add.setall(False)
        pointer_to_entry = int2ba(index_in_dic)  # Index to be added
        # After the index is added, we remove overflow zeros
        zeros_to_remove = len(pointer_to_entry)
        output_to_add.extend(pointer_to_entry)
        output_to_add = output_to_add[zeros_to_remove:]
        output_to_add.extend(entry_symbol)  # Adding the symbol which extends dict element
        output_buffer.extend(output_to_add)
        print(output_to_add.to01())

        elements_added += 1
        elements_added_bits += 1
        print(elements_added, elements_added_bits, entry_index_len)
        if elements_added > 2 ** entry_index_len:
            entry_index_len += 1
            elements_added_bits = 1

        input_buffer = input_buffer[8 * bytes_read:]

    with open(file + '.compressed' + str(dict_size), mode='wb') as out:
        output_buffer.fill()
        out.write(output_buffer)

    with open(file + '.compressed' + str(dict_size), mode='rb') as inp:
        buffer = bitarray()
        buffer.fromfile(inp)
        print("file:", buffer.to01())


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
        while input_len > 0:
            index_len = int(log2(entry_index - 1 if entry_index > 1 else 1)) + 1  # 1 - 0, 2 - 0,1, 3-0,1,2, 4-0,1,2,3.
            # 1,2 - 1 bit, 3,4 - 2 bits, 5,6,7,8-3 bits, 9,10,11,12,13,14,15,16 - 4 bits

            index = ba2int(input_buffer[:index_len])

            entry = bytearray()
            entry.extend(dictionary[index])

            if input_len - index_len > 8:
                word = input_buffer[index_len:index_len + 8]
                entry.append(int(word.to01(), 2))
                input_buffer = input_buffer[index_len + 8:]
                entry_index = entry_index + 1
                input_len = len(input_buffer)
            else:
                input_len = 0

            if n is inf or len(dictionary) < n:
                dictionary.append(entry)
            output_buffer.extend(entry)

    file_path = Path(file)

    if file_path.suffix.startswith('.compressed'):
        with open(file_path.stem + '.uncompressed', mode='wb') as out:
            out.write(output_buffer)
    print(output_buffer)


if __name__ == "__main__":
    print('\n')
    # encode(0, 'test_text.txt')
    # encode(0, 'test_text_longer.txt')
    # encode(0, 'test_image.bmp')
    # encode(2, 'test_text.txt')
    # encode(2, 'test_text_longer.txt')
    # encode(2, 'test_image.bmp')
    decode('test_text.txt.compressed0')
    decode('test_text_longer.txt.compressed0')
