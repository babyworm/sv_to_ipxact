예제 모음
=========

이 섹션에서는 sv_to_ipxact의 다양한 사용 예제를 소개합니다.

예제 1: AXI4 Master 인터페이스
-------------------------------

SystemVerilog 소스
^^^^^^^^^^^^^^^^^^

.. code-block:: systemverilog

    module axi_master_example #(
        parameter ADDR_WIDTH = 32,
        parameter DATA_WIDTH = 64
    ) (
        input  wire clk,
        input  wire rst_n,

        // AXI4 Master Interface
        output wire [ADDR_WIDTH-1:0]  M_AXI_AWADDR,
        output wire [7:0]              M_AXI_AWLEN,
        output wire [2:0]              M_AXI_AWSIZE,
        output wire [1:0]              M_AXI_AWBURST,
        output wire                    M_AXI_AWVALID,
        input  wire                    M_AXI_AWREADY,
        // ... 기타 AXI 신호들
    );
    endmodule

변환 명령
^^^^^^^^^

::

    sv_to_ipxact -i examples/axi_master_example.sv -v

출력 결과
^^^^^^^^^

33개의 M_AXI 신호가 AXI4 master 버스 인터페이스로 정확히 매핑됩니다.

생성된 IP-XACT (일부):

.. code-block:: xml

    <spirit:component>
      <spirit:vendor>user</spirit:vendor>
      <spirit:name>axi_master_example</spirit:name>
      <spirit:busInterfaces>
        <spirit:busInterface>
          <spirit:name>M_AXI</spirit:name>
          <spirit:busType spirit:vendor="amba.com"
                         spirit:library="AMBA4"
                         spirit:name="AXI4"
                         spirit:version="r0p0_0"/>
          <spirit:master/>
          <spirit:portMaps>
            <spirit:portMap>
              <spirit:logicalPort>
                <spirit:name>AWADDR</spirit:name>
              </spirit:logicalPort>
              <spirit:physicalPort>
                <spirit:name>M_AXI_AWADDR</spirit:name>
              </spirit:physicalPort>
            </spirit:portMap>
            <!-- ... 기타 portMap 항목들 -->
          </spirit:portMaps>
        </spirit:busInterface>
      </spirit:busInterfaces>
    </spirit:component>

예제 2: 다중 버스 인터페이스
-----------------------------

SystemVerilog 소스
^^^^^^^^^^^^^^^^^^

.. code-block:: systemverilog

    module dual_interface (
        input wire clk,
        input wire rst_n,

        // AXI4-Lite Slave Interface
        input  wire [31:0]  S_AXI_AWADDR,
        input  wire [2:0]   S_AXI_AWPROT,
        input  wire         S_AXI_AWVALID,
        output wire         S_AXI_AWREADY,
        // ... 기타 AXI-Lite 신호들

        // APB Master Interface
        output wire [31:0]  M_APB_PADDR,
        output wire         M_APB_PSEL,
        output wire         M_APB_PENABLE,
        // ... 기타 APB 신호들
    );
    endmodule

변환 명령
^^^^^^^^^

::

    sv_to_ipxact -i examples/dual_interface.sv

결과 분석
^^^^^^^^^

두 개의 서로 다른 버스 인터페이스가 인식됩니다:

1. **S_AXI**: AXI4-Lite slave (19개 신호)
2. **M_APB**: APB4 master (7개 신호)

각 인터페이스는 독립적인 busInterface 요소로 생성됩니다.

예제 3: 프로그래밍 방식 사용
----------------------------

Python 코드에서 직접 사용하기:

.. code-block:: python

    from sv_to_ipxact.sv_parser import SystemVerilogParser
    from sv_to_ipxact.library_parser import LibraryParser
    from sv_to_ipxact.protocol_matcher import ProtocolMatcher
    from sv_to_ipxact.ipxact_generator import IPXACTGenerator

    # 1. 라이브러리 로드
    lib_parser = LibraryParser("libs")
    if not lib_parser.load_cache(".libs_cache.json"):
        lib_parser.parse_all_protocols()
        lib_parser.save_cache()

    # 2. SystemVerilog 파싱
    sv_parser = SystemVerilogParser()
    module = sv_parser.parse_file("design.sv")

    # 3. 포트 그룹화 및 프로토콜 매칭
    port_groups = sv_parser.group_ports_by_prefix()
    matcher = ProtocolMatcher(lib_parser.protocols)
    bus_interfaces, unmatched = matcher.match_all_groups(port_groups)

    # 4. IP-XACT 생성
    generator = IPXACTGenerator(module, bus_interfaces, unmatched)
    generator.write_to_file("output.ipxact")

    # 또는 문자열로 가져오기
    xml_str = generator.to_string()
    print(xml_str)

예제 4: 커스텀 프로토콜 추가
----------------------------

``libs/`` 디렉토리에 새로운 프로토콜 정의를 추가할 수 있습니다:

1. 프로토콜 정의 파일 구조::

    libs/
    └── custom_vendor/
        └── CUSTOM_BUS/
            └── v1_0/
                ├── CUSTOM_BUS.xml        # Bus definition
                └── CUSTOM_BUS_rtl.xml    # Abstraction definition

2. Bus definition (CUSTOM_BUS.xml):

.. code-block:: xml

    <spirit:busDefinition>
      <spirit:vendor>custom_vendor</spirit:vendor>
      <spirit:library>CUSTOM_BUS</spirit:library>
      <spirit:name>MyBus</spirit:name>
      <spirit:version>v1_0</spirit:version>
      <spirit:directConnection>true</spirit:directConnection>
    </spirit:busDefinition>

3. Abstraction definition (CUSTOM_BUS_rtl.xml):

.. code-block:: xml

    <spirit:abstractionDefinition>
      <spirit:vendor>custom_vendor</spirit:vendor>
      <spirit:library>CUSTOM_BUS</spirit:library>
      <spirit:name>MyBus_rtl</spirit:name>
      <spirit:version>v1_0</spirit:version>
      <spirit:ports>
        <spirit:port>
          <spirit:logicalName>DATA</spirit:logicalName>
          <spirit:wire>
            <spirit:onMaster>
              <spirit:direction>out</spirit:direction>
              <spirit:width>32</spirit:width>
            </spirit:onMaster>
          </spirit:wire>
        </spirit:port>
        <!-- ... 기타 포트 정의 -->
      </spirit:ports>
    </spirit:abstractionDefinition>

4. 캐시 재생성 및 사용::

    sv_to_ipxact -i design.sv --rebuild

예제 5: 매칭 임계값 조정
-------------------------

신호 이름이 표준과 약간 다른 경우::

    # 엄격한 매칭 (기본값)
    sv_to_ipxact -i design.sv --threshold 0.8

    # 느슨한 매칭
    sv_to_ipxact -i design.sv --threshold 0.4

임계값이 낮을수록 더 많은 프로토콜 후보가 매칭되지만,
잘못된 매칭이 발생할 가능성도 높아집니다.

권장 임계값:
- 0.8-1.0: 표준 명명 규칙을 엄격히 따르는 경우
- 0.6-0.8: 일반적인 경우 (기본값: 0.6)
- 0.4-0.6: 비표준 명명 규칙을 사용하는 경우

더 많은 예제
------------

프로젝트의 ``examples/`` 디렉토리에서 더 많은 예제를 찾을 수 있습니다:

* ``axi_master_example.sv`` - AXI4 master 인터페이스
* ``dual_interface.sv`` - 다중 버스 인터페이스
