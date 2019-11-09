# dmm-dyn4
Read status of and control a Dynamic Motor Motion DYN4 servo drive

This Python module is to read status from a DMM DYN4 servo drive using a serial connection.
I need this for monitoring torque-current in LinuxCNC but implemented all the read status commands.
The speed command is also implemented and will work if the drive is configured for RS232 control.
I didn't implemement more control commands because I didn't need them but they could be implemented
easily if someone is interested in testing them. I don't know how similar the DYN4 and DYN2 commands are.
As with similar code, use at your own risk. I plan to use this module in LinuxCNC userspace, but with some
work it could be made into a realtime component to help better synchronize reading from the drive with
LinuxCNC operations.
