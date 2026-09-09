# WiCal 지원 사이트

WiCal의 한국어·영어 지원 페이지와 개인정보처리방침을 만드는 정적 사이트다. 앱 소스와 분리된 문서 전용 저장소로 공개할 예정이다. Python 3 표준 라이브러리만 사용하며 외부 스크립트, 폰트, 방문 분석 및 문의 폼은 포함하지 않는다.

운영자, 문의 이메일 및 문의 메일 보관 기준은 2026-09-09 확인됐다. 문의 이메일과 첨부자료는 문의 처리와 후속 대응이 끝나면 삭제될 예정이다.

## 콘텐츠 수정

- `site.json`: 공개 기본 URL, 운영자, 문의 이메일, 시행일 및 실제 문의 메일 보관 기준.
- `content.json`: 한국어·영어 문구. 실제 앱 동작과 외부 서비스 처리가 바뀌면 두 언어를 함께 수정한다.
- `assets/`: 스타일과 기존 WiCal 앱 아이콘.
- `build.py`: HTML 및 사이트맵 생성.

`support_retention`은 운영자가 정한 실제 기준을 `{"ko": "한국어 문구", "en": "English text"}` 형식으로 넣는다. 기간이나 삭제 시점을 임의로 정하지 않는다. 실제로 게시할 때 시행일도 확인한다.

## 로컬 검토

```bash
python3 build.py --preview
mkdir -p /tmp/wical-site-preview
ln -sfn "$PWD/_site" /tmp/wical-site-preview/wical-site
python3 -m http.server 8765 --bind 127.0.0.1 --directory /tmp/wical-site-preview
```

브라우저에서 `http://127.0.0.1:8765/wical-site/`를 연다. 초안은 배너와 `noindex`를 포함하고 `_site/`는 Git에서 제외한다.

## 배포 준비

운영 정보가 확정되면 아래 명령으로 배포 파일을 만든다. 필수 설정이 없거나 보관 기준의 한·영 문구가 비어 있으면 공개 빌드는 중단된다.

```bash
python3 build.py --output docs
```

생성된 `docs/`를 검토한 다음 문서 전용 공개 저장소 `SeokBA/wical-site`의 `main`에 커밋한다. GitHub Pages는 `main` 브랜치의 `/docs`에서 게시하도록 설정한다. 생성 스크립트를 실행하는 것만으로 원격 게시되지는 않는다.

공개 주소:

- 한국어 지원: `https://seokba.github.io/wical-site/ko/support/`
- 영어 지원: `https://seokba.github.io/wical-site/en/support/`
- 한국어 개인정보처리방침: `https://seokba.github.io/wical-site/ko/privacy/`
- 영어 개인정보처리방침: `https://seokba.github.io/wical-site/en/privacy/`

실제 HTTPS 응답과 본문을 확인한 후 App Store Connect의 각 언어 URL을 등록한다. 앱 설정에 링크를 추가하면 현재 업로드된 빌드 4와 별개의 빌드 번호로 검증·업로드해야 한다.

게시 절차 참고: [GitHub Pages 사이트 만들기](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site), [GitHub Pages HTTPS](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).
