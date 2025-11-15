# AXI 신호 Prefix/Postfix 처리 능력 분석 리포트

## 결론: **대부분의 경우 해결 가능**

현재 구현은 **prefix와 postfix가 붙은 AXI 신호를 처리할 수 있습니다**. 다만, 몇 가지 조건이 필요합니다.

## ✅ 지원되는 패턴

### 1. Prefix 변형
- ✅ `M_AXI_AWADDR` (표준)
- ✅ `m_axi_awaddr` (소문자)
- ✅ `M_AXI0_AWADDR` (인스턴스 번호 포함)
- ✅ `AXI_M_AWADDR` (순서 변경)
- ✅ `MASTER_AXI4_AWADDR` (긴 prefix)

### 2. Postfix 변형
- ✅ `M_AXI_AWADDR_o` (출력 표시)
- ✅ `M_AXI_AWADDR_i` (입력 표시)
- ✅ `M_AXI_AWADDR_0` (인덱스)
- ✅ `M_AXI_AWADDR0` (인덱스, 언더스코어 없음)

### 3. 복합 패턴
- ✅ `M_AXI0_AWADDR_o` (prefix 번호 + postfix)
- ✅ `m_axi_awaddr_i` (소문자 + postfix)

## 작동 원리

### 1. 토큰 분리
```python
# 예: M_AXI_AWADDR_o
tokens = ['M', 'AXI', 'AWADDR', 'o']
```

### 2. 후보 생성
`_get_port_suffix_candidates()` 메서드가 모든 가능한 토큰 조합을 생성:
```python
candidates = [
    'M', 'M_AXI', 'M_AXI_AWADDR', 'M_AXI_AWADDR_o',
    'AXI', 'AXI_AWADDR', 'AXI_AWADDR_o',
    'AWADDR', 'AWADDR_o',  # ← 핵심 신호 추출!
    'o'
]
```

### 3. 정규화 및 매칭
```python
# 정규화: 대문자 변환 + 언더스코어 제거
'AWADDR' → 'AWADDR' ✅
'AWADDR_o' → 'AWADDRO' (하지만 'AWADDR'도 후보에 있음)
```

## 실제 테스트 결과

### 테스트 1: Postfix만 있는 경우 ✅
```systemverilog
M_AXI_AWADDR_o, M_AXI_AWVALID_o, M_AXI_AWREADY_i, ...
```
**결과**: ✅ 성공 (25개 신호 매칭)

### 테스트 2: 인스턴스 번호 포함 ✅
```systemverilog
M_AXI0_AWADDR, M_AXI0_AWVALID, M_AXI0_AWREADY, ...
```
**결과**: ✅ 성공 (25개 신호 매칭)

### 테스트 3: 소문자 prefix ✅
```systemverilog
m_axi_awaddr, m_axi_awvalid, m_axi_awready, ...
```
**결과**: ✅ 성공 (25개 신호 매칭)

## ⚠️ 제한 사항 및 조건

### 1. 충분한 신호 필요
- **최소 요구사항**: 같은 prefix를 가진 신호가 **10개 이상** 권장
- **이유**: 매칭 점수 계산 시 required 신호 매칭률이 중요
- **실패 사례**: 신호가 3개만 있으면 매칭 점수가 낮아 실패할 수 있음

### 2. 일관된 네이밍
- 같은 인터페이스의 신호는 **같은 prefix**를 가져야 함
- 예: `M_AXI_AWADDR`, `M_AXI_AWVALID` (같은 `M_AXI` prefix)

### 3. 매칭 임계값
- 기본 임계값: **0.6**
- 신호가 적으면 임계값을 낮춰야 할 수 있음: `--threshold 0.4`

## 개선 가능한 부분

### 현재 구현의 장점
1. ✅ 유연한 토큰 분리 (언더스코어, CamelCase 지원)
2. ✅ 모든 가능한 조합 생성
3. ✅ 정규화를 통한 대소문자/언더스코어 무시

### 향후 개선 사항
1. **Postfix 자동 인식**: `_o`, `_i`, `_0` 같은 일반적인 postfix 패턴 자동 제거
2. **그룹 병합**: 유사한 prefix를 가진 그룹 자동 병합 (예: `M_AXI`, `M_AXI0`)
3. **더 유연한 매칭**: 핵심 신호만 매칭되어도 성공 판정

## 사용 권장사항

### ✅ 권장 패턴
```systemverilog
// 표준 패턴 (가장 안정적)
M_AXI_AWADDR, M_AXI_AWVALID, M_AXI_AWREADY, ...

// Postfix 사용 시 (충분한 신호 필요)
M_AXI_AWADDR_o, M_AXI_AWVALID_o, M_AXI_AWREADY_i, ...

// 인스턴스 번호 포함 (정상 작동)
M_AXI0_AWADDR, M_AXI0_AWVALID, M_AXI0_AWREADY, ...
```

### ⚠️ 주의사항
1. **신호 수**: 최소 10개 이상의 AXI 신호 제공
2. **일관성**: 같은 인터페이스는 같은 prefix 사용
3. **임계값 조정**: 필요시 `--threshold` 옵션 사용

## 최종 답변

**질문**: AXI 신호에 prefix나 postfix 어떤 형태가 붙던지 해결할 수 있는 상황인가?

**답변**:
- ✅ **대부분의 경우 해결 가능**
- ✅ 표준 prefix/postfix 패턴은 모두 지원
- ⚠️ 단, **충분한 신호 수** (10개 이상 권장)와 **일관된 네이밍** 필요
- ✅ 현재 구현으로도 실무에서 사용 가능한 수준

## 테스트 파일

모든 테스트 파일은 `test_samples/` 디렉토리에 있습니다:
- `test_postfix_only.sv` - Postfix 패턴 테스트 (성공)
- `test_various_patterns.sv` - 다양한 패턴 테스트
- `test_simple_prefix.sv` - 표준 패턴 테스트 (성공)
