#!/usr/bin/env python

# Copyright 2019 Kent A. Vander Velden <kent.vandervelden@gmail.com>
#
# If you use this software, please consider contacting me. I'd like to hear
# about your work.
#
# This file is part of DMM-DYN4.
#
#     DMM-Dyn4 is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     DMM-DYN4 is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with DMM-DYN4.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import print_function

import time
import serial

import numpy as np


def sign_extend(value, bits):
    # from: https://stackoverflow.com/a/32031543
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


class DMMException(Exception):
    def __init__(self):
        Exception.__init__(self)


class DMMExceptionUnexpectedLength(DMMException):
    def __init__(self, n, expected_n):
        DMMException.__init__(self)
        self.n = n
        self.expected_n = expected_n


class DMMExceptionTruncatedWrite(DMMException):
    def __init__(self, n, expected_n):
        DMMException.__init__(self)
        self.n = n
        self.expected_n = expected_n


class DMMExceptionUnknownFunctionID(DMMException):
    def __init__(self, func_id):
        DMMException.__init__(self)
        self.func_id = func_id


class DMMExceptionUnknownFunctionID(DMMException):
    def __init__(self, func_id):
        DMMException.__init__(self)
        self.func_id = func_id


class DMMExceptionUnexpectedFunc(DMMException):
    def __init__(self):
        DMMException.__init__(self)


class DMMDrive:
    def __init__(self, serial_dev, drive_id):
        self.serial = serial.Serial(serial_dev,
                                    38400,
                                    timeout=None,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS)
        self.drive_id = drive_id

        # print(dir(self.serial))

        self.flush()
        # print(serial.VERSION)
        # print(self.serial.isOpen())
        self.debug = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.serial.close()

    def flush(self):
        self.serial.flushInput()
        self.serial.timeout = .05
        while self.serial.read(1) != '':
            pass

    @staticmethod
    def verify_func_id(func_id):
        if not (0x10 <= func_id <= 0x1b or func_id == 0x1e):
            raise DMMExceptionUnknownFunctionID(func_id)

    def general_read2(self, func_id2):
        packet = [0x00 | self.drive_id,
                  0x80 | (0 << 5) | func_id2,
                  0x80]
        packet += [0x80 | (sum(packet) & 0x7f)]

        if self.debug:
            print([hex(x) for x in packet])

        packet = bytearray(packet)
        n = self.serial.write(packet)

        if n != len(packet):
            raise DMMExceptionTruncatedWrite(n, len(packet))

    host_fids = {
        'Set_Origin': 0x00,
        'Go_Absolute_Pos': 0x01,
        'Make_LinearLine': 0x02,
        'Go_Relative_Pos': 0x03,
        'Make_CircularArc': 0x04,
        'Assign_Drive_ID': 0x05,
        'Read_Drive_ID': 0x06,
        'Set_Drive_Config': 0x07,
        'Read_Drive_Config': 0x08,
        'Read_Drive_Status': 0x09,
        'Turn_ConstSpeed': 0x0a,
        'Square_Wave': 0x0b,
        'Sin_Wave': 0x0c,
        'SS_Frequency': 0x0d,
        'General_Read': 0x0e,
        'ForMotorDefine': 0x0f,
        'Set_MainGain': 0x10,
        'Set_SpeedGain': 0x11,
        'Set_IntGain': 0x12,
        'Set_TrqCons': 0x13,
        'Set_HighSpeed': 0x14,
        'Set_HighAccel': 0x15,
        'Set_Pos_OnRange': 0x16,
        'Set_GearNumber': 0x17,
        'Read_MainGain': 0x18,
        'Read_SpeedGain': 0x19,
        'Read_IntGain': 0x1a,
        'Read_TrqCons': 0x1b,
        'Read_HighSpeed': 0x1c,
        'Read_HighAccel': 0x1d,
        'Read_Pos_OnRange': 0x1e,
        'Read_GearNumber': 0x1f}

    dyn_fids = {
        'Is_MainGain': 0x10,
        'Is_SpeedGain': 0x11,
        'Is_IntGain': 0x12,
        'Is_TrqCons': 0x13,
        'Is_HighSpeed': 0x14,
        'Is_HighAccel': 0x15,
        'Is_Drive_ID': 0x16,
        'Is_Pos_OnRange': 0x17,
        'Is_GearNumber': 0x18,
        'Is_Status': 0x19,
        'Is_Config': 0x1a,
        'Is_AbsPos32': 0x1b,
        'Is_TrqCurrent': 0x1e}

    def read_MainGain(self):
        self.general_read2(self.host_fids['Read_MainGain'])
        return self.check_response(self.dyn_fids['Is_MainGain'])

    def read_SpeedGain(self):
        self.general_read2(self.host_fids['Read_SpeedGain'])
        return self.check_response(self.dyn_fids['Is_SpeedGain'])

    def read_IntGain(self):
        self.general_read2(self.host_fids['Read_IntGain'])
        return self.check_response(self.dyn_fids['Is_IntGain'])

    def read_TrqCons(self):
        self.general_read2(self.host_fids['Read_TrqCons'])
        return self.check_response(self.dyn_fids['Is_TrqCons'])

    def read_HighSpeed(self):
        self.general_read2(self.host_fids['Read_HighSpeed'])
        return self.check_response(self.dyn_fids['Is_HighSpeed'])

    def read_HighAccel(self):
        self.general_read2(self.host_fids['Read_HighAccel'])
        return self.check_response(self.dyn_fids['Is_HighAccel'])

    def read_Pos_OnRange(self):
        self.general_read2(self.host_fids['Read_Pos_OnRange'])
        return self.check_response(self.dyn_fids['Is_Pos_OnRange'])

    def read_GearNumber(self):
        self.general_read2(self.host_fids['Read_GearNumber'])
        return self.check_response(self.dyn_fids['Is_GearNumber'])

    def read_Status(self):
        self.general_read2(self.host_fids['Read_Drive_Status'])
        return self.check_response(self.dyn_fids['Is_Status'])

    def read_Config(self):
        self.general_read2(self.host_fids['Read_Drive_Config'])
        return self.check_response(self.dyn_fids['Is_Config'])

    def read_AbsPos32(self):
        self.general_read(self.dyn_fids['Is_AbsPos32'])
        return self.check_response(self.dyn_fids['Is_AbsPos32'])

    def read_TrqCurrent(self):
        self.general_read(self.dyn_fids['Is_TrqCurrent'])
        return self.check_response(self.dyn_fids['Is_TrqCurrent'])

    def set_Config(self):
        func_id2 = self.host_fids['Set_Drive_Config']
        # Toggling the enable bit (b5) does not effect the drive (only tested in analog mode)
        cnf = ((0 << 6) |    # TBD
               (1 << 5) |    # b5 = 0 : let Drive servo
                             # b5 = 1 : let Drive free, motor could be turned freely
               (0x01 << 3) | # b4 b3 = 0 : Position servo as default
                             #         1 : Speed servo
                             #         2 : Torque servo
                             #         3 : TBD
               (0 << 2) |    # b2 = 0 : works as relative mode(default) like normal optical encoder
                             # b2 = 1 : works as absolute position system, motor will back to absolute zero or POS2(Stored in
                             #          sensor) automatically after power on reset.
               (0x03 << 0))  # b1 b0 = 0 : RS232 mode
                             #         1 : CW,CCW mode
                             #         2 : Pulse/Dir or (SPI mode Optional)
                             #         3 : Anlog mode
        packet = [0x00 | self.drive_id,
                  0x80 | (0 << 5) | func_id2,
                  0x80 | cnf]
        
        packet += [0x80 | (sum(packet) & 0x7f)]

        if self.debug:
            print([hex(x) for x in packet])

        packet = bytearray(packet)
        n = self.serial.write(packet)

        if n != len(packet):
            raise DMMExceptionTruncatedWrite(n, len(packet))

    def check_response(self, expected_func_id, max_attempts=3):
        for i in range(max_attempts):
            func_id, v = self.read_response()
            if func_id == expected_func_id:
                break
        if i == max_attempts:
            raise DMMExceptionUnexpectedFunc()

        return v

    def general_read(self, func_id):
        self.verify_func_id(func_id)

        packet = [0x00 | self.drive_id,
                  0x80 | (0 << 5) | 0x0e,
                  0x80 | (func_id & 0x7f)]
        packet += [0x80 | (sum(packet) & 0x7f)]

        if self.debug:
            print([hex(x) for x in packet])

        packet = bytearray(packet)
        n = self.serial.write(packet)

        if n != len(packet):
            raise DMMExceptionTruncatedWrite(n, len(packet))

    def read_response(self):
        if self.debug:
            print('read response')

        self.serial.timeout = .05

        arr = []
        first_byte = False
        expected_len = 0
        timed_out = False
        while True:
            x = self.serial.read(1)
            if x == '':
                # timeout occured
                timed_out = True
                break
            x = ord(x)
            first_byte = (x & 0x80) == 0
            if first_byte:
                if self.debug:
                    print('first byte')
                first_byte = True
                expected_len = 0
                arr = []

            arr += [x]
            if len(arr) == 2:
                expected_len = 4 + ((x >> 5) & 0x03)

            # x = x & 0x7f
            if self.debug:
                print(hex(x))

            if len(arr) == expected_len:
                break

        if timed_out:
            return False

        if self.debug:
            print(expected_len, len(arr), [hex(x) for x in arr])

        def verify_length(arr, expected_n):
            n = (arr[1] >> 5) & 0x03
            # print(hex(arr[1]), n, expected_n)
            if n != expected_n:
                raise DMMExceptionUnexpectedLength(n, expected_n)

        if arr and expected_len == len(arr):
            drive_id = arr[0] & 0x7f
            func_id = arr[1] & 0x1f

            crc_check = ((sum(arr[:-1]) ^ arr[-1]) & 0x7f) == 0
            if self.debug:
                print(crc_check)
                print(hex(func_id))
            if crc_check:
                if 0x00 <= func_id <= 0x0a or 0x1e < func_id:
                    print('Unallowed address read:', func_id)
                elif func_id == 0x10:
                    # Is_MainGain
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x11:
                    # Is_SpeedGain
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x12:
                    # Is_IntGain
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x13:
                    # Is_TrqCons
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x14:
                    # Is_HighSpeed
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x15:
                    # Is_HighAccel
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x16:
                    # Is_Drive_ID
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x17:
                    # Is_Pos_OnRange
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f

                elif func_id == 0x18:
                    # Is_GearNumber
                    verify_length(arr, 3)
                    # self.debug = True
                    # print([hex(x) for x in arr])
                    # x = self.read_signed_val(arr)
                    # self.debug = False
                    x = [((arr[2] & 0x7f) << 7) | (arr[3] & 0x7f),
                         ((arr[4] & 0x7f) << 7) | (arr[5] & 0x7f)]

                elif func_id == 0x19:
                    # Is_Status
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f
                    d = {}

                    if x & (1 << 0):
                        d['in position'] = '0 (motor busy, or |Pset - Pmotor|> OnRange)'
                        d['in position'] = '0'
                    else:
                        d['in position'] = '1 (On position, i.e. |Pset - Pmotor| < = OnRange)'
                        d['in position'] = '1'

                    if x & (1 << 1):
                        d['motor'] = 'motor free'
                    else:
                        d['motor'] = 'motor servo'

                    x2 = (x >> 2) & 0x7
                    if x2 == 0:
                        d['alarm'] = 'No alarm'
                        d['alarm'] = ''
                    elif x2 == 1:
                        d['alarm'] = 'motor lost phase alarm, |Pset - Pmotor|>8192(steps), 180(deg)'
                        d['alarm'] = 'lost phase'
                    elif x2 == 2:
                        d['alarm'] = 'motor over current alarm'
                        d['alarm'] = 'over current'
                    elif x2 == 3:
                        d['alarm'] = 'motor overheat alarm, or motor over power'
                        d['alarm'] = 'overheat or over power'
                    elif x2 == 4:
                        d['alarm'] = 'there is error for CRC code check, refuse to accept current command'
                        d['alarm'] = 'corrupt command'
                    elif x2 > 4:
                        d['alarm'] = 'TBD'

                    if x & (1 << 5):
                        d['motion'] = 'busy (means built in S-curve, linear, circular motion is busy on current motion)'
                        d['motion'] = 'busy'
                    else:
                        d[
                            'motion'] = 'completed (means built in S-curve, linear, circular motion completed; waiting for next motion)'
                        d['motion'] = 'completed'

                    if x & (1 << 6):
                        d['pin2'] = '1 (pin2 status of JP3,used for Host PC to detect CNC zero position or others)'
                        d['pin2'] = '1'
                    else:
                        d['pin2'] = '0 (pin2 status of JP3,used for Host PC to detect CNC zero position or others)'
                        d['pin2'] = '0'

                    x = d

                elif func_id == 0x1a:
                    # Is_Config
                    verify_length(arr, 0)
                    x = arr[2] & 0x7f
                    print(hex(x))
                    d = {}

                    x2 = x & 0x03
                    if x2 == 0:
                        d['input mode'] = 'RS232 mode'
                        d['input mode'] = 'RS232'
                    elif x2 == 1:
                        d['input mode'] = 'CW/CCW mode'
                        d['input mode'] = 'CW/CCW'
                    elif x2 == 2:
                        d['input mode'] = 'Pulse/Dir or (SPI mode Optional)'
                        d['input mode'] = 'pulse/dir'
                    elif x2 == 3:
                        d['input mode'] = 'Analog mode'
                        d['input mode'] = 'analog'

                    if x & (1 << 2):
                        d['positioning'] = 'works as absolute position system, motor will back to absolute zero or POS2(Stored in sensor) automatically after power on reset.'
                        d['positioning'] = 'absolute'
                    else:
                        d['positioning'] = 'relative mode(default) like normal optical encoder'
                        d['positioning'] = 'relative'

                    x2 = (x >> 3) & 0x03
                    if x2 == 0:
                        d['servo mode'] = 'Position servo as default'
                        d['servo mode'] = 'position'
                    elif x2 == 1:
                        d['servo mode'] = 'Speed servo'
                        d['servo mode'] = 'speed'
                    elif x2 == 2:
                        d['servo mode'] = 'Torque servo'
                        d['servo mode'] = 'torque'
                    elif x2 == 3:
                        d['servo mode'] = 'TBD'

                    if x & (1 << 5):
                        d['enabled'] = 'let drive servo'
                        d['enabled'] = 'yes'
                    else:
                        d['enabled'] = 'let Drive free, motor could be turned freely'
                        d['enabled'] = 'no'

                    if x & (1 << 6):
                        d['b6'] = '1 TBD'
                    else:
                        d['b6'] = '0 TBD'

                    x = d

                elif func_id == 0x1b:
                    # Is_AbsPos32
                    x = self.read_signed_val(arr)

                elif func_id in [0x1c, 0x1d]:
                    print('Unknown address read:', func_id)

                elif func_id == 0x1e:
                    # Is_TrqCurrent
                    x = self.read_signed_val(arr)

        return func_id, x

    def read_signed_val(self, arr):
        arr2 = arr[2:-1]

        x = sign_extend(arr2[0] << 1, 8) >> 1
        if self.debug:
            print('first byte', [hex(arr2[0]), hex(x), x])

        for y in arr2[1:]:
            x = (x << 7) + (y & 0x7f)

        if self.debug:
            print(x, [hex(x_) for x_ in arr2])

        return x

    def measure_speed(self, integration_time=.1):
        p1 = self.read_AbsPos32()
        time.sleep(integration_time)
        p2 = self.read_AbsPos32()
        encoder_ppr = 65536.
        rpm = (p2 - p1) / integration_time * 60. / encoder_ppr
        return rpm

    def set_speed(self, rpm):
        packet = [0x00 | self.drive_id,
                  0x80 | (3 << 5) | 0x0a,
                  0x80 | ((rpm >> (7 * 3)) & 0x7f),
                  0x80 | ((rpm >> (7 * 2)) & 0x7f),
                  0x80 | ((rpm >> (7 * 1)) & 0x7f),
                  0x80 | ((rpm >> (7 * 0)) & 0x7f)]
        packet += [0x80 | (sum(packet) & 0x7f)]

        if self.debug:
            print([hex(x) for x in packet])

        packet = bytearray(packet)
        n = self.serial.write(packet)

        if n != len(packet):
            raise DMMExceptionTruncatedWrite(n, len(packet))

    def integrate_TrqCurrent(self, max_dt=1.):
        st = time.time()
        dt = 0.
        arr = []
        while dt < max_dt:
            arr += [self.read_TrqCurrent()]
            dt = time.time() - st

        # = [dmm.read_TrqCurrent() for _ in range(100)]
        # print(arr)
        d = {'min': np.min(arr), 'max': np.max(arr), 'mean': np.mean(arr), 'median': np.median(arr),
             'stddev': np.std(arr)}
        print(d)

        arr = np.abs(arr)
        d = {'min': np.min(arr), 'max': np.max(arr), 'mean': np.mean(arr), 'median': np.median(arr),
             'stddev': np.std(arr)}
        print(d)


def main():
    with DMMDrive('/dev/ttyUSB0', 0) as dmm:
        d = {}
        d['Status'] = dmm.read_Status()

        d['MainGain'] = dmm.read_MainGain()
        d['SpeedGain'] = dmm.read_SpeedGain()
        d['IntGain'] = dmm.read_IntGain()
        d['TrqCons'] = dmm.read_TrqCons()
        d['HighSpeed'] = dmm.read_HighSpeed()
        d['HighAccel'] = dmm.read_HighAccel()
        d['Pos_OnRange'] = dmm.read_Pos_OnRange()
        d['GearNumber'] = dmm.read_GearNumber()
        d['Status'] = dmm.read_Status()
        d['Config'] = dmm.read_Config()
        d['AbsPos32'] = dmm.read_AbsPos32()
        d['TrqCurrent'] = dmm.read_TrqCurrent()

        dmm.set_speed(50)
        time.sleep(.5)
        d['Speed'] = dmm.measure_speed()

        print(d)

        dmm.integrate_TrqCurrent()


if __name__ == "__main__":
    main()
