sv_to_ipxact 문서
==================

SystemVerilog 모듈을 IP-XACT 컴포넌트 정의로 변환하는 도구입니다.

.. toctree::
   :maxdepth: 2
   :caption: 목차:

   installation
   usage
   api
   examples

소개
----

sv_to_ipxact는 SystemVerilog 모듈 파일을 읽어 AMBA 버스 프로토콜을 자동으로 인식하고
IP-XACT (IEEE 1685-2009) 형식의 컴포넌트 정의를 생성합니다.

주요 기능
---------

* SystemVerilog 모듈 파서 (ANSI/non-ANSI 스타일 지원)
* 89개의 AMBA 프로토콜 자동 인식 (AMBA2-5)
* 신호 prefix 기반 버스 인터페이스 매칭
* 동적 라이브러리 로딩 및 캐싱
* IP-XACT XML 생성

빠른 시작
----------

설치::

    python3 -m venv venv
    source venv/bin/activate
    pip install -e .

사용::

    sv_to_ipxact -i design.sv
    sv_to_ipxact -i design.sv -o output.xml --rebuild

인덱스
------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
