
| 영상 시청을 원할시 클릭 |
| ------ |
|[![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/helmet.png)](https://youtu.be/vrGrH6fPmb8)|

# 현장 안전 스마트 헬멧

- 14년을 기점으로 18년까지 꾸준히 사고 사망자수가 증가하고 있음을 확인할 수 있다. 사고사망자수는 2017년 964명에서 971명으로 소폭 증가했으며 이중에서 건설업이 485명으로 절반을 차지
- 공사장 근로자의 생명과도 직결되기 때문에 안전모는 현장에서 일하는 사람한테는 필수불가결한 존재
- 아무것도 보이지 않는 곳에서 일을 할 경우 위험을 감지하기 어려워 사건사고들이 빈번히 발생

| 사고 현황 |
| ------ |
|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/death_graph.png)|

| 부저 | 오실로스코프 결과 |
| ------ | ------ |
|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/buzzer.jpg)|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/buzzer2.jpg)|


| LED | 오실로스코프 결과 |
| ------ | ------ |
|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/led.jpg)|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/led2.jpg)|


| 진동센서 | 오실로스코프 결과 |
| ------ | ------ |
|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/vibration.png)|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/vibration2.jpg)|

| 초음파센서 | 오실로스코프 결과 |
| ------ | ------ |
|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/ultra.jpg)|![waiting](https://github.com/DunkHimYo/hard_hats_v2/blob/main/img/ultra2.jpg)|


## 해결 방안

- 사용자의 위험 정도를 부저와 LED를 통해 출력
- 진동센서로 사용자의 신체의 부담 정도를 측정
- 현장에 위험이 될수 있는 요인들을 가스 누수, 화상 등 사건에 대해 방지를 할 수 있는 센서들을 장착
- 사건의 현장 기록 및 사용자의 얼굴을 서버로 전송하여 응급 상황 판단

## 기대 효과

- 착용자는 헬멧으로 가스 와 불꽃을 감지할 수 있으며 어두운 환경일 경우 조도센서로 인식해서 LED를 통해 후방 협착 사고를 방지 할 수 있습니다.
- 현장에서는 최소 2인 1조를 원칙으로 하기 때문에 인명 피해 발생시 카메라 센서를 통해 촬영하여 서버로 보내 빠른 상태 파악을 할 수 있습니다.
- 서버에서 얼굴 인식을 하기 위해 haar classifier을 이용하여 얼굴을 인식하였으며 추가적으로 카메라센서로부터 서버에 실시간 전송하면 현장을 실시간 파악할 수 있습니다.
