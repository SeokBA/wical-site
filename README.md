# WiCal 지원 사이트

WiCal의 한국어·영어 지원 페이지와 개인정보처리방침을 만드는 정적 사이트다. 앱 소스와 분리된 문서 전용 공개 저장소에서 관리한다. Python 3 표준 라이브러리만 사용하며 외부 스크립트, 폰트, 방문 분석 및 문의 폼은 포함하지 않는다.

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

실제 HTTPS 응답과 본문을 확인한 후 App Store Connect의 각 언어 URL을 등록한다. 앱 설정에 포함된 링크를 변경하면 빌드 번호를 증가시켜 검증·업로드한다.

게시 절차 참고: [GitHub Pages 사이트 만들기](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site), [GitHub Pages HTTPS](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).

## 대표 사이트 통합 (2026-09-10)

기존 `wical-publisher-site`의 Git 이력과 배포 설정을 이 저장소에 통합했다. 지원·개인정보 문구, 대표 사이트와 app-ads.txt를 이제 이 프로젝트에서 함께 관리한다.

```text
site.json / content.json   공통 운영 정보·한영 지원/정책 문구
assets/                    지원 사이트 원본 자산
publisher/                 대표 페이지 템플릿·app-ads.txt·robots.txt 원본
build.py                   두 배포 대상 생성
 docs/                     기존 GitHub Pages 배포 결과
 dist/                     기존 Sites 배포 결과
.openai/hosting.json        기존 Sites 프로젝트 연결 (유지)
```

`python3 build.py --output docs`로 두 결과를 함께 생성한다. `docs/`와 `dist/`를 직접 수정하지 않는다. 대표 페이지의 지원 주소·운영자·이메일은 `site.json`에서 주입한다. `--preview`는 기존처럼 `_site/`만 만들며 배포용 `dist/`를 덮어쓰지 않는다.

배포 주소는 그대로 유지한다.

- 지원·개인정보: `https://seokba.github.io/wical-site/` → GitHub Pages의 `main:/docs`.
- 대표 페이지: `https://wical-support.hjkim2714.chatgpt.site/` → 동일 Sites 프로젝트의 `dist/`.
- 광고 인증: 대표 페이지 호스트의 `/app-ads.txt`.

GitHub 원격 `origin`은 유지했다. Sites 게시 시에도 이 저장소 루트의 기존 `.openai/hosting.json`을 사용하고, 새 Sites 프로젝트를 생성하지 않는다. 배포할 정확한 커밋을 Sites 소스 저장소에 전송한 뒤 `dist/`를 패키징하여 기존 프로젝트에 게시한다. GitHub push와 Sites 게시가 서로를 자동 실행하지는 않는다.

이번 작업은 로컬 소스 통합이다. 생성 결과의 모든 파일이 통합 전과 바이트 단위로 같음을 확인했으므로 기존 게시 버전을 유지했다. 원격 push, 재배포, 앱·App Store URL 변경은 수행하지 않았다.

원래 publisher 저장소와 파일은 `/Users/tuna/orca/backups/wical-site-consolidation-20260910/`에 보관한다. 이력은 이 저장소의 merge 커밋에도 남아 있다.
