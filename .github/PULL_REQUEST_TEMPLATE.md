## Summary

<!-- What changed and why. Link related issues (e.g. Fixes #123). -->

## Surface

- [ ] Vue SPA (`frontend-vue/`, `/seim/`)
- [ ] REST API (`/api/`)
- [ ] Wagtail CMS
- [ ] Backend / data model
- [ ] Tests or CI
- [ ] Docs

## Test plan

<!-- How you verified this. Include role (student / coordinator / admin) if UI. -->

- [ ] `make test` (or equivalent backend pytest)
- [ ] `npm --prefix frontend-vue run test:run` (if SPA changed)
- [ ] `make quality-check` or `ruff check .`

## Checklist

- [ ] No secrets, `.env`, or credentials in the diff
- [ ] Docs or comments updated if behavior changed
- [ ] PR targets `main` and will stay green on CI
