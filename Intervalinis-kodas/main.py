 # main.py @ Intervalinis-kodas
import itertools
import os
from math import log2
import argparse


from bitarray import bitarray
from bitarray.util import int2ba, ba2int


# 1 bitas - c1 ? c2 = 0 ? 1
# 4 bitai - k

# For printing the files in binary format
def print_file_binary(file):
    with open(file, mode='rb') as f:
        file_buffer = bitarray()
        file_buffer.fromfile(f)
        print("File <" + file + ">:", file_buffer.to01(), "\n")


def generate_gamma(index: int):
    # uk = 000...000(k+1)_2
    zeros = '0' * int(log2(index + 1))
    number = bin(index + 1)[2:]
    gamma_array = bitarray(zeros + number)
    return gamma_array


# C2
def generate_delta(index: int):
    # v_k_s = u_[log2(k+1)] + (k+1)_2
    m_k = int(log2(index + 1))
    delta_array = generate_gamma(m_k)
    k_part = int2ba(index + 1)
    delta_array.extend(k_part)
    delta_array.pop(len(delta_array) - m_k - 1)
    return delta_array


def generate_gamma_inv(element: bitarray):
    while not element[0]:
        element.pop(0)
    return ba2int(element) - 1


def generate_delta_inv(element: bitarray):
    if len(element) == 1:
        return 0
    zero_counter = 0
    while not element[0]:
        element.pop(0)
        zero_counter += 1
    element.pop(0)
    for i in range(zero_counter):
        element.pop(0)
    element.insert(0, True)
    return ba2int(element) - 1


def initialize_abc(k: int):
    return [''.join(seq) for seq in itertools.product('01', repeat=k)]


def encode(in_file, out_file, is_c1: bool, k: int):
    out_buffer = bitarray()
    out_buffer.append(is_c1)
    out_buffer.extend(int2ba(k - 1, length=4))
    #  First bit indicates whether it is c1 or c2
    #  Following next 4 bits define word length.

    pcode_gen_func = generate_gamma if is_c1 else generate_delta
    #  Select p code generator function.

    input_buffer = bitarray()
    input_buffer.extend(''.join(initialize_abc(k)))  # Fill with ABC.
    input_buffer.fromfile(in_file)  # Fill with data from file.
    buffer_len = len(input_buffer)

    word_index = k * 2 ** k
    while word_index < buffer_len:

        if word_index + k > buffer_len:
            fill = word_index + k - buffer_len
            input_buffer.extend('0' * fill)

        word = input_buffer[word_index:word_index + k]
        for prev_word_index in range(word_index, 0, -k):  # Read from abc beginning to the current index.
            prev_word = input_buffer[prev_word_index - k:prev_word_index]
            if word == prev_word:
                out_buffer.extend(pcode_gen_func((word_index - prev_word_index) // k))
                break
        word_index = word_index + k

    out_buffer.fill()
    out_file.write(out_buffer)
    print(out_file)
    print("FILE", f'<{in_file.name}>', "COMPRESSED TO", f'<{out_file.name}>')


def decode(in_file, out_file):
    input_buffer = bitarray()
    input_buffer.fromfile(in_file)
    is_c1 = input_buffer.pop(0)  # First bit indicates whether it is c1 or c2
    k = ba2int(input_buffer[0:4]) + 1  # Following next 4 bits define word length.
    input_buffer = input_buffer[4:]

    output_buffer = bitarray()  # Buffer with ABC
    output_buffer.extend(''.join(initialize_abc(k)))

    current_index = 0
    while len(input_buffer) > current_index:
        zero_counter = 0
        try:
            while not input_buffer[current_index + zero_counter]:
                zero_counter += 1
        except IndexError:  # If the ending zeros reached
            break

        if is_c1:
            word_len = zero_counter * 2 + 1
            distance = generate_gamma_inv(input_buffer[current_index : current_index + word_len])

        else:
            u_length = 2 * zero_counter + 1
            m_k = generate_gamma_inv(input_buffer[current_index : current_index + u_length])
            word_len = 1 + m_k + 2 * int(log2(1 + m_k))
            distance = generate_delta_inv(input_buffer[current_index : current_index + word_len])

        if distance == 0:
            decoded_word = output_buffer[-k * (distance + 1):]
        else:
            decoded_word = output_buffer[-k * (distance + 1): -distance * k]

        output_buffer.extend(decoded_word)
        current_index += word_len

    output_buffer[(2 ** k) * k:].tofile(out_file)  # Output buffer without the added ABC
    print(f"FILE <{in_file.name}> DECOMPRESSED TO <{out_file.name}>")


# init
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='(De-)Compression using Universal coding algorithm.')
    parser.add_argument('-k', type=int, default=8, choices=range(2, 17),
                        help='Number raised by power of 2 for word length')
    parser.add_argument('--elias', choices=['gamma', 'delta', 'g', 'd'], type=str, default='g',
                        help='Type of encoding')
    parser.add_argument('--type', choices=['encode', 'decode', 'e', 'd'], type=str, required=True,
                        help='Type of operation')
    parser.add_argument('infile', nargs=1, type=argparse.FileType('rb'),
                        help='File to (de-)compress')
    parser.add_argument('outfile', nargs=1, type=argparse.FileType('wb'),
                        help='Output file for (de-)compression')

    args = parser.parse_args()

    if args.type == 'e' or args.type == 'encode':
        if args.elias == 'gamma' or args.elias == 'g':
            encode(args.infile[0], args.outfile[0], True, args.k)
        elif args.elias == 'delta' or args.elias == 'd':
            encode(args.infile[0], args.outfile[0], False, args.k)
    elif args.type == 'd' or args.type == 'decode':
        decode(args.infile[0], args.outfile[0])