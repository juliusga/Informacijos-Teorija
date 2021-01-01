# main.py @ Intervalinis-kodas
from math import log2
from bitarray import bitarray
from bitarray.util import int2ba, ba2int
import itertools
import os
# 1 bitas - c1 ? c2 = 0 ? 1
# 4 bitai - k

# For printing the files in binary format
def print_file_binary(file):
    with open(file, mode='rb') as f:
        file_buffer = bitarray()
        file_buffer.fromfile(f)
        print("File <" + file + ">:", file_buffer.to01(), "\n")


def generate_gamma(index: int):
    #uk = 000...000(k+1)_2
    zeros = '0' * int(log2(index + 1))
    number = bin(index + 1)[2:]
    gamma_array = bitarray(zeros + number)
    return gamma_array


#C2
def generate_delta(index: int):
    # v_k_s = u_[log2(k+1)] + (k+1)_2
    m_k = int(log2(index + 1))
    delta_array = generate_gamma(m_k)
    k_part = int2ba(index+1)
    delta_array.extend(k_part)
    delta_array.pop(len(delta_array) - m_k - 1)
    return delta_array


def generate_gamma_inv(element: bitarray):
    while element[0] != True:
        element.pop(0)
    return ba2int(element) - 1


def generate_delta_inv(element: bitarray):
    if len(element) == 1:
        return 0
    zero_counter = 0
    while element[0] != True:
        element.pop(0)
        zero_counter += 1
    element.pop(0)
    for i in range(zero_counter):
        element.pop(0)
    element.insert(0, True)
    return ba2int(element) - 1


def initialize_abc(k: int):
    return [''.join(seq) for seq in itertools.product('01', repeat=k)]


def encode(file:str, is_c1: bool, k: int):
    out_buffer = bitarray()
    out_buffer.append(is_c1)
    out_buffer.extend(int2ba(k-1, length=4))
    #  First bit indicates whether it is c1 or c2
    #  Following next 4 bits define word length.

    pcode_gen_func = generate_gamma if is_c1 else generate_delta
    #  Select p code generator function.

    with open(file, mode='rb') as f:
        input_buffer = bitarray()
        input_buffer.extend(''.join(initialize_abc(k))) #  Fill with ABC.
        input_buffer.fromfile(f) #  Fill with data from file.
        buffer_len = len(input_buffer)
        
        for word_index in range(k * 2**k, buffer_len, k): #  start from file beginning.
            word = input_buffer[word_index:word_index + k]
            for prev_word_index in range(word_index, 0, -k): #  Read from abc beginning to the current index.
                prev_word = input_buffer[prev_word_index-k:prev_word_index]
                if word == prev_word:
                    out_buffer.extend(pcode_gen_func(word_index//k - prev_word_index//k))
                    break

    with open(file + '.compressed', mode='wb') as out:
        out_buffer.tofile(out)


def decode(file: str):
    with open(file, mode='rb') as f:
        input_buffer = bitarray()
        input_buffer.fromfile(f)
        is_c1 = input_buffer.pop(0)         # First bit indicates whether it is c1 or c2
        k = ba2int(input_buffer[0:4]) + 1   # Following next 4 bits define word length.
        input_buffer = input_buffer[4:]

        output_buffer = bitarray()          # Buffer with ABC
        output_buffer.extend(''.join(initialize_abc(k)))

        while len(input_buffer) != 0:
            zero_counter = 0
            try:
                while input_buffer[zero_counter] != True:
                    zero_counter += 1
            except IndexError:              # If the ending zeros reached
                break

            if is_c1:
                word_len = zero_counter * 2 + 1
                distance = generate_gamma_inv(input_buffer[0:word_len])

            else:
                u_lenght = 2 * zero_counter + 1
                m_k = generate_gamma_inv(input_buffer[0:u_lenght])
                word_len = 1 + m_k + 2 * int(log2(1 + m_k))
                distance = generate_delta_inv(input_buffer[0:word_len])

            if distance == 0:
                decoded_word = output_buffer[-k * (distance + 1):]
            else:
                decoded_word = output_buffer[-k * (distance + 1): -distance * k]

            output_buffer.extend(decoded_word)
            input_buffer = input_buffer[word_len:]  # Pop the read word out of the buffer

    file_name_ext = os.path.splitext(file)[0]              # Split the file name.(extension) and the .compressed
    file_name, ext = os.path.splitext(file_name_ext)       # Split the file name and the real extension
    with open(file_name + '_decompressed' + ext, mode='wb') as out:
        output_buffer[(2 ** k) * k:].tofile(out)    # Output buffer without the added ABC
        print("FILE", '<' + file + '>', "DECOMPRESSED TO", '<' + file_name + '_decompressed' + ext + '>')

        
# init
if __name__ == "__main__":
    if False:
        print("gamma:")
        for i in range(10):
            gamma = generate_gamma(i)
            print('u' + str(i), "=>", gamma.copy())
            print(gamma.copy(), "=>", 'u' + str(generate_gamma_inv(gamma.copy())))
            print()
    
    if False:
        print("delta:")
        for i in range(10):
            delta = generate_delta(i)
            print('v' + str(i), "=>", delta.copy())
            print(delta.copy(), "=>", 'v' + str(generate_delta_inv(delta.copy())))
            print()

    decode('test_gamma.txt.compressed')
        
    decode('test_delta.txt.compressed')

    decode("image_delta.bmp.compressed")

    decode("image_gamma.bmp.compressed")

