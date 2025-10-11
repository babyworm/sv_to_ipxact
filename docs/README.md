# 문서 빌드 가이드

이 디렉토리에는 sv_to_ipxact 프로젝트의 Sphinx 문서 소스가 포함되어 있습니다.

## 문서 빌드 방법

### 1. 의존성 설치

```bash
pip install -r ../docs_requirements.txt
```

### 2. HTML 문서 생성

프로젝트 루트에서:

```bash
./generate_docs.sh
```

또는 docs 디렉토리에서:

```bash
make html
```

### 3. 문서 보기

생성된 문서는 `_build/html/index.html` 에 있습니다:

```bash
# 브라우저로 열기
firefox _build/html/index.html
# 또는
google-chrome _build/html/index.html
```

## 문서 구조

```
docs/
├── conf.py              # Sphinx 설정
├── index.rst            # 메인 페이지
├── installation.rst     # 설치 가이드
├── usage.rst            # 사용 가이드
├── api.rst              # API 문서
├── examples.rst         # 예제 모음
├── Makefile             # 빌드 자동화
└── _build/              # 생성된 문서 (git 무시됨)
    └── html/
        └── index.html
```

## 문서 업데이트

1. `.rst` 파일을 수정
2. `make html`로 재빌드
3. 브라우저에서 새로고침하여 확인

## 문서 정리

```bash
make clean
```

## 참고

- Sphinx 문서: https://www.sphinx-doc.org/
- reStructuredText 문법: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
