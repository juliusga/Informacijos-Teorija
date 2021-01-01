from math import log2
from bitarray import bitarray
from bitarray.util import int2ba

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

    # init
if __name__ == "__main__":
    print("gamma:")
    for i in range(10):
        print('u' + str(i), generate_gamma(i))
    print("delta:")
    for i in range(10):
        print('v' + str(i), generate_delta(i))
    pass