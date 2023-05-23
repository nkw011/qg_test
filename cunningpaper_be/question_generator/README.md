# Question Generator

## ⚠️ NOTICE ⚠️

### 1. farm-haystack 버전
PDF를 읽고 Text로 변환하기위해서 haystack을 버전을 업그레이드 해야합니다.
* 권장 버전: 1.15.0
```
pip install farm-haystack==1.15.0

or

pip install farm-haystack --upgrade
```

### 2. PyMuPDF 라이브러리 설치
PDFReader를 사용하기위해 외부 라이브러리인 [PyMuPDF](https://github.com/pymupdf/PyMuPDF)를 설치해야합니다.
```
python -m pip install --upgrade pymupdf
```

### 3. OCR 라이브러리 설치
PDF를 OCR을 사용해서 읽어올 수도 있습니다.
이를 위해 [Tesseract OCR](https://github.com/tesseract-ocr/tesseract), [Python Tesseract](https://github.com/madmaze/pytesseract)를 모두 설치해야합니다.
* [Tesseract OCR 설치 가이드](https://tesseract-ocr.github.io/tessdoc/Installation.html): MAC OSX는 brew를 이용해 설치할 것을 권장함
* Python Tesseract: `pip install pytesseract`

추가로 poppler error가 발생할 수도 있습니다. pdf를 image로 변환할 때 발생하는 error입니다. poppler를 설치하면 해결할 수 있습니다.
* MAC OSX: `brew install poppler`
* Windows: Windows는 어떻게 설치할지 아직 찾지 못하였습니다. 아래 링크를 참고해서 검색하시면 될 것 같습니다.
    * 검색 키워드: `poppler windows`, `poppler installation in windows`
    * [연관 링크1](https://towardsdatascience.com/poppler-on-windows-179af0e50150)