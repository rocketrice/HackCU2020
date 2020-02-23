# from gpiozero import AngularServo
# from time import sleep
#
# servo = AngularServo(12, min_angle=-42, max_angle=44)
# while True:
#     servo.min()
#     sleep(1)
#     servo.mid()
#     sleep(1)
#     servo.max()
#     sleep(1)
#     servo.angle = 40
#     sleep(1)
#     servo.angle = 20
#     sleep(1)
#     servo.angle = 0
#     sleep(1)
#     servo.angle = -20
#     sleep(1)
#     servo.angle = -40

"""
Demonstration of how to control servo pulses with RPIO.PWM
RPIO Documentation: http://pythonhosted.org/RPIO
"""
from RPIO import PWM

servo = PWM.Servo()

# Add servo pulse for GPIO 17 with 1200µs (1.2ms)
servo.set_servo(18, 1200)

# Add servo pulse for GPIO 17 with 2000µs (2.0ms)
servo.set_servo(18, 2000)

# Clear servo on GPIO17
servo.stop_servo(18)