# Hajiie's Blog

이 블로그는 Astro 기반의 [Fuwari](https://github.com/saicaca/fuwari) 템플릿을 사용하여 만들어졌습니다.

## 로컬 실행과 빌드 확인

Node.js 22와 pnpm 9.14.4를 사용합니다. nvm을 사용한다면 프로젝트 폴더에서 `nvm use`로 `.nvmrc`의 버전을 선택합니다.

```sh
pnpm install --frozen-lockfile
pnpm dev
```

개발 서버는 초안을 포함합니다. 실제 배포 결과는 다음 순서로 확인합니다.

```sh
pnpm build
pnpm preview
```

터미널에 출력되는 HTTP 주소로 접속합니다. `dist/index.html`을 파일로 직접 열면 `/_astro/` 경로의 CSS·JavaScript를 불러올 수 없습니다. 프로덕션 빌드에서는 `draft: true`인 글이 제외됩니다.

## 템플릿

이 블로그는 [Astro](https://astro.build) 프레임워크와 [Fuwari](https://github.com/saicaca/fuwari) 테마를 기반으로 합니다.

::github{repo="saicaca/fuwari"}

## 라이선스

이 블로그의 콘텐츠는 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 라이선스를 따릅니다.

블로그를 구성하는 데 사용된 기본 소스 코드는 MIT 라이선스를 따릅니다.
