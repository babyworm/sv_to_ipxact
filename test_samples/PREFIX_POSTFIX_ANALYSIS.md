# AXI 신호 Prefix/Postfix 처리 분석

## 현재 구현 상태

### 지원되는 기능

현재 구현은 **prefix/postfix 처리를 어느 정도 지원**하고 있습니다:

1. **`_get_port_suffix_candidates()` 메서드**: 포트 이름에서 모든 가능한 토큰 조합을 생성
2. **`_normalize_name()` 메서드**: 대소문자와 언더스코어를 정규화하여 비교
3. **`_split_port_tokens()` 메서드**: 포트 이름을 토큰으로 분리 (언더스코어 또는 CamelCase 기준)

### 작동 원리

```python
# 예: M_AXI_AWADDR_o
tokens = ['M', 'AXI', 'AWADDR', 'o']
candidates = [
    'M', 'M_AXI', 'M_AXI_AWADDR', 'M_AXI_AWADDR_o',
    'AXI', 'AXI_AWADDR', 'AXI_AWADDR_o',
    'AWADDR', 'AWADDR_o',  # ← AWADDR 추출 가능!
    'o'
]
```

정규화 후:
- `AWADDR` → `AWADDR` ✅
- `AWADDR_o` → `AWADDRO` ❌ (하지만 `AWADDR`도 후보에 있음)

## 테스트 결과

### ✅ 성공 사례

1. **표준 패턴**: `M_AXI_AWADDR` → 정상 매칭
2. **소문자 prefix**: `m_axi_awaddr` → 정상 매칭
3. **인스턴스 번호**: `M_AXI0_AWADDR` → 정상 매칭 (숫자 제거 후 매칭)

### ⚠️ 제한 사항

1. **Postfix 처리**:
   - `M_AXI_AWADDR_o` → `AWADDR` 후보가 생성되지만, 그룹 내 신호가 충분하지 않으면 매칭 실패
   - 신호가 많을수록 매칭 성공률 증가

2. **매칭 임계값**:
   - 기본 임계값 0.6
   - 신호가 적으면 (3개 이하) 매칭 점수가 낮아 실패할 수 있음

3. **Prefix 그룹핑**:
   - 포트는 먼저 prefix로 그룹화됨
   - 같은 prefix를 가진 신호들이 같은 그룹에 있어야 함

## 실제 테스트

### 테스트 1: 표준 패턴 (성공)
```systemverilog
M_AXI_AWADDR, M_AXI_AWVALID, M_AXI_AWREADY, ...
```
→ ✅ 정상 매칭 (25개 신호 매칭)

### 테스트 2: Postfix 패턴 (부분 성공)
```systemverilog
M_AXI_AWADDR_o, M_AXI_AWVALID_o, M_AXI_AWREADY_i, ...
```
→ ⚠️ 신호가 충분하면 매칭 가능하지만, 그룹이 분리되면 실패

### 테스트 3: 인스턴스 번호 (성공)
```systemverilog
M_AXI0_AWADDR, M_AXI0_AWVALID, M_AXI0_AWREADY, ...
```
→ ✅ 정상 매칭 (숫자 제거 후 매칭)

## 결론

### 현재 상태: **부분 지원**

- ✅ **Prefix 변형**: 지원됨 (M_AXI, m_axi, M_AXI0 등)
- ✅ **Postfix 제거**: 기술적으로 가능하지만 그룹 내 신호가 충분해야 함
- ⚠️ **복잡한 패턴**: 신호가 적으면 매칭 실패 가능

### 권장 사항

1. **충분한 신호 제공**: 최소 10개 이상의 AXI 신호가 같은 prefix를 가져야 함
2. **일관된 네이밍**: 같은 인터페이스의 신호는 같은 prefix/postfix 패턴 사용
3. **임계값 조정**: 필요시 `--threshold` 옵션으로 매칭 민감도 조정

### 개선 가능한 부분

1. **Postfix 자동 제거**: `_o`, `_i`, `_0` 같은 일반적인 postfix 자동 인식
2. **그룹 병합**: 유사한 prefix를 가진 그룹 자동 병합
3. **더 유연한 매칭**: 신호가 적어도 핵심 신호만 매칭되면 성공
