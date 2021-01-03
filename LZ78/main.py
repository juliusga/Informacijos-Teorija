''''LZ78 algorithm'''

from math import log2, inf

from bitarray import bitarray
from bitarray.util import ba2int, int2ba

import argparse

# 5 PIRMI BITAI - K (0 - 31) (0 - inf)
# K | Dictionary size
# 0 | INF
# 1 | 2
# 2 | 4
# 3 | 8
# ...


def encode(dict_size: int, in_file, out_file):
    input_buffer = bitarray()
    input_buffer.fromfile(in_file)

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
            elif input_buffer[0: bits_read].tobytes() not in dictionary:
                entry_symbol = input_buffer[bits_read - 8:bits_read]
                entry_index = 0 if bits_read == 8 else dictionary.index(input_buffer[0:bits_read - 8].tobytes()) + 1
                break

        if dict_size == 0 or len(dictionary) < 2 ** dict_size:
            dictionary_entry = input_buffer[:bits_read].tobytes()
            dictionary.append(dictionary_entry)

        # Add entries to output
        length_of_index = 1 if entries_added == 0 else int(log2(entries_added)) + 1
        output_buffer.extend(int2ba(entry_index, length=length_of_index))
        if entry_symbol is not None:
            output_buffer.extend(entry_symbol)
        entries_added += 1

        # Shrink the input buffer
        input_buffer = input_buffer[bits_read:] if entry_symbol is not None else bitarray()

    output_buffer.fill()
    out_file.write(output_buffer)
    print("FILE <" + in_file.name + "> COMPRESSED TO <" + out_file.name + ">")


def decode(in_file, out_file):
    entry_index = 1
    dictionary = [bytearray()]
    output_buffer = bytearray()
    input_buffer = bitarray()
    input_buffer.fromfile(in_file)
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

    out_file.write(output_buffer)
    print(f"FILE <{in_file.name}> DECOMPRESSED TO <{out_file.name}>")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='(De-)Compression using LZ78 algorithm.')
    parser.add_argument('-k', type=int, default=16, choices=range(0, 32),
                        help='Number raised by power of 2 for defining dictionary size')
    parser.add_argument('--type', choices=['encode', 'decode', 'e', 'd'], type=str, required=True,
                        help='Type of operation')
    parser.add_argument('infile', nargs=1, type=argparse.FileType('rb'),
                        help='File to (de-)compress')
    parser.add_argument('outfile', nargs=1, type=argparse.FileType('wb'),
                        help='Output file for (de-)compression')

    args = parser.parse_args()

    if args.type == 'e' or args.type == 'encode':
        encode(args.k, args.infile[0], args.outfile[0])
    elif args.type == 'd' or args.type == 'decode':
        decode(args.infile[0], args.outfile[0])

