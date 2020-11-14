#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import ctypes

from ReadWriteMemory import ReadWriteMemory
from ReadWriteMemory import ReadWriteMemoryError

'''
    This code was made by TrikzMe for Cain532's challenge.

    Dependencies:
                https://github.com/vsantiago113/ReadWriteMemory => python setup.py install

    Challenge:
        ~Week 1~
          Build some sort of Health 'manipulation' function (Get Creative!)
            -> Assign health value depending of time of the day

        ~Week 2~
          Build some sort  of Currency 'manipulation' function (Get Creative!)
            -> ammo/items values to current hour:minute

        ~Week 3~
          Build a unique function that nobody has seen before! 
            -> reverse damages

    Special thanks to L'In20Cible for his help!
'''

rwm = ReadWriteMemory()
Process = rwm.get_process_by_name('mgsi.exe')
Process.open()

# - Functions by my friend "L'In20Cible" to patch the c_uint to c_ushort in the original function
def ReadWithType(self, lp_base_address, value, type='c_uint'):
    """
    Read data from the process's memory.
    :param lp_base_address: The process's pointer
    :return: The data from the process's memory if succeed if not raises an exception.
    """
    try:
        read_buffer = ctypes.c_uint()
        lp_buffer = ctypes.byref(read_buffer)
        n_size = ctypes.sizeof(read_buffer)
        lp_number_of_bytes_read = ctypes.c_ulong(0)
        ctypes.windll.kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(lp_base_address), lp_buffer, n_size, lp_number_of_bytes_read)
        return read_buffer.value
    except (BufferError, ValueError, TypeError) as error:
        if self.handle:
            self.close()
        self.error_code = self.get_last_error()
        error = {'msg': str(error), 'Handle': self.handle, 'PID': self.pid,
                 'Name': self.name, 'ErrorCode': self.error_code}
        ReadWriteMemoryError(error)

def WriteWithType(self, lp_base_address, value, type='c_uint'):
    """
    Write data to the process's memory.
    :param lp_base_address: The process' pointer.
    :param value: The data to be written to the process's memory
    :return: It returns True if succeed if not it raises an exception.
    """
    try:
        write_buffer = getattr(ctypes, type)(value)
        lp_buffer = ctypes.byref(write_buffer)
        n_size = ctypes.sizeof(write_buffer)
        lp_number_of_bytes_written = ctypes.c_ulong(0)
        ctypes.windll.kernel32.WriteProcessMemory(self.handle, ctypes.c_void_p(lp_base_address), lp_buffer, n_size, lp_number_of_bytes_written)
        return True
    except (BufferError, ValueError, TypeError) as error:
        if self.handle:
            self.close()
        self.error_code = self.get_last_error()
        error = {'msg': str(error), 'Handle': self.handle, 'PID': self.pid,
                 'Name': self.name, 'ErrorCode': self.error_code}
        ReadWriteMemoryError(error)

NameAddress=0x00675810
# Life=0x0072382E
# CapLife=0x0078E7F6
Life=0x0078E7F6
CapLife=0x0078E7F8
CurrentItem=0x0078E7FE
Items = {"Bandana": 0x0078E840,
        "Body Armor": 0x0078E83A,
        "Camera": 0x0078E842,
        "Cardboard Box A - To Heliport": 0x0078E82E,
        "Cardboard Box B - To Nuclear Warhead Storage Building": 0x0078E830,
        "Cardboard Box C - To Snowfield": 0x0078E832,
        "Cigarette": 0x0078E82A,
        "Diazepam": 0x0078E848,
        "Gas Mask": 0x0078E838,
        "Goggles": 0x0078E82C,
        "Handkerchief":0x0078E856,
        "ID Card": 0x0078E84C,
        "Mine Detector": 0x0078E850,
        "Ketchup": 0x0078E83C,
        "MO Disc": 0x0078E852,
        "Medicine": 0x0078E846,
        "Night Vision Goggles": 0x0078E834,
        "PAL Card Key": 0x0078E84A,
        "Ration": 0x0078E844,
        "Rope": 0x0078E854,
        "Stealth": 0x0078E83E,
        "Suppressor":0x0078E858,
        "Thermal Goggles": 0x0078E836
}
Weapons = {"C4": 0x0078E80E,
        "Chaff": 0x0078E812,
        "Claymore": 0x0078E80C,
        "Famas": 0x0078E804,
        "Grenade": 0x0078E806,
        "Nikita": 0x0078E808,
        "PSG1": 0x0078E814,
        "Socom": 0x0078E802,
        "Stinger": 0x0078E80A,
        "Stun": 0x0078E810
}

# - Username
UsernameQuery=''
while UsernameQuery == '':
    UsernameQuery = input(' - Please enter your username: \n(not too long because it may overwrite existing data) \n')
    if UsernameQuery != '':
        # - Clear the terminal
        clear = lambda: os.system('cls')
        clear()
        print('Hi ' + UsernameQuery + '!\nEnjoy :)\n\n*CTRL+C to exit*')
        NumberOfBytes=4
        UsernameBytesList=[]
        for i in range(0,len(UsernameQuery),NumberOfBytes):
            UsernameBytesList.append(UsernameQuery[i:i+NumberOfBytes]) # Add every 4 characters to the list
            UsernameToBytesArray = bytearray.fromhex(''.join(hex(ord(x))[2:] for x in UsernameQuery[i:i+NumberOfBytes])) # Convert username string to bytes array
            # - Original way of processing read and write because this uses 4 bytes:
            Process.write(NameAddress + i,int.from_bytes(UsernameToBytesArray, byteorder='little', signed=False)) # Write each 4 bytes

def MainFunction():
    # - Cap life reading and formatting
    CapLifeValue = ReadWithType(Process, CapLife, 'c_ushort')
    CapLifeValueToHex = (CapLifeValue).to_bytes(4, byteorder='big').hex()[4:]
    CapLifeValueToDec = int(CapLifeValueToHex, 16)

    CurrentTime = time.strftime("%H%M") # What's the current time (hour and minutes only)?

    TimePourcentage = ((100 * int(CurrentTime)) / 2400) # Calculating the pourcentage of the current time, example: if it's 12:00 -> 100 x 1200 / 2400 = 50%
    NewLifeValue = ((int(TimePourcentage) * int(CapLifeValueToDec)) / 100) # Calculating the new life value based on the time pourcentage over the cap life value, example:
    # 50 x 256 / 100 = 128
    # 50 is 50% previously calculated - 256 is the cap life value - 128 is 256/2
    WriteWithType(Process, Life, int(NewLifeValue), 'c_ushort')

    HourMinutes = hex(int(CurrentTime, 16))[2:].zfill(2) # Formatting the time value to HEX

    # - For each weapons and Ration item, assign the current time value
    for Item, ItemAddress in Items.items():
        if Item == 'Ration':
            WriteWithType(Process, ItemAddress, int(HourMinutes[:2]), 'c_ushort')
            WriteWithType(Process, ItemAddress + 0x16, int(HourMinutes[2:]), 'c_ushort')
    for Weapon, WeaponAddress in Weapons.items():
        WriteWithType(Process, WeaponAddress, int(HourMinutes[:2]), 'c_ushort')
        WriteWithType(Process, WeaponAddress + 0x14, int(HourMinutes[2:]), 'c_ushort')

    CurrentItemValue = ReadWithType(Process, CurrentItem, 'c_ushort')
    if CurrentItemValue == 13:
        # - Reverse damages if the player have Ration equiped
        WriteWithType(Process, 0x004531EE, 0xba850f, 'c_ushort') # Reverse damages
    else:
        WriteWithType(Process, 0x004531EE, 0xba840f, 'c_ushort') # Default damages
    time.sleep(1) # Wait 1 sec
while True:
    MainFunction()

Process.close()