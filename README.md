# IoTTeamProject
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
