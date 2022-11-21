# circlin6.0-api-python
써클인 앱(2022.6.29. 현재 6.0 버전) python api server

---


## Project Logs
- <b>2022.11.17(목)</b>
  - ```development_v2``` 브랜치 생성, 서버 개편 시작
    - 기존 main 브랜치는 Raw SQL을 실행하여 로직을 실행하고 있습니다.
    - 그러나 코드 가독성 & 유지/보수성 향상을 위해, 아래 내용을 주안점으로 두고 개편을 하고 있습니다.
      - PHP laravel -> Python flask 로 프레임워크 변경
      - 계층 구조를 도입하여 비즈니스 로직 ~ 데이터베이스의 결합을 최대한 느슨하게 하기
        - representation layer(```api```)
        - application layer(```services```)
        - Domain layer(```domain```)
        - Infrastructure(```adapter```)