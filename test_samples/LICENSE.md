# Test Samples License and Attribution

이 디렉토리의 파일들은 IP-XACT 변환 도구 테스트를 위해 수집된 SystemVerilog 예제 파일들입니다.

## 외부에서 가져온 파일 (Third-Party Files)

### PULP Platform

다음 파일들은 PULP Platform 프로젝트에서 가져온 것입니다:

#### axi_cut.sv
- **출처**: [PULP Platform AXI Repository](https://github.com/pulp-platform/axi)
- **원본 경로**: `src/axi_cut.sv`
- **라이선스**: Solderpad Hardware License, Version 0.51 (SHL-0.51)
- **저작권**: Copyright (c) 2014-2018 ETH Zurich, University of Bologna
- **작성자**:
  - Wolfgang Roenninger <wroennin@iis.ee.ethz.ch>
  - Fabian Schuiki <fschuiki@iis.ee.ethz.ch>
  - Andreas Kurth <akurth@iis.ee.ethz.ch>
- **라이선스 링크**: http://solderpad.org/licenses/SHL-0.51

#### axi_demux.sv
- **출처**: [PULP Platform AXI Repository](https://github.com/pulp-platform/axi)
- **원본 경로**: `src/axi_demux.sv`
- **라이선스**: Solderpad Hardware License, Version 0.51 (SHL-0.51)
- **저작권**: Copyright (c) 2019 ETH Zurich and University of Bologna
- **작성자**:
  - Michael Rogenmoser <michaero@iis.ee.ethz.ch>
  - Wolfgang Roenninger <wroennin@iis.ee.ethz.ch>
  - Thomas Benz <tbenz@iis.ee.ethz.ch>
  - Andreas Kurth <akurth@iis.ee.ethz.ch>
- **라이선스 링크**: http://solderpad.org/licenses/SHL-0.51

#### axi_interconnect.sv
- **출처**: [PULP Platform AXI Repository](https://github.com/pulp-platform/axi)
- **원본 경로**: `src/axi_interconnect.sv`
- **라이선스**: Solderpad Hardware License, Version 0.51 (SHL-0.51)
- **참고**: 이 파일은 다운로드 시도했으나 실제 내용이 포함되지 않았습니다.

### Alex Forencich's Verilog AXI Components

다음 파일들은 Alex Forencich의 Verilog AXI 컴포넌트 저장소에서 가져오려고 시도했으나 실제로는 다운로드되지 않았습니다:

#### axi_master.sv
- **출처 시도**: [alexforencich/verilog-axi](https://github.com/alexforencich/verilog-axi)
- **원본 경로 시도**: `rtl/axi_master.v`
- **상태**: 다운로드 실패 (파일이 비어있음)

#### axi_slave.sv
- **출처 시도**: [alexforencich/verilog-axi](https://github.com/alexforencich/verilog-axi)
- **원본 경로 시도**: `rtl/axi_slave.v`
- **상태**: 다운로드 실패 (파일이 비어있음)

#### axi4_lite_master.sv
- **출처 시도**: [alexforencich/verilog-axi](https://github.com/alexforencich/verilog-axi)
- **원본 경로 시도**: `rtl/axi_lite_master.v`
- **상태**: 다운로드 실패 (파일이 비어있음)

## 직접 작성한 테스트 파일 (Original Test Files)

다음 파일들은 IP-XACT 변환 도구 테스트를 위해 직접 작성한 파일들입니다:

### axi4_master_example.sv
- **작성 목적**: AXI4 마스터 인터페이스 테스트
- **설명**: 표준 포트 기반 AXI4 마스터 인터페이스 예제
- **라이선스**: 이 프로젝트의 라이선스에 따름

### axi4_lite_slave_example.sv
- **작성 목적**: AXI4-Lite 슬레이브 인터페이스 테스트
- **설명**: 표준 포트 기반 AXI4-Lite 슬레이브 인터페이스 예제
- **라이선스**: 이 프로젝트의 라이선스에 따름

### dual_axi_interfaces.sv
- **작성 목적**: 다중 AXI 인터페이스 테스트
- **설명**: 마스터와 슬레이브 인터페이스를 모두 포함한 예제
- **라이선스**: 이 프로젝트의 라이선스에 따름

### test_postfix_only.sv
- **작성 목적**: Postfix 패턴 테스트
- **설명**: `_o`, `_i` 같은 postfix가 있는 AXI 신호 테스트
- **라이선스**: 이 프로젝트의 라이선스에 따름

### test_prefix_postfix.sv
- **작성 목적**: 다양한 prefix/postfix 패턴 테스트
- **설명**: 여러 가지 prefix/postfix 조합 테스트
- **라이선스**: 이 프로젝트의 라이선스에 따름

### test_simple_prefix.sv
- **작성 목적**: 표준 prefix 패턴 테스트
- **설명**: 표준 `M_AXI_*` 패턴 테스트
- **라이선스**: 이 프로젝트의 라이선스에 따름

### test_various_patterns.sv
- **작성 목적**: 다양한 네이밍 패턴 테스트
- **설명**: prefix, postfix, 인스턴스 번호 등 다양한 패턴 테스트
- **라이선스**: 이 프로젝트의 라이선스에 따름

## 라이선스 정보

### Solderpad Hardware License, Version 0.51 (SHL-0.51)

PULP Platform에서 가져온 파일들은 Solderpad Hardware License, Version 0.51을 따릅니다.

**주요 내용**:
- 하드웨어 설계를 위한 오픈소스 라이선스
- Apache 2.0과 유사하지만 하드웨어에 특화됨
- 상업적 사용 가능
- 수정 및 배포 가능
- 저작권 표시 및 라이선스 고지 필요

**전체 라이선스 텍스트**: http://solderpad.org/licenses/SHL-0.51

### 이 프로젝트의 라이선스

직접 작성한 테스트 파일들은 이 프로젝트의 라이선스에 따릅니다.
프로젝트 루트의 `LICENSE.txt` 파일을 참조하세요.

## 사용 목적

이 디렉토리의 모든 파일은 **IP-XACT 변환 도구의 테스트 목적으로만 사용**됩니다.
프로덕션 코드에 직접 사용하지 마세요.

## 참고 자료

- [PULP Platform AXI Repository](https://github.com/pulp-platform/axi)
- [Solderpad Hardware License](http://solderpad.org/licenses/SHL-0.51)
- [Alex Forencich's Verilog AXI Components](https://github.com/alexforencich/verilog-axi)

## 업데이트 이력

- 2024-11-15: 초기 라이선스 문서 작성
  - PULP Platform 파일들의 출처 및 라이선스 정보 추가
  - 직접 작성한 테스트 파일 목록 정리
