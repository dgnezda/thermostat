THERMOSTAT APP V. 1.00
======================
by Domen Gnezda

For Raspberry PICO W + Waveshare Sensor Kit


About:
Thermostat app is a simulation of a thermostat application, using Rasberry
PICO's built in temperature sensor, external color LED, red LED, pushbutton,
potentiometer and 128*128 OLED screen.


Instructions:

- Set thermostat temperature with potentiometer.
- Press Blue key (button) to exit app

Put one finger onto the Raspberry Pico microprocessor chip to warm it up
and see the room temperature (Temp) rise - chip temperature is used for this
reading.

If thermostat temperature is set above room temperature, a red LED will
start to blink, representing the ON state of an imaginary heating system.
An additional color LED is used as feedback to be able to quickly assert
room temperature. The colors used are BLUE for cold, GREEN for normal,
ORANGE for warm, RED for hot.

A so called "power bar" of # symbols is used as additional visual feedback 
to represent the setting of the thermostat. More #-s means warmer.

Example of OLED screen reading:

    +--------------+
    |              |
    | Temp: 20.0 C |
    |              |
    | .-. .-.  .-. |
    | .'' |\|  |\| |
    | `-- `-'. `-' |
    |              |
    |  ######      |
    +--------------+


* If used with non "W" PICO model, make sure to use correct PIN numbers!
* OLED driver Class by Waveshare (make of Sensor kit) is used.
