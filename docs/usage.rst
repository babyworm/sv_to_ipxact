사용 가이드
============

기본 사용법
-----------

가장 간단한 사용 방법::

    sv_to_ipxact -i design.sv

이렇게 하면 ``design.ipxact`` 파일이 생성됩니다.

명령행 옵션
-----------

필수 옵션
^^^^^^^^^

``-i, --input FILE``
    입력 SystemVerilog 파일 경로

선택 옵션
^^^^^^^^^

``-o, --output FILE``
    출력 IP-XACT 파일 경로 (기본값: ``<입력파일명>.ipxact``)

``--rebuild``
    라이브러리 캐시를 강제로 재생성합니다. ``libs/`` 디렉토리가
    업데이트된 경우 사용하세요.

``--libs DIR``
    라이브러리 디렉토리 경로 (기본값: ``libs``)

``--cache FILE``
    캐시 파일 경로 (기본값: ``.libs_cache.json``)

``--threshold FLOAT``
    프로토콜 매칭 임계값 0.0-1.0 (기본값: 0.6).
    값이 높을수록 더 정확한 매칭을 요구합니다.

``-v, --verbose``
    상세한 출력을 표시합니다.

사용 예제
---------

예제 1: 기본 변환
^^^^^^^^^^^^^^^^^

AXI master 인터페이스를 가진 모듈::

    sv_to_ipxact -i examples/axi_master_example.sv

출력::

    ======================================================================
    SystemVerilog to IP-XACT Converter
    ======================================================================
    Input:  examples/axi_master_example.sv
    Output: examples/axi_master_example.ipxact

    [1] Loading protocol library...
    Loaded 89 protocols from cache

    [2] Parsing SystemVerilog file...
    Module: axi_master_example
    Ports: 37

    [3] Matching protocols...
    Port groups: 3
      Matched M_AXI to amba.com:AMBA4:AXI4:r0p0_0 (master)
        - Matched 33 signals
    Matched bus interfaces: 1
      - M_AXI: AXI4 (master)

    [4] Generating IP-XACT...
    IP-XACT file written to: examples/axi_master_example.ipxact

예제 2: 출력 파일 지정
^^^^^^^^^^^^^^^^^^^^^^^

::

    sv_to_ipxact -i my_design.sv -o ipxact/output.xml

예제 3: 상세 출력
^^^^^^^^^^^^^^^^^

::

    sv_to_ipxact -i design.sv -v

모든 파싱된 포트와 매칭 상세 정보를 표시합니다.

예제 4: 라이브러리 캐시 재생성
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

새로운 AMBA 프로토콜 정의를 ``libs/`` 에 추가한 후::

    sv_to_ipxact -i design.sv --rebuild

이렇게 하면 라이브러리를 다시 스캔하고 캐시를 업데이트합니다.

예제 5: 다중 인터페이스
^^^^^^^^^^^^^^^^^^^^^^^

여러 버스 인터페이스를 가진 모듈::

    sv_to_ipxact -i examples/dual_interface.sv

출력::

    [3] Matching protocols...
      Matched S_AXI to amba.com:AMBA4:AXI4-Lite:r0p0_0 (slave)
        - Matched 19 signals
      Matched M_APB to amba.com:AMBA4:APB4:r0p0_0 (master)
        - Matched 7 signals
    Matched bus interfaces: 2
      - S_AXI: AXI4-Lite (slave)
      - M_APB: APB4 (master)

워크플로우
-----------

1. **SystemVerilog 파일 준비**

   모듈 포트가 명확하게 정의되어 있고, 버스 신호들이
   일관된 prefix를 사용하는지 확인하세요.

2. **변환 실행**

   ::

       sv_to_ipxact -i design.sv

3. **결과 확인**

   생성된 ``.ipxact`` 파일을 XML 에디터나 IP-XACT 도구로
   열어 확인하세요.

4. **필요시 조정**

   매칭이 정확하지 않다면 ``--threshold`` 값을 조정하거나
   SystemVerilog 파일의 신호 이름을 표준 명명 규칙에 맞게
   수정하세요.

트러블슈팅
----------

프로토콜 매칭 실패
^^^^^^^^^^^^^^^^^^

증상: "No protocol match for prefix" 메시지

해결방법:

1. 신호 이름이 일관된 prefix를 사용하는지 확인
2. ``--threshold`` 값을 낮춰보세요 (예: 0.4)
3. ``-v`` 옵션으로 상세 정보 확인

파싱 에러
^^^^^^^^^

증상: "No module definition found"

해결방법:

1. SystemVerilog 문법이 올바른지 확인
2. 파일에 정확히 하나의 모듈이 있는지 확인
3. 주석이 올바르게 닫혔는지 확인

캐시 문제
^^^^^^^^^

증상: 새로 추가한 프로토콜이 인식되지 않음

해결방법::

    sv_to_ipxact -i design.sv --rebuild
