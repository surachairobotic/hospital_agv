import serial, time, keyboard

class Controller():
    def __init__(self, port='COM3'):
        self.left_id = 2
        self.right_id = 1

        # Open serial port at "COM3" with a baud rate of 115200
        self.ser = serial.Serial(port, baudrate=115200)

    # Define a function to calculate the Modbus CRC
    def modbus_crc(self, data):
        crc = 0xFFFF
        for i in data:
            crc = crc ^ i
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc = crc >> 1
        return crc

    def decimal2hex(self, dec):
        return hex(dec & (2**16-1))[2:]

    #def readRegister(self, id, function_code='03', start_addr='202C', register_num=1):
    #    return self.cmd(id, function_code='03', start_addr, register_num)

    def cmd(self, id=2, function_code='06', register_addr='203A', register_value=100):
        hx = self.decimal2hex(register_value)
        res = str(id).zfill(2) + function_code + register_addr + str(hx).zfill(4)
        res = bytes.fromhex(res)

        # Calculate the Modbus CRC of the data and append it to the end as a bytes object
        crc = self.modbus_crc(res)
        crc_bytes = crc.to_bytes(2, byteorder='little')
        res += crc_bytes

        return res

    def forward(self, speed=100):
        self.move(speed, speed)

    def move(self, spdL=100, spdR=100):
        # Convert the hex string to a bytes object
        cmdL = self.cmd(id=self.left_id, register_value=spdL)
        cmdR = self.cmd(id=self.right_id, register_value=-spdR)

        self.ser.write(cmdL)
        time.sleep(0.0005)
        self.ser.write(cmdR)

    def __del__(self):
        # Close the serial port
        self.ser.close()

robot = Controller()

limit=10
spd = 0
mode=0
t=time.time()
t2=time.time()
while True:
    if spd > limit or spd < -limit:
        spd = 0
    if keyboard.is_pressed('q'):
        spd=0
        robot.forward(0)
        robot.forward(0)
        robot.forward(0)
        break
    elif keyboard.is_pressed('a'):
        mode=1
    elif keyboard.is_pressed('d'):
        mode=2
    elif keyboard.is_pressed('s'):
        mode=0
    elif keyboard.is_pressed('up'):
        spd=spd+1
    elif keyboard.is_pressed('down'):
        spd=spd-1
    elif keyboard.is_pressed('0'):
        spd=0
    if spd>limit:
        spd=limit
    elif spd<-limit:
        spd=-limit
    if time.time()-t > 1.0:
        print('Current Speed : ' + str(spd))
        robot.forward(spd)
        t=time.time()
    if time.time()-t2 > 0.1:
        if mode is 0:
            robot.forward(spd)
        elif mode is 1:
            robot.forward(0)
            time.sleep(0.01)
            robot.move(spd, -spd)
        elif mode is 2:
            robot.forward(0)
            time.sleep(0.01)
            robot.move(-spd, spd)
        t2=time.time()
    time.sleep(0.01)
