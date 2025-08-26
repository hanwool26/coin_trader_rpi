# Coin Trader RPI

업비트(Upbit) API를 활용한 자동화 암호화폐 거래 시스템입니다. 라즈베리파이에서 실행되도록 설계되었으며, 다양한 거래 전략을 지원합니다.

## 🏗️ 시스템 아키텍처

### 전체 구조
```
coin_trader_rpi/
├── main.py                 # 메인 진입점
├── src/                    # 핵심 소스 코드
│   ├── manager.py         # 전체 시스템 관리자
│   ├── socket_server.py   # 클라이언트 통신 서버
│   ├── autotrade.py      # 자동 거래 엔진
│   ├── event_infinite.py  # 무한 매수 전략
│   ├── event_couple.py    # 연동 거래 전략
│   ├── event.py          # 기본 이벤트 클래스
│   ├── coin.py           # 코인 정보 관리
│   ├── account.py        # 업비트 계정 연동
│   ├── util.py           # 유틸리티 함수
│   ├── report.py         # 거래 리포트 생성
│   └── log.py            # 로깅 시스템
├── tests/                 # 테스트 코드
│   ├── conftest.py       # 테스트 설정 및 fixture
│   ├── test_*.py         # 각 모듈별 테스트
│   └── test_integration.py # 통합 테스트
├── tool/                  # 도구 및 설정
│   ├── systemd/          # systemd 서비스 설정
│   └── profit_sum.sh     # 수익 계산 스크립트
├── requirements.txt       # Python 의존성
├── pytest.ini           # pytest 설정
├── Makefile             # 테스트 및 빌드 명령어
├── run_tests.py         # 테스트 실행 스크립트
└── install.sh            # 설치 스크립트
```

## 🚀 주요 기능

### 1. 거래 전략
- **무한 매수 전략 (EventInfinite)**: RSI 기반 분할 매수 및 동적 매도
- **연동 거래 전략 (EventCouple)**: 두 코인 간의 상관관계를 활용한 거래
- **자동 거래 (AutoTrade)**: RSI와 거래량 기반 자동 코인 선별 및 거래

### 2. 핵심 컴포넌트

#### Manager 클래스
- 전체 거래 시스템의 중앙 제어
- 계정 관리, 이벤트 생성/제거, 자산 업데이트
- 소켓 서버와의 통신 관리

#### Socket Server
- 클라이언트와의 JSON 기반 통신
- 실시간 거래 명령 처리
- 연결 상태 관리

#### Event System
- **EventInfinite**: RSI 기반 무한 매수 전략
  - 동적 간격 조정 (4~48시간)
  - 분할 매수 (PER_BUY 단위)
  - 단계별 매도 (2%, 3%, 4%, 5% 수익률)
- **EventCouple**: 연동 거래 전략
  - 주요 코인과 연계 코인의 상관관계 활용
  - 3단계 거래 강도 (welldone, medium, rare)

### 3. 거래 로직

#### 무한 매수 전략
```python
# RSI 기준값
RSI_UPSTD = 60    # RSI 상한선
RSI_DOWNSTD = 20  # RSI 하한선

# 매도 마진
SELL_MARGIN = [1.02, 1.03, 1.04, 1.05]  # 2%, 3%, 4%, 5%
```

#### 자동 거래
- RSI 20-60 범위 내 코인 선별
- 거래량 기준 정렬
- 최소 가격 1원 이상 필터링
- 중복 거래 방지

## 🧪 테스트 환경

### 테스트 실행
```bash
# 모든 테스트 실행
make test

# 단위 테스트만
make test-unit

# 통합 테스트만
make test-integration

# 커버리지 포함
make coverage

# 전체 테스트 파이프라인
python run_tests.py
```

### 테스트 커버리지
- 목표: 80% 이상
- HTML 리포트: `htmlcov/` 디렉토리
- 터미널 리포트: `--cov-report=term-missing`

자세한 테스트 가이드는 [TESTING.md](TESTING.md)를 참조하세요.

## 🔧 설치 및 실행

### 시스템 요구사항
- 라즈베리파이 (Raspberry Pi)
- Python 3.x
- 업비트 API 키 (Access Key, Secret Key)

### 설치 방법
```bash
# 1. 저장소 클론
git clone <repository_url>
cd coin_trader_rpi

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 권한 설정 및 설치
sudo chmod +x install.sh
sudo ./install.sh
```

### 서비스 관리
```bash
# 서비스 시작
sudo systemctl start coin_trade.service

# 서비스 상태 확인
sudo systemctl status coin_trade.service

# 서비스 중지
sudo systemctl stop coin_trade.service
```

## 📊 API 통신

### 클라이언트 명령어
- `do_start`: 거래 시작
- `do_stop`: 거래 중지
- `account`: 계정 연결
- `auto_trade_start`: 자동 거래 시작
- `auto_trade_stop`: 자동 거래 중지
- `request_asset`: 자산 정보 요청

### 응답 형식
```json
{
  "command": "asset_update",
  "asset": 1000000
}
```

## 📈 거래 전략 상세

### 무한 매수 전략
1. **초기 매수**: 설정된 잔고로 첫 매수 실행
2. **동적 간격**: 시장 상황에 따른 매수 간격 조정
3. **분할 매수**: PER_BUY 단위로 단계별 매수
4. **단계별 매도**: 수익률에 따른 차등 매도

### 연동 거래 전략
1. **모니터링**: 주요 코인과 연계 코인 가격 변화 감시
2. **매수 시점**: 주요 코인 상승 시 연계 코인 매수
3. **매도 조건**: 목표 수익률 달성 시 매도

## 🛠️ 개발 환경

### 의존성
- `pyupbit`: 업비트 API 클라이언트
- `numpy`: 수치 계산
- `pandas`: 데이터 처리
- `requests`: HTTP 통신

### 개발 도구
- `pytest`: 테스트 프레임워크
- `pytest-cov`: 커버리지 분석
- `black`: 코드 포맷팅
- `flake8`: 코드 린팅
- `mypy`: 타입 체크

### 로깅
- 실시간 거래 로그
- 월별 거래 리포트 (`/usr/share/coin_trade/output/`)
- 시스템 상태 모니터링

## 🔒 보안 고려사항

- API 키는 환경변수나 설정 파일로 관리
- 네트워크 통신은 로컬 소켓 기반
- 거래 제한 및 위험 관리 로직 포함

## 📝 라이센스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다. 실제 거래에 사용하기 전에 충분한 테스트와 검증이 필요합니다.

## ⚠️ 주의사항

- 암호화폐 거래는 높은 위험을 수반합니다
- 실제 자금으로 거래하기 전에 페이퍼 트레이딩으로 전략 검증
- API 키 보안에 주의
- 거래소의 이용약관 및 정책 준수

## 🤝 기여

버그 리포트, 기능 제안, 코드 개선 등 모든 기여를 환영합니다.

### 기여 가이드
1. 이슈 생성 또는 기존 이슈 확인
2. 포크 후 기능 브랜치 생성
3. 코드 작성 및 테스트 추가
4. 커버리지 80% 이상 유지
5. Pull Request 생성

---

**개발자**: hanwool26@gmail.com  
**최종 업데이트**: 2024년
