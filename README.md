라즈베리파이 핀맵 http://www.dreamy.pe.kr/zbxe/files/attach/images/1209/923/768/003/ae9486b726825a307d431cc0fdc2597e.png

mcp3008 핀 배치 https://m.blog.naver.com/PostView.nhn?blogId=roboholic84&logNo=220367321777&proxyReferer=https%3A%2F%2Fwww.google.com%2F


미세먼지 센서 회로도 https://cafe.naver.com/mechawiki/33

초록색 - adc in

검정색 - led 조절 핀 GPIO2

정책 설명
https://docs.aws.amazon.com/ko_kr/iot/latest/developerguide/pub-sub-policy.html
https://docs.aws.amazon.com/ko_kr/iot/latest/developerguide/iot-moisture-tutorial.html
host 주소
azjctapxbp7sc-ats.iot.ap-northeast-2.amazonaws.com

# IoTTeamProject

fsr 2개, 온도 센서로 부터 생성되는 기능들 추가해야함

hand free 아니고 자동차에 부모 있는 상황을 초기상황으로 가정하고 방치기능 구현했음

온도에 따른 방치시간 설정, 아기가 카시트에 있는지 확인해야할듯

온습도 센서 예제
https://m.blog.naver.com/chandong83/220902795488

RFID 실행 환경 설정 방법
https://www.instructables.com/id/RFID-RC522-Raspberry-Pi/%20https://github.com/lthiery/SPI-Py.git



pc 
핸드폰


라즈베리파이1 --5

발찌(온도, 심박)


라즈베리파이2 --6

카시트(온도, 미세먼지, 서보모터, 감압센서 , 열선패드)


라즈베리파이3

차량(감압센서)

유모차 뼈대(서보모터, rfid 리더기)





미리 데우기 coap
파이1 pub --- 파이2 sub
파이1 pub --- pc sub
pc pub --- 파이2 sub


실시간 온도조절 mqtt	
파이1 pub ---- 파이2 sub	---- /anklet/temp


유모차 방치 알림 mqtt
파이3(뼈대)  --rfid-- pc 
파이3(뼈대) pub --- 파이2 sub  ----- /stroller/handfree
파이2 pub --- pc sub ------ /car_seat/neglect


차량 방치 알림 mqtt
파이3(차량) pub ---- 파이2 sub -----  /car/parent 
파이2 pub ---- pc sub ----------- /car_seat/neglect






핸드폰 거치 강제 기능
 rfid 기능

추가 요청할 센서 및 
빵판 3개
150옴 막대저항
220uf 캐패시터

mcp3008 3개

모스펫 1개
