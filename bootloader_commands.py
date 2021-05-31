import serial
import time
import sys
from termcolor import colored

MAX_REPEAT_NUM = 30

ser = 0

ACK = b'\x79'
NACK = b'\x1f'

START_BOOTLOADER = b'\x7F'
ERASE_MEM_CMD = b'\x43\xBC'
WRITE_MEM_CMD = b'\x31\xCE'

GET_CHECKSUM = b'\xA1\x5E'
CRC_POLINOMIAL = b'\x04\xC1\x1D\xB7'
CRC_INITIAL = b'\xFF\xFF\xFF\xFF'

GET_COMMAND = b'\x00\xFF'

START_ADDR = 0x08000000

#checksum
def xor(data):
    res = 0
    for byte in data:
        res ^= byte
    return bytes([res])

def read_answer():
    global ser
    answer = ser.read(1)
    print(colored(answer.hex(), 'green'))
    return answer

def write_serial(bts):
    global ser
    print(colored(bts, 'blue'))
    ser.write(bts)

#RTS and DTR sequence
def serial_startup():
    global ser
    ser = serial.Serial(sys.argv[2], 115200,
        serial.EIGHTBITS, serial.PARITY_EVEN, serial.STOPBITS_ONE, timeout = 2)

    #burn2:
    ser.setRTS(False)
    ser.setDTR(False)
    ser.setDTR(True)
    time.sleep(0.5)

    #burn1:
    # ser.setRTS(False)
    # ser.setDTR(True)
    # time.sleep(0.3)
    # ser.setDTR(False)
    # time.sleep(0.3)

def serial_cleanup():
    global ser
    ser.setRTS(True)

#################################COMMANDS#####################################
def startup():
    global ser
    response = NACK
    for i in range(MAX_REPEAT_NUM):
        write_serial(START_BOOTLOADER)
        response = read_answer()
        if response == NACK:
            print("NACK")
            if i == MAX_REPEAT_NUM - 1:
                print("Startup error. Abort...")
                exit(0)
        elif response == ACK:
            print("Startup")
            break
        else:
            print(response)
            print("Startup error. Abort...")
            exit(0)

def global_erase():
    global ser
    response = NACK
    for i in range(MAX_REPEAT_NUM):
        write_serial(ERASE_MEM_CMD)
        write_serial(b'\xFF\x00')
        time.sleep(2)
        response = read_answer()
        if response == NACK:
            print("NACK")
            if i == MAX_REPEAT_NUM - 1:
                print("Erase error. Abort...")
                exit(0)
        elif response == ACK:
            print("Erase successful")
            break
        else:
            print(response)
            print("Erase error. Abort...")
            exit(0)

def write_memory_4bytes(hex_str):
    global ser
    addr = START_ADDR + int(hex_str[3:7], 16)
    addr = addr.to_bytes(4, 'big')
    hex_str = hex_str[9:-3]
    hex_str = bytes.fromhex(hex_str)
    write_serial(WRITE_MEM_CMD)
    write_serial(addr + xor(addr))
    N = bytes([len(hex_str) - 1])
    write_serial(N)
    write_serial(hex_str)
    write_serial(xor(N + hex_str))
    time.sleep(0.01)

def get_checksum(length):
    global ser
    addr = START_ADDR.to_bytes(4, 'big')
    length_bytes = length.to_bytes(4, 'big')
    sleep_val = 0.5

    write_serial(GET_CHECKSUM)
    time.sleep(sleep_val)
    read_answer()
    write_serial(addr + xor(addr))
    time.sleep(sleep_val)
    read_answer()
    write_serial(length_bytes + xor(length_bytes))
    time.sleep(sleep_val)
    read_answer()
    write_serial(CRC_POLINOMIAL + xor(CRC_POLINOMIAL))
    time.sleep(sleep_val)
    read_answer()
    write_serial(CRC_INITIAL + xor(CRC_INITIAL))
    read_answer()

    read_answer()
    read_answer()
    read_answer()
    read_answer()
    read_answer()

def get_command():
    global ser
    write_serial(GET_COMMAND)
    if read_answer() == ACK:
        while True:
            answer = read_answer()
            if answer == ACK or answer == NACK or answer == '':
                break