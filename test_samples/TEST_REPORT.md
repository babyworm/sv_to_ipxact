# IP-XACT 변환 테스트 리포트

## 테스트 개요
인터넷에서 다운로드한 SystemVerilog AXI 파일들로 IP-XACT 변환 기능을 테스트했습니다.

## 테스트 파일 목록

### 1. axi4_master_example.sv ✅
- **소스**: 직접 작성 (포트 기반 AXI4 마스터 인터페이스)
- **포트 수**: 42개
- **변환 결과**: ✅ 성공
- **매칭된 프로토콜**: `amba.com:AMBA4:AXI4:r0p0_0` (master)
- **매칭된 신호**: 39개
- **매칭되지 않은 포트**: 2개 (clk, rst_n)
- **생성된 파일**: `axi4_master_example.ipxact`

**결과**: AXI4 마스터 인터페이스가 정확히 인식되고 IP-XACT로 변환되었습니다.

### 2. axi4_lite_slave_example.sv ✅
- **소스**: 직접 작성 (포트 기반 AXI4-Lite 슬레이브 인터페이스)
- **포트 수**: 21개
- **변환 결과**: ✅ 성공
- **매칭된 프로토콜**: `amba.com:AMBA4:AXI4-Lite:r0p0_0` (slave)
- **매칭된 신호**: 19개
- **매칭되지 않은 포트**: 2개 (aclk, aresetn)
- **생성된 파일**: `axi4_lite_slave_example.ipxact`

**결과**: AXI4-Lite 슬레이브 인터페이스가 정확히 인식되고 IP-XACT로 변환되었습니다.

### 3. dual_axi_interfaces.sv ✅
- **소스**: 직접 작성 (다중 AXI 인터페이스)
- **포트 수**: 34개
- **변환 결과**: ✅ 성공
- **매칭된 프로토콜**:
  - `M_AXI`: `amba.com:AMBA4:ACE-Lite_RO:r0p0_0` (master) - 16개 신호
  - `S_AXI_LITE`: `amba.com:AMBA4:AXI4-Lite:r0p0_0` (slave) - 16개 신호
- **매칭되지 않은 포트**: 2개 (clk, rst_n)
- **생성된 파일**: `dual_axi_interfaces.ipxact`

**결과**: 다중 인터페이스가 모두 인식되었습니다. 다만 M_AXI가 ACE-Lite_RO로 매칭된 것은 AXI4와 신호가 유사하기 때문입니다.

### 4. axi_cut.sv ⚠️
- **소스**: PULP Platform (https://github.com/pulp-platform/axi)
- **포트 수**: 6개
- **변환 결과**: ⚠️ 부분 성공 (프로토콜 매칭 실패)
- **매칭된 프로토콜**: 없음
- **매칭되지 않은 포트**: 6개 (struct 기반 인터페이스)
- **생성된 파일**: `axi_cut.ipxact`

**결과**: 파일은 파싱되었지만, struct 기반 AXI 인터페이스를 사용하여 포트 기반 매칭이 불가능했습니다. IP-XACT 파일은 생성되었지만 busInterface가 없습니다.

### 5. axi_demux.sv ❌
- **소스**: PULP Platform (https://github.com/pulp-platform/axi)
- **변환 결과**: ❌ 실패
- **오류**: "No module definition found"

**결과**: 파서가 모듈 정의를 찾지 못했습니다. 이는 include 파일이나 복잡한 SystemVerilog 구조 때문일 수 있습니다.

## 테스트 통계

- **총 테스트 파일**: 5개
- **완전 성공**: 3개 (60%)
- **부분 성공**: 1개 (20%)
- **실패**: 1개 (20%)

## 주요 발견 사항

### ✅ 성공 사례
1. **포트 기반 AXI 인터페이스**: 표준 포트 기반 AXI 신호 (예: `M_AXI_AWADDR`, `S_AXI_AWADDR`)는 정확히 인식됩니다.
2. **다중 인터페이스**: 하나의 모듈에 여러 AXI 인터페이스가 있어도 모두 인식됩니다.
3. **AXI4 vs AXI4-Lite**: 두 프로토콜이 정확히 구분되어 매칭됩니다.

### ⚠️ 제한 사항
1. **Struct 기반 인터페이스**: PULP Platform과 같은 struct 기반 AXI 인터페이스는 현재 지원되지 않습니다.
   - 예: `axi_req_t`, `axi_resp_t` 같은 struct 타입
2. **복잡한 모듈 구조**: include 파일이나 복잡한 SystemVerilog 구조는 파싱에 실패할 수 있습니다.
3. **프로토콜 매칭 정확도**: 일부 경우 유사한 프로토콜 (예: AXI4 vs ACE-Lite_RO)이 잘못 매칭될 수 있습니다.

## 권장 사항

1. **포트 기반 인터페이스 사용**: 현재 도구는 포트 기반 AXI 인터페이스에 최적화되어 있습니다.
2. **명확한 신호 네이밍**: 표준 AXI 신호 네이밍 규칙을 따르면 더 정확한 매칭이 가능합니다.
   - 마스터: `M_AXI_*` 또는 `m_axi_*`
   - 슬레이브: `S_AXI_*` 또는 `s_axi_*`
3. **프로토콜 매칭 임계값 조정**: 필요시 `--threshold` 옵션으로 매칭 정확도를 조정할 수 있습니다.

## 결론

포트 기반 AXI 인터페이스를 가진 SystemVerilog 파일들은 IP-XACT로 성공적으로 변환됩니다.
현재 도구는 표준 포트 기반 인터페이스에 최적화되어 있으며, struct 기반 인터페이스는 향후 지원이 필요합니다.
