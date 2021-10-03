import pulseio
import digitalio
import board
from collections import deque
import numpy as np
import io
import socket
import struct
import time
import spidev
import threading

class helmet():
    def __init__(self,ip_addr=None,port_num=None,input_pin_number:dict={},output_pin_number:dict={}):

        self.flame_thread=None
        self.gas_thread=None
        self.distance_thread=None
        self.client_thread=None
        self.state_thread=None

        self._input_pin_number_setting(input_pin_number)
        self._output_pin_number_setting(output_pin_number)

        self.state = {'flame': False, 'gas': False, 'vibration': False, 'distance': False, 'camera': False}
        self.state_thread =  threading.Thread(target=self.state_output)

        if ip_addr is not None or port_num is not None:
            """
            소켓 통신 연결
            """
            self.client_socket = socket.socket()
            self.client_socket.connect((ip_addr, port_num))
            self.client_thread=threading.Thread(target=self.client)

    def __del__(self):
        self.client_socket.close()

    def _input_pin_number_setting(self,pin_number:dict):
        """
            센서핀 세팅
        """
        if all([i  in pin_number.keys() for i in ('trig','echo')]):
            self.trig = digitalio.DigitalInOut(pin_number['trig'])
            self.echo = digitalio.DigitalInOut(pin_number['echo'])
            self.trig.direction = digitalio.Direction.OUTPUT
            self.echo.diriection = digitalio.Direction.INPUT
            self.client_thread = threading.Thread(target=self.chking_distance)

        if 'gas_pin' in pin_number.keys():
            self.gas_pin =  digitalio.DigitalInOut(pin_number['gas_pin'])
            self.gas_pin.direction = digitalio.Direction.INPUT
            self.gas_thread = threading.Thread(target=self.gas_detect)
            
        if 'flame_pin' in pin_number.keys():
            self.flame_pin =  digitalio.DigitalInOut(pin_number['flame_pin'])
            self.flame_pin.direction = digitalio.Direction.INPUT
            self.flame_thread = threading.Thread(target=self.flame_detect)

        if 'life_button' in pin_number.keys():
            self.life_button = digitalio.DigitalInOut(pin_number['life_button'])
            self.life_button.direction = digitalio.Direction.INPUT
            self.life_button.pull = digitalio.Pull.UP

        if 'ultra_button' in pin_number.keys():
            self.ultra_button = digitalio.DigitalInOut(pin_number['ultra_button'])
            self.ultra_button.direction = digitalio.Direction.INPUT
            self.ultra_button.pull = digitalio.Pull.UP

        if 'vibration' in pin_number.keys():
            self.vibration_pin = digitalio.DigitalInOut(board.D12)
            self.vibration_pin.direction = digitalio.Direction.INPUT
            self.vibration_sum = 1.0
            self.sec_sum = 1.0

        if 'illuminance' in pin_number.keys():
            self.spi=spidev.SpiDev()
            self.spi.open(0,0)
            self.spi.max_speed_hz=1350000

    def _output_pin_number_setting(self, pin_number):
        """
            출력 핀 세팅
        """
        if 'buz' in pin_number.keys():
            self.buz = digitalio.DigitalInOut(pin_number['buz'])
            self.buz.direction = digitalio.Direction.OUTPUT

        if 'front_red_pin' in pin_number.keys():
            self.front_red_pin = digitalio.DigitalInOut(pin_number['front_red_pin'])
            self.front_red_pin.direction = digitalio.Direction.OUTPUT

        if 'front_green_pin' in pin_number.keys():
            self.front_green_pin = digitalio.DigitalInOut(pin_number['front_green_pin'])
            self.front_green_pin.direction = digitalio.Direction.OUTPUT

        if 'front_blue_pin' in pin_number.keys():
            self.front_blue_pin = digitalio.DigitalInOut(pin_number['front_blue_pin'])
            self.front_blue_pin.direction = digitalio.Direction.OUTPUT

        if 'rear_light_pin' in pin_number.keys():
            self.rear_light_pin = digitalio.DigitalInOut(pin_number['rear_light_pin'])
            self.rear_light_pin.direction = digitalio.Direction.OUTPUT

    def analog_read(self,channel):
        """
            디지털 신호 아날로그 변환
        """
        r=self.spi.xfer2([1,(8+channel)<<4,0])
        adc_out=((r[1]&3)<<8)+r[2]
        return adc_out

    def turn_off_front_led(self):
        """
            헬멧 앞부분 LED OFF
        """
        self.front_red_pin.value = True
        self.front_blue_pin.value = False
        self.front_green_pin.value = False

    def turn_on_front_ledR(self):
        """
            헬멧 앞부분 LED RED ON
        """
        self.front_red_pin.value = True
        self.front_blue_pin.value = False
        self.front_green_pin.value = False

    def turn_on_front_ledB(self):
        """
            헬멧 앞부분 LED BLUE ON
        """
        self.front_red_pin.value = False
        self.front_blue_pin.value = True
        self.front_green_pin.value = False

    def turn_on_front_ledG(self):
        """
            헬멧 앞부분 LED Green ON
        """
        self.front_red_pin.value = True
        self.front_blue_pin.value = False
        self.front_green_pin.value = False

    def chking_distance(self):
        """
            이전 거리와 현재 거리의 간격 Threshold
        """
        max_index = 2
        buffer = deque()
        threshold = 5

        safe_distance_chking_button = False

        while True:

            if not self.ultra_button.value:
                safe_distance_chking_button ^= True

            if safe_distance_chking_button == True:
                if len(buffer) < max_index:
                    buffer.append(self.get_distance())

                else:
                    for i in range(len(buffer) - 1):
                        buffer[i] = abs(buffer[i + 1] - buffer[i])

                    calculation_range = np.array(buffer)[:-1]
                    #p = sum(numpy.array(calculation_range) >= threshold) / len(calculation_range)

                    if any(calculation_range >= threshold):
                        self.state['distance']=True

                    else:
                        self.state['distance']=False

                    buffer.popleft()
            else:
                self.state['distance']=False


    def get_distance(self):
        """
            초음파를 이용한 거리 예측
        """
        self.trig.value = False
        time.sleep(0.5)
        self.trig.value = True
        time.sleep(0.00001)  # 10us
        self.trig.value = False

        while self.echo.value == 0:
            pulse_begin = time.time()

        while self.echo.value == 1:
            pulse_end = time.time()

        duration = float(pulse_end - pulse_begin)
        distance = (340 * (duration / 2)) * 100;
        return distance

    def client(self):
        """
            서버에 상태 전송
        """
        self.connection = self.client_socket.makefile('wb')

        self.client_socket.send(b'vibration_conn')
        rcv_data = self.client_socket.recv(100)

        while True:
            if rcv_data==b'conn':
                self.vibration_chking()

            self.camera_chking()


    def state_output(self):
        """
            현재 상태 출력
        """
        state={'flame': False, 'gas': False, 'vibration': False, 'distance': False, 'camera': False}

        while True:
            if self.state['camera']:
                self.turn_on_front_ledB()

            elif any(self.state.values()):
                self.turn_on_front_ledR()
            else:
                self.turn_on_front_ledG()

            time.sleep(1)
            self.state = state

    def vibration_chking(self):
        """
            진동 센서를 이용한 신체 부담 경우 계산
        """
        self.vibration_sum += int(self.vibration_pin.value)
        self.sec_sum += 1
        time.sleep(1)
        life_sign = self.sec_sum // self.vibration_sum

        if self.sec_sum == 180:
            self.vibration_sum = 1.0
            self.sec_sum = 1.0

        if life_sign >= 10:
            self.client_socket.send(b'help')

        else:
            self.client_socket.send(b'fine')

        rcv_data = self.client_socket.recv(100)

        if rcv_data.decode() == b'chking':

            self.state['vibration'] = True

            while not self.life_button.value == 0:
                pass

            self.client_socket.send(b'find')

            self.state['vibration'] = False

            self.sec_sum = 1.0
            self.vibration_sum = 1.0

        else:
            self.state['vibration'] = False
            self.client_socket.send(b'find')


    def camera_chking(self):
        """
            카메라 버튼을 이용한 서버 사진 전송
        """
        start_time = time.time()

        while not self.life_button.value == 1:
            pass

        result_time = float(time.time() - start_time)

        if result_time >= 3:

            self.client_socket.send(b'camera_on')

            with picamera.PiCamera() as camera:
                camera.resolution = (640, 480)

                time.sleep(1)

                stream = io.BytesIO()
                camera.capture(stream, 'jpeg')

                self.connection.write(struct.pack('<L', stream.tell()))
                self.connection.flush()

                stream.seek(0)
                self.connection.write(stream.read())

                stream.seek(0)
                stream.truncate()

        else:
            self.client_socket.send(b'camera_off')

    def ambient_light_chking(self):
        """
            조도 센서를 이용한 후면 LED ON OFF
        """
        illuminance_value=self.analog_read(1)
        voltage=illuminance_value*3.3/1024

        if voltage > 900:
            self.rear_light_pin.value=True

        else:
            self.rear_light_pin.value=False

    def gas_detect(self):
        """
            유해 가스 감시
        """
        while True:
            if self.gas_sensor:
                self.state['gas']=False
            else:
                self.state['gas'] = True

    def flame_detect(self):
        """
            불꽃 감지
        """
        while True:
            if self.flame_sensor:
                self.state['flame']=False
            else:
                self.state['flame'] = True


if __name__ == '__main__':
    H=helmet(ip_addr='write ip addr',port_num='write port num',input_pin_number={},output_pin_number={})

    H.flame_thread.start()
    H.gas_thread.start()
    H.client_thread.start()
    H.state_thread.start()

    H.flame_thread.join()
    H.gas_thread.join()
    H.client_thread.join()
    H.state_thread.join()

