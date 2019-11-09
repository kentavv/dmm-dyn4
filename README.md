# dmm-dyn4
Read status of and control a Dynamic Motor Motion DYN4 servo drive

This Python module is to read status from a DMM DYN4 servo drive using a serial connection.
I need this for monitoring torque-current but implemented all the read status commands.
The speed command is also implemented and will work if the drive is configured for RS232 control.
I didn't implemement more control commands because I didn't need them but they could be implemented
easily if someone is interested in testing them. I don't know how similar the DYN4 and DYN2 commands are.
As with similar code, use at your own risk.
