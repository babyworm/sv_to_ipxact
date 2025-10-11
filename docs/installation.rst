설치 가이드
============

시스템 요구사항
----------------

* Python 3.8 이상
* pip (Python 패키지 관리자)

의존성
------

sv_to_ipxact는 다음 Python 패키지들을 필요로 합니다:

* lxml >= 4.9.0 - XML 파싱 및 생성
* pyverilog >= 1.3.0 - SystemVerilog 파싱 (향후 사용)

설치 방법
---------

가상환경 생성
^^^^^^^^^^^^^

프로젝트를 위한 Python 가상환경을 생성하는 것을 권장합니다::

    python3 -m venv venv
    source venv/bin/activate  # Linux/Mac
    # 또는
    venv\Scripts\activate     # Windows

개발 모드 설치
^^^^^^^^^^^^^^

소스 코드에서 개발 모드로 설치::

    pip install -e .

이렇게 하면 소스 코드를 수정할 때마다 재설치 없이 변경사항이 반영됩니다.

일반 설치
^^^^^^^^^

릴리스 버전을 설치하려면::

    pip install sv_to_ipxact

설치 확인
---------

설치가 성공적으로 완료되었는지 확인::

    sv_to_ipxact --help

다음과 같은 도움말 메시지가 표시되어야 합니다::

    usage: sv_to_ipxact [-h] -i INPUT [-o OUTPUT] [--rebuild] ...

문서 생성 (선택사항)
--------------------

문서를 로컬에서 생성하려면::

    pip install -r docs_requirements.txt
    ./generate_docs.sh

생성된 HTML 문서는 ``docs/_build/html/index.html`` 에서 확인할 수 있습니다.
