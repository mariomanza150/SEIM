# Course-level grade translation (subjects / carta)

SEIM reuses [`grades.services.GradeTranslationService`](../../grades/services.py) when a coordinator **confirms** host course grades on an application.

## Catalog

- Host subjects hang off a **university** (`HostInstitution`). School and academic program are optional.
- Students see institution-level subjects always, plus school- and program-level rows when those destination FKs are set.
- Unlisted host courses can be added as custom code / name / credits (XOR with a catalog pick).

## Workflow

1. After the application is `approved`, `nominated`, or `completed`, the student proposes a host grade from the institution’s `grade_scale`.
2. `POST /api/applications/{id}/propose-subject-grades/` marks rows as `proposed`.
3. `POST /api/applications/{id}/confirm-subject-grades/` (coordinator/admin) requires:
   - Host institution `grade_scale`
   - Student `profile.grade_scale`
   - A proposed host grade on every selection
4. Confirmation calls `GradeTranslationService.translate_grade` (direct mapping, then GPA-equivalent fallback) and writes `confirmed_host_grade` + `home_grade`.
5. The Carta de Homologación PDF is regenerated with host/home grade columns.
6. `POST /api/applications/{id}/reject-subject-grades/` reopens mapping and grade edits.

Admin catalog UI: `/seim/admin/programs/:id/destinations`.
