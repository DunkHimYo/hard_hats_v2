import io
#모듈 io 선언
import socket
#모듈 socket 선언
import struct
#모듈 struct 선언
from PIL import Image
#모듈 Image 선언
import cv2
#모듈 cv2 선언
import numpy as np
#모듈 np선언
import matplotlib.pyplot as plt
#모듈 matplotlib 선언
import atexit

def answer(conn):
#클라이언트의 대답을 수신 받는 함수
    data = conn.recv(10)
    print(data)
    #data 변수에 클라이언트로 부터 받은 데이터 수신
    if data.decode() == 'help':
    #받은 데이터가 'help'일 경우
        conn.send(b'chking')
        #클라이언트에게 0 송신
    else:
    #'help'가 아닐 경우
        conn.send(b'safe')
        #클라이언트에게 '1' 송신
        print(conn.recv(10))
        #괜찮은지 find 신호 여부 확인

def recv_capture(conn):
#사진 수신 처리 함수
    try:
    #해당 영역 내에 오류 발생시 except에 넘김
            connection = conn.makefile('rb')
            #connection 변수에 이미지 파일을 바이트 형태로 읽을 객체 생성
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            #image_len 변수에 클라이언트로 부터 받은 이미지의 크기 할당
            image_stream = io.BytesIO()
            #image_stream 변수에 BytesIO 객체 생성
            image_stream.write(connection.read(image_len))
            #image_stream에 image_len 크기만큼 파일을 읽어 들임
            image_stream.seek(0)
            #image_stream의 바이트 읽는 위치를 처음으로 설정

            image = Image.open(image_stream).convert('RGB')
            #image를 바이트 형태로 읽어와 RGB방식으로 변환함
            image = np.array(image)
            #image를 바이트 형태에서 10진수로 변환
            image = image[:, :, ::-1]
            #image내에 있는 데이터 가공
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            #image를 RGB 형태에서 BGR 형태로 변환
            face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
            #face_cascade변수에 얼굴을 인식할 수 있는 데이터를 받아옴
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #image_gray에 기존 이미지를 gray로 변환하여 할당
            faces = face_cascade.detectMultiScale(image_gray, 1.3, 5)
            #faces 변수에 인식된 얼굴 데이터 스케일링
            for (x, y, w, h) in faces:
            #검출된 얼굴 위치(x, y, w, h) 리스트 리턴
                cv2.rectangle(image, (x, y), (x + w,
                                              y + h), (255, 0, 0), 2)
                #cv2.rectangle을 이용하여 빨간색 테두리로 그림
                roi_gray = image_gray[y:y + h, x:x + w]
                roi_color = image[y:y + h, x:x + w]
                #사각형 테두리 영역 내의 이미지 컷

            if image_len:
            #이미지에 크기가 있을 경우
                plt.imshow(image)
                plt.show()
                #이지를 보여줌

    finally:
    #종료할 경우
        connection.close()
        #서버 연결 해제
def atexit_program():
    server_socket.close()


if __name__ == '__main__':
    server_socket = socket.socket()
    # TCP 통신을 위한 socket 객체 할당
    server_socket.bind(('192.168.137.1', 8000))
    # 연결할 IP주소 및 포트 번호 선언
    server_socket.listen(0)
    #클라이언트의 접속을 기다림
    conn, addr = server_socket.accept()
    #conn, addr 변수에 클라이언트가 접속할 경우 연결 정보 객체와 정보를 반환된 값을 할당
    
    vibration_chk = conn.recv(10)
    if vibration_chk == b'vibration_conn':
        conn.send(b'conn')
    else:
        conn.send(b'disconn')
        
    while True:
        if vibration_chk == b'vibration_conn':
            answer(conn)

        capture_chk = conn.recv(10)

        if capture_chk.decode()==b'camera_on':
            recv_capture(conn)


    atexit.register(atexit_program)
