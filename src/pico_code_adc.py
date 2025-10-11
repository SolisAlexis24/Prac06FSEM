# ## #############################################################
#
# src/pico-code-adc.py
#
# Author: Mauricio Matamoros
# Date:
#
# ## ############################################################
from machine import ADC, Pin     # Board Analogic-to-Digital Converter
from utime import sleep_ms       # Delay function in milliseconds

V_ADC = 3.3

def setup():
    '''
        Setup the Pico ADC channels
    '''
    global adcm, adcp
    adcm = ADC(Pin(26))         # Init ADC0
    adcp = ADC(Pin(27))         # Init ADC1
# end def

def read_temp():
    '''
        Reads temperature in C from the ADC
    '''
    # The actual temperature
    vplus  = adcp.read_u16()
    # The reference temperature value, i.e. 0°C
    vminus = adcm.read_u16()
    # Calculate the difference. when V+ is smaller than V- we have negative temp
    vdiff  = vplus - vminus
    # Then, we need to convert values from codes to V and then to temperature in °C
    # To compute V from codes, we need to multiply by the conversion factor V = codes * 3.3/2^(16)-1
    # To convert given V into °C, we need to recall that for LM35 1°C = 0.01V
    # Temp = 0.01 * Codes * 3.3/65535 -> Temp = codes * 3.3/655.35
    temp = vdiff * V_ADC / 655.35
    return temp
# end def


def read_avg_temp(count=10):
    '''
        Gets the average of N temperature reads
    '''
    avgtemp = 0
    for i in range(count):
        avgtemp += read_temp()
    return avgtemp / count
# end def


def main():
    setup()
    while(True):                      # Repeat forever
        temp = read_avg_temp()        # Fetch temperature
        print(f'Temp: {temp:0.2f}°C') # Print temperature
        sleep_ms(1000)                # Wait for 1000ms
#end def

if __name__ == '__main__':
     main()
