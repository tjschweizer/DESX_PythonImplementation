# This is a python implementation of DESX. This is for my learning purposes only.
# Based on http://page.math.tu-berlin.de/~kant/teaching/hess/krypto-ws2006/des.htm
# Test with https://paginas.fe.up.pt/~ei10109/ca/des.html
import math, sys, gc

# DES Constants
# Key Permutation PC1
PC1 = [57, 49, 41, 33, 25, 17, 9,
       1, 58, 50, 42, 34, 26, 18,
       10, 2, 59, 51, 43, 35, 27,
       19, 11, 3, 60, 52, 44, 36,
       63, 55, 47, 39, 31, 23, 15,
       7, 62, 54, 46, 38, 30, 22,
       14, 6, 61, 53, 45, 37, 29,
       21, 13, 5, 28, 20, 12, 4]
# Key Permutation PC2
PC2 = [14, 17, 11, 24, 1, 5,
       3, 28, 15, 6, 21, 10,
       23, 19, 12, 4, 26, 8,
       16, 7, 27, 20, 13, 2,
       41, 52, 31, 37, 47, 55,
       30, 40, 51, 45, 33, 48,
       44, 49, 39, 56, 34, 53,
       46, 42, 50, 36, 29, 32]
# Initial Message Permutation
IP = [58, 50, 42, 34, 26, 18, 10, 2,
      60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6,
      64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17, 9, 1,
      59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5,
      63, 55, 47, 39, 31, 23, 15, 7]
# Ebit Selection Table
EBIT = [32, 1, 2, 3, 4, 5,
        4, 5, 6, 7, 8, 9,
        8, 9, 10, 11, 12, 13,
        12, 13, 14, 15, 16, 17,
        16, 17, 18, 19, 20, 21,
        20, 21, 22, 23, 24, 25,
        24, 25, 26, 27, 28, 29,
        28, 29, 30, 31, 32, 1]

# S Boxes
S1 = [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
      [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
      [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
      [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]]

S2 = [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
      [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
      [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
      [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]]

S3 = [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
      [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
      [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
      [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]]

S4 = [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
      [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
      [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
      [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]]

S5 = [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
      [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
      [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
      [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]]

S6 = [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
      [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
      [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
      [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]]

S7 = [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
      [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
      [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
      [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]]

S8 = [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
      [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
      [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
      [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]

SP = [16,7,20,21,
      29,12,28,17,
      1,15,23,26,
      5,18,31,10,
      2,8,24,14,
      32,27,3,9,
      19,13,30,6,
      22,11,4,25]

def utf8len(s):
    # https://stackoverflow.com/questions/30686701/python-get-size-of-string-in-bytes
    return len(s.encode('utf-8'))


def xorBinaryString(str1, str2):
    tmpInt1 = eval("0b" + str1)
    tmpInt2 = eval("0b" + str2)
    xorInt = tmpInt1 ^ tmpInt2
    xorString = eval('f"{xorInt:0' + str(len(str1)) + 'b}"')
    return xorString


def byteArrayToBinaryString(arr):
    binString = ""
    for i in range(len(arr)):
        binString += f"{arr[i]:08b}"
    return binString


def bitstring_to_bytes(s):
    # https://stackoverflow.com/questions/32675679/convert-binary-string-to-bytearray-in-python-3
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')


def bitshiftBinaryString(s, iter):
    tmpString = s
    for j in range(iter):
        outputString = ""
        for i in range(len(tmpString) - 1):
            outputString += tmpString[i + 1]
        outputString += tmpString[0]
        tmpString = outputString
    return outputString


def calc_desx(messageString, keyString):
    # first pad message and key to a multiple of 16 bytes
    # messageString = bytearray(messageString.encode())
    # keyString = bytearray(keyString.encode())
    messageString_length = len(messageString)
    keyString_length = len(keyString)
    numBlocks = math.ceil(messageString_length / 16)
    blocks = []
    for i in range(numBlocks):
        blocks.append(messageString[i * 16:(i + 1) * 16])
    extraMessageBytes = 16 - messageString_length % 16
    extraKeyBytes = 16 - keyString_length % 16
    if (extraMessageBytes != 0) and (extraMessageBytes != 16):
        for i in range(extraMessageBytes):
            messageString += b'\0'
    if (extraKeyBytes != 0) and (extraKeyBytes != 16):
        for i in range(extraKeyBytes):
            keyString += b'\0'

    # next split into for loop for each block of 16 bytes
    for block in blocks:

        # Now we create our left and right half block:
        leftBlock = block[:8]
        rightBlock = block[8:]

        # Now we create the 56 bit actual key as a binary string
        tmpKeyString = byteArrayToBinaryString(keyString)

        # Then we permute the key using PC-1
        permKey = ""
        for j in range(len(PC1)):
            permKey += tmpKeyString[PC1[j] - 1]

        # then split the permutated string into two halves
        C = []
        D = []
        C.append(permKey[:28])
        D.append(permKey[28:])
        # next calculate bitshifted keys
        keyIterArray = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
        for j in range(16):
            C.append(bitshiftBinaryString(C[j], keyIterArray[j]))
            D.append(bitshiftBinaryString(D[j], keyIterArray[j]))

        # Now we create keys Kn n=1:16 using PC-2
        Kn = []
        for j in range(16):
            tmpString = ""
            CnDn = C[j + 1] + D[j + 1]
            for k in range(len(PC2)):
                tmpString += CnDn[PC2[k] - 1]
            Kn.append(tmpString)

        # subkeys have been created. Now we begin encoding the data.
        # first clean up some variables
        del ([CnDn, extraKeyBytes, extraMessageBytes, i, j, k, keyIterArray, keyString_length, leftBlock,
              messageString_length, permKey, rightBlock, tmpString, tmpKeyString, numBlocks])
        gc.collect()

        # Initial Permutation of block
        permMessage = ""
        binaryMessageString = byteArrayToBinaryString(messageString)
        for index in IP:
            permMessage += binaryMessageString[index - 1]

        # Now we begin the actual message encoding
        # Initialize Variables
        L = []
        R = []
        L.append(permMessage[:32])
        R.append(permMessage[32:])
        for i in range(16):
            # Ln = R(n-1)
            L.append(R[i])
            # Rn = L(n-1) + f(Rn-1,Kn). We need to calculator f(Rn-1,Kn) first
            # First expand Rn-1 from 32 to 48 bits using EBIT
            Etmp = ""
            for bit in EBIT:
                Etmp += R[i][bit - 1]
            K0 = xorBinaryString(Kn[i], Etmp)

            SB0=""
            for j in range(8):
                B=K0[j*6:(j+1)*6]
                SB=(eval("S"+str(j+1)+'[eval("0b" + B[0]+B[5])][eval("0b" + B[1:5])]'))
                SB0+=f"{SB:04b}"

            f=""
            for index in SP:
                f+=SB0[index-1]
            R.append(xorBinaryString(L[i],f))
        print("break")


if __name__ == '__main__':
    calc_desx(bytearray(b'\x01\x23\x45\x67\x89\xAB\xCD\xEF'), bytearray(b'\x13\x34\x57\x79\x9B\xBC\xDF\xF1'))
