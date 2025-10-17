# sv_to_ipxact

SystemVerilog 모듈을 IP-XACT 컴포넌트 정의로 변환하는 도구입니다. AMBA 버스 프로토콜을 자동으로 인식하고 busInterface와 portMap을 생성합니다.

## 주요 기능

- SystemVerilog 모듈 파서 (ANSI 및 non-ANSI 스타일 지원)
- AMBA (AMBA2~5) 및 JEDEC DFI4 프로토콜 정의 라이브러리
- 자동 버스 인터페이스 매칭 (신호 prefix 기반)
- 동적 라이브러리 로딩 및 캐싱
- IP-XACT (IEEE 1685-2009, 2014, 2022) XML 생성

## 설치

```bash
# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는: venv\Scripts\activate  # Windows

# 패키지 설치
pip install -e .
```

## 사용법

### 기본 사용

```bash
# 입력 파일만 지정 (출력: design.ipxact)
sv_to_ipxact -i design.sv

# 출력 파일 지정
sv_to_ipxact -i design.sv -o output.xml

# 라이브러리 캐시 재생성
sv_to_ipxact -i design.sv --rebuild

# IP-XACT 2009 표준 사용
sv_to_ipxact -i design.sv --ipxact-2009

# IP-XACT 2022 표준 사용
sv_to_ipxact -i design.sv --ipxact-2022

# 생성된 IP-XACT 파일을 원격 스키마에 대해 유효성 검사
sv_to_ipxact -i design.sv --validate

# 생성된 IP-XACT 파일을 로컬 스키마에 대해 유효성 검사 (없으면 다운로드)
sv_to_ipxact -i design.sv --validate-local

# 생성된 IP-XACT 파일 유효성 검사 안 함
sv_to_ipxact -i design.sv --no-validate

# 상세 출력
sv_to_ipxact -i design.sv -v
```

### 옵션

- `-i, --input`: 입력 SystemVerilog 파일 (필수)
- `-o, --output`: 출력 IP-XACT 파일 (기본값: `<input>.ipxact`)
- `--rebuild`: 라이브러리 캐시 강제 재생성
- `--libs`: 라이브러리 디렉토리 경로 (기본값: `libs`)
- `--cache`: 캐시 파일 경로 (기본값: `.libs_cache.json`)
- `--threshold`: 매칭 임계값 0.0-1.0 (기본값: 0.6)
- `--ipxact-2009`: IP-XACT 2009 표준 사용 (기본값: 2014)
- `--ipxact-2022`: IP-XACT 2022 표준 사용 (기본값: 2014)
- `--validate`: 생성된 IP-XACT 파일을 원격 스키마에 대해 유효성 검사
- `--validate-local`: 생성된 IP-XACT 파일을 로컬 스키마에 대해 유효성 검사 (없으면 다운로드)
- `--no-validate`: 생성된 IP-XACT 파일 유효성 검사 안 함
- `-v, --verbose`: 상세 출력

## 예제

### AXI4 Master 인터페이스

```systemverilog
module axi_master_example (
    input  wire clk,
    input  wire rst_n,

    // AXI4 Master
    output wire [31:0] M_AXI_AWADDR,
    output wire [7:0]  M_AXI_AWLEN,
    // ... 기타 AXI4 신호들
);
```

변환:
```bash
sv_to_ipxact -i examples/axi_master_example.sv
```

결과: `M_AXI` 프리픽스를 가진 신호들이 AXI4 master busInterface로 매핑됨

### 다중 인터페이스

```systemverilog
module dual_interface (
    // AXI4-Lite Slave
    input  wire [31:0] S_AXI_AWADDR,
    // ...

    // APB Master
    output wire [31:0] M_APB_PADDR,
    // ...
);
```

두 개의 버스 인터페이스가 자동으로 인식되어 각각 매핑됩니다.

## 지원 프로토콜

### AMBA2
- AHB

### AMBA3
- AXI, AXI_RO, AXI_WO
- APB
- AHB-Lite, AHBLiteInitiator, AHBLiteTarget
- ATB, LPI

### AMBA4
- AXI4, AXI4-Lite, AXI4Stream
- AXI4_RO, AXI4_WO
- APB4
- ACE, ACE-Lite, ACE-Lite_RO, ACE-Lite_WO
- ACP, ATB
- P-Channel, Q-Channel

### AMBA5
- AXI5, AXI5-Lite, AXI5-Stream
- APB5
- AHB5Initiator, AHB5Target
- ACE5, ACE5-Lite, ACE5-LiteACP, ACE5-LiteDVM
- CHI (A~H 버전, RND/RNF/RNI/SNF/SNI)
- ATB, CXS, GFB, LTI

### JEDEC
- DFI4

## 프로젝트 구조

```
sv_to_ipxact/
├── src/sv_to_ipxact/
│   ├── library_parser.py     # AMBA 프로토콜 XML 파서
│   ├── sv_parser.py           # SystemVerilog 파서
│   ├── protocol_matcher.py   # 프로토콜 매칭 알고리즘
│   ├── ipxact_generator.py   # IP-XACT XML 생성기
│   └── main.py                # CLI 엔트리포인트
├── libs/                      # AMBA 프로토콜 정의 (ARM 제공)
├── examples/                  # 예제 파일
├── CLAUDE.md                  # 개발자 가이드
└── README.md
```

## 동작 방식

1.  **라이브러리 로딩**: `libs/` 디렉토리의 IP-XACT 프로토콜 정의 파싱 (첫 실행 시 캐싱)
2.  **SystemVerilog 파싱**: 모듈 포트 추출
3.  **신호 그룹화**: 공통 prefix를 가진 신호들을 그룹화
4.  **프로토콜 매칭**: 각 그룹을 AMBA 프로토콜과 비교하여 최적 매치 선택
5.  **IP-XACT 생성**: busInterface와 portMap을 포함한 XML 생성
6.  **로컬 스키마 다운로드 (--validate-local 옵션 사용 시)**: `schemas/IPXACT-<version>/`에 로컬 스키마 파일이 없으면 Accellera 공식 웹사이트에서 자동으로 다운로드됩니다.

## 라이브러리 업데이트

`libs/` 디렉토리에 새로운 프로토콜 정의를 추가하면 자동으로 인식됩니다:

```bash
# 새 프로토콜 추가 후
sv_to_ipxact -i design.sv --rebuild
```

라이브러리 캐시는 자동으로 무효화되며, `--rebuild` 옵션으로 수동 재생성 가능합니다.

## 문서

### 온라인 문서 생성

프로젝트의 전체 API 문서와 상세 가이드를 생성할 수 있습니다:

```bash
# 문서 생성 의존성 설치
pip install -r docs_requirements.txt

# 문서 생성
./generate_docs.sh

# 또는
cd docs && make html
```

생성된 문서는 `docs/_build/html/index.html` 에서 확인할 수 있습니다.

### 문서 내용

- **설치 가이드**: 설치 방법 및 의존성
- **사용 가이드**: 명령행 옵션 및 워크플로우
- **API 문서**: 전체 Python API 레퍼런스
- **예제 모음**: 다양한 사용 예제와 설명
- **개발자 가이드**: [CLAUDE.md](CLAUDE.md) - 내부 아키텍처 및 개발 지침

### 소스코드 문서화

모든 Python 모듈은 상세한 docstring을 포함하고 있습니다:

- Google 스타일 docstring
- 타입 힌트 포함
- 사용 예제 포함
- Sphinx를 통한 자동 문서 생성

예시:
```python
from sv_to_ipxact.sv_parser import SystemVerilogParser

# 도움말 보기
help(SystemVerilogParser)
help(SystemVerilogParser.parse_file)
```

## 테스트

### 유닛 테스트 실행

```bash
# 유닛 테스트만 실행
make test-unit

# 통합 테스트 실행
make test-integration

# 모든 테스트 실행
make test-all

# 커버리지 포함 테스트
make test-cov
```

### 테스트 커버리지

현재 테스트 커버리지:
- **library_parser.py**: 93%
- **protocol_matcher.py**: 84%
- **sv_parser.py**: 87%
- **ipxact_generator.py**: 92% (통합 테스트)

커버리지 리포트는 `htmlcov/index.html` 에서 확인할 수 있습니다.

## Makefile 명령어

프로젝트는 다양한 작업을 쉽게 수행할 수 있는 Makefile을 제공합니다:

```bash
# 도움말 보기
make help

# 개발 환경 설정
make install-dev

# 테스트
make test           # 유닛 테스트
make test-all       # 모든 테스트
make test-cov       # 커버리지 포함

# 코드 품질
make lint           # 린터 실행
make format         # 코드 포맷팅
make check          # 린트 + 테스트

# 문서
make docs           # 문서 생성
make docs-serve     # 문서 생성 후 브라우저에서 열기

# 예제
make run-examples   # 모든 예제 실행
make rebuild-cache  # 라이브러리 캐시 재생성

# 정리
clean:          # 빌드 산출물, 캐시 파일 및 다운로드된 스키마 제거
make clean-all      # 모든 생성 파일 제거

# CI
make ci             # 전체 CI 파이프라인
make ci-quick       # 빠른 CI 체크
```

### 자주 사용하는 명령어

```bash
# 개발 시작
make install-dev

# 코드 변경 후 테스트
make test

# 커밋 전 체크
make check

# 예제 실행
make run-examples
```

## 개발자 가이드

상세한 개발 가이드는 [CLAUDE.md](CLAUDE.md)를 참조하세요.
