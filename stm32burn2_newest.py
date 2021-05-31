from bootloader_commands import *

def print_statusbar(current, total):
    div = current/total
    if div <= 0.1:
        print('[█---------]{}%'.format(int(div * 100)))
    elif div <= 0.2:
        print('[██--------]{}%'.format(int(div * 100)))
    elif div <= 0.3:
        print('[███-------]{}%'.format(int(div * 100)))
    elif div <= 0.4:
        print('[████------]{}%'.format(int(div * 100)))
    elif div <= 0.5:
        print('[█████-----]{}%'.format(int(div * 100)))
    elif div <= 0.6:
        print('[██████----]{}%'.format(int(div * 100)))
    elif div <= 0.7:
        print('[███████---]{}%'.format(int(div * 100)))
    elif div <= 0.8:
        print('[████████--]{}%'.format(int(div * 100)))
    elif div <= 0.9:
        print('[█████████-]{}%'.format(int(div * 100)))
    elif div <= 1:
        print('[██████████]{}%'.format(int(div * 100)))

def write_memory(hex_file):
    counter = 1
    for hex_str in hex_file:
        print_statusbar(counter, len(hex_file))
        counter+=1
        response = NACK
        for i in range(MAX_REPEAT_NUM):
            write_memory_4bytes(hex_str)
            response = read_answer()
            if response == NACK:
                print("NACK")
                if i == MAX_REPEAT_NUM - 1:
                    print("Write error. Abort...")
                    exit(0)
            elif response == ACK:
                print("ACK")
                break
            else:
                print("Write error. Abort...")
                exit(0)
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python3 stm32burn.py hex_file device")
        exit(0)

    serial_startup()

    hex_file = open(sys.argv[1], 'r')
    hex_file = hex_file.readlines()
    hex_file = hex_file[1:-2]

    startup()
    global_erase()
    write_memory(hex_file)
    print("Write successfull")
    exit(0)
