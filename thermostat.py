"""
    THERMOSTAT APP V. 1.00
    ======================
    by Domen Gnezda
    
    For Raspberry PICO W + Waveshare Sensor Kit
    
    
    About:
    Thermostat app is a simulation of a thermostat application, using Raspberry
    PICO's built in temperature sensor, external color LED, red LED, pushbutton,
    potentiometer and 128*128 OLED screen.
    
    
    Instructions:
    
    - Set thermostat temperature with potentiometer.
    - Press Blue key (button) to exit app
    
    Room temperature (Temp) is represented on top line ("Temp: 20.0 C").
    Thermostat temperature setting is represented with big ASCII numbers.

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

"""

from machine import Pin, ADC, I2C
from neopixel import NeoPixel
import framebuf
import time


# SET PINS
inner_temp  =   ADC(4)
rgb_led_pin =   Pin(22, Pin.OUT)
rgb_led     =   NeoPixel(rgb_led_pin, 1) 
turn_key    =   ADC(Pin(27))
led         =   Pin(10, Pin.OUT)
key         =   Pin(3,Pin.IN,Pin.PULL_UP)
rgb_led[0]  =   (0, 30, 0)
rgb_led.write()


# ASCII NUM FONT
nums_small = [
    [".-.", "|\|", "`-'"],
    [" . ", "'| ", " ' "],
    [".-.", ".''", "`--"],
    ["-. ", "-| ", "-' "],
    [". .", "`-|", "  '"],
    [".-.", "``.", "--'"],
    [".-.", "|-.", "`-'"],
    [".-.", " .'", "'  "],
    [".-.", ")-(", "`-'"],
    [".-.", "`-|", "`-'"],
]


# OLED SCREEN DRIVER
class OLED(framebuf.FrameBuffer):
    def __init__(self, i2c_num=1, i2c_scl=7, i2c_sda=6, i2c_freq=1_000_000):
        
        self.width  = 128
        self.height = 128
        
        self.rotate = 180 #only 0 and 180

        self.olde_addr = 0x3d

        self.i2c = I2C(id=i2c_num, scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=i2c_freq)
        

        self.temp = bytearray(2)
        self.buffer = bytearray(self.height * self.width//2)

        super().__init__(self.buffer, self.width, self.height, framebuf.GS4_HMSB)
        self.init_display()
        
        self.white =   0xf
        self.balck =   0x0000
        
    def write_cmd(self, cmd):
        self.temp[0] = 0x00 
        self.temp[1] = cmd
        self.i2c.writeto(self.olde_addr, self.temp)

    def write_data(self, buf):
        self.i2c.writeto(self.olde_addr, b'\x40'+buf)
        
    def init_display(self):
        """Initialize display"""  
        
        self.write_cmd(0xae)     #--turn off oled panel

        self.write_cmd(0x15)     #  set column address
        self.write_cmd(0x00)     #  start column   0
        self.write_cmd(0x7f)     #  end column   127

        self.write_cmd(0x75)     #   set row address
        self.write_cmd(0x00)     #  start row   0
        self.write_cmd(0x7f)     #  end row   127

        self.write_cmd(0x81)     # set contrast control
        self.write_cmd(0x80) 

        self.write_cmd(0xa0)     # gment remap
        self.write_cmd(0x51)     #51

        self.write_cmd(0xa1)     # start line
        self.write_cmd(0x00) 

        self.write_cmd(0xa2)     # display offset
        self.write_cmd(0x00) 

        self.write_cmd(0xa4)     # rmal display
        self.write_cmd(0xa8)     # set multiplex ratio
        self.write_cmd(0x7f) 

        self.write_cmd(0xb1)     # set phase leghth
        self.write_cmd(0xf1) 

        self.write_cmd(0xb3)     # set dclk
        self.write_cmd(0x00)     #80Hz:0xc1 90Hz:0xe1   100Hz:0x00   110Hz:0x30 120Hz:0x50   130Hz:0x70     01
 
        self.write_cmd(0xab)     #
        self.write_cmd(0x01)     #

        self.write_cmd(0xb6)     # set phase leghth
        self.write_cmd(0x0f) 

        self.write_cmd(0xbe) 
        self.write_cmd(0x0f) 

        self.write_cmd(0xbc) 
        self.write_cmd(0x08) 

        self.write_cmd(0xd5) 
        self.write_cmd(0x62) 

        self.write_cmd(0xfd) 
        self.write_cmd(0x12) 

        time.sleep(0.1)
        self.write_cmd(0xAF);#--turn on oled panel

    def setwindows(self, Xstart, Ystart, Xend, Yend):
        if((Xstart > self.width) or (Ystart > self.height) or (Xend > self.width) or (Yend > self.height)):
            return
        self.write_cmd(0x15)
        self.write_cmd(Xstart//2)
        self.write_cmd(Xend//2 - 1)

        self.write_cmd(0x75)
        self.write_cmd(Ystart)
        self.write_cmd(Yend - 1)
        
    def show(self):
        self.setwindows(0, 0, 128, 128)
        self.write_data(self.buffer)
        return


def draw_screen(ambient_temp, set_temp):
        row = 8    # set row height
        first, second, third = convert_temp_to_str(round(set_temp, 1))

        # CALCULATE POWER LEVEL (#) STRING
        temp_diff = -(int(set_temp) - 25)
        spaces = ' ' * temp_diff
        hashes = (10 - temp_diff) * '#'
        level_string = hashes + spaces

        # DRAW UPDATED SCREEN
        OLED.fill(0x0)
        OLED.text("+--------------+",1,0*row,OLED.white)
        OLED.text("|              |",1,1*row,OLED.white)
        OLED.text("|              |",1,2*row,OLED.white)
        OLED.text(f"| Temp: {round(ambient_temp, 1)} C |",1,3*row,OLED.white)
        OLED.text("|              |",1,4*row,OLED.white)
        OLED.text("|              |",1,5*row,OLED.white)
        OLED.text("|              |",1,6*row,OLED.white)
        OLED.text(f"| {first[0]} {second[0]}  {third[0]} |",1,7*row,OLED.white)
        OLED.text(f"| {first[1]} {second[1]}  {third[1]} |",1,8*row,OLED.white)  #SSD1327
        OLED.text(f"| {first[2]} {second[2]}. {third[2]} |",1,9*row,OLED.white)
        OLED.text("|              |",1,10*row,OLED.white)
        OLED.text("|              |",1,11*row,OLED.white)
        OLED.text("|              |",1,12*row,OLED.white)
        OLED.text(f"|  {level_string}  |",1,13*row,OLED.white)
        OLED.text("|              |",1,14*row,OLED.white)
        OLED.text("+--------------+",1,15*row,OLED.white)
        
        OLED.show()


def get_temp():
    # GET TEMPERATURE FROM BUILTIN TEMPERATURE SENSOR AND CONVERT INTO CELSIUM
    adc_value = inner_temp.read_u16()
    volt = (3.3/65535) * adc_value
    temperature = 27 - (volt - 0.706)/0.001721
    return round(temperature, 2)


def set_rgb_led(temp):
    # SETS COLOR OF RGB LED REGARDING TO CHIP TEMPERATURE
    if temp > 23.5:
        rgb_led[0]=(0, 4, 0) # red
        rgb_led.write()
    elif temp > 23:
        rgb_led[0]=(2, 2, 0) # orange
        rgb_led.write()
    elif temp > 21:
        rgb_led[0]=(4, 0, 0) # green
        rgb_led.write()
    else:
        rgb_led[0]=(0, 0, 4) # blue
        rgb_led.write()


def convert_temp_to_str(temp):
    # CONVERT TEMPERATURE FLOAT INTO STRING LIST FOR EACH DIGIT
    temp = int(temp * 10)
    third_digit = temp % 10
    temp //= 10
    second_digit = temp % 10
    temp //= 10
    first_digit = temp
    first_digit_str_lst = nums_small[first_digit]
    second_digit_str_lst = nums_small[second_digit]
    third_digit_str_lst = nums_small[third_digit]
    return first_digit_str_lst, second_digit_str_lst, third_digit_str_lst


def get_thermostat():
    # GET VOLTAGE READING FROM POTENTIOMETER AND CONVERT IT TO TEMPERATURE
    # FORMAT IN CELSIUM
    voltage = turn_key.read_u16()*3.3/65535
    temperature = (1 - ((voltage - 0.02) / (3.3 - 0.02))) * (25 - 16) + 16
    return round(temperature, 1)


if __name__=='__main__':
    # INITIALIZE OLED SCREEN
    OLED = OLED()
    OLED.fill(0x0)
    OLED.show()

    # START MAIN LOOP - PRESS BLUE BUTTON TO EXIT
    while True:
        # READ TEMPERATURE SENSOR, THERMOSTAT KNOB SETTING
        thermostat = get_thermostat()
        ambient_temp = get_temp()

        # TURN ON "HEATING" IF THERMOSTAT IS SET HIGHER THAN ROOM TEMP
        if thermostat > ambient_temp:
            led.toggle()
        else:
            led.value(1)
            
        # SET RGB LED ACCORDING TO ROOM TEMP
        set_rgb_led(ambient_temp)

        # CHECK PUSHBUTTON FOR EXIT COMMAND
        if(key.value() == 0): 
            time.sleep_ms(5)
            if(key.value() == 0): 
                # DEINIT
                OLED.fill(0x0)
                OLED.show()
                rgb_led[0]=(0, 0, 0)
                rgb_led.write()
                led.value(1)
                break
        
        # DRAW SCREEN
        draw_screen(ambient_temp, thermostat)
        time.sleep(0.5)

