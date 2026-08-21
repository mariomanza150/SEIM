Vue SPA Frontend
================

The Django ``frontend`` app and ``templates/frontend/`` SSR UI are **removed**.
Application UI is the **Vue 3.5 + Vite 7** SPA in ``frontend-vue/``, served at
``/seim/``. Wagtail CMS templates under ``cms/templates/`` serve the public site
at ``/``.

Overview
--------

Current frontend stack:

* **Vue 3 SPA** at ``/seim/*`` — dashboards, applications, documents, staff UI
* **Pinia** stores and **Vue Router 4** client routes
* **Bootstrap 5** + shared tokens: ``static/css/utilities/seim-shared-tokens.css``
* **Build output**: ``frontend-vue/dist/`` collected to static files
* **Vite base**: ``/static/`` (see ``frontend-vue/vite.config.js``)

Development
-----------

From the repo root:

.. code-block:: bash

   npm --prefix frontend-vue install
   npm --prefix frontend-vue run dev      # Vite dev server (optional)
   npm --prefix frontend-vue run build    # Production bundle
   python manage.py collectstatic --noinput

Unit tests use **Vitest**:

.. code-block:: bash

   npm --prefix frontend-vue run test:run

E2E tests use **Playwright** (``tests/e2e_playwright/``):

.. code-block:: bash

   make e2e-test

Staff vs Django admin
---------------------

* **Vue staff UI**: ``/seim/admin/*`` (programs, dynforms builder, workflows)
* **Django admin**: ``/seim/django-admin/`` (ORM models, users, config)
* **Wagtail CMS admin**: ``/cms/``

Historical Django frontend (removed)
------------------------------------

The removed ``frontend`` Django app provided Bootstrap 5 SSR pages, ``static/js/main.js``,
and django-template dashboards. Those paths now redirect to the Vue SPA or Wagtail.
Do not reintroduce ``.. automodule:: frontend`` — the package no longer exists.

Related Documentation
--------------------

* :doc:`frontend_guide` — Maintainer guide (Vue patterns, auth store)
* :doc:`api` — REST API used by the SPA
* ``docs/notes/SPA_VS_LEGACY.md`` — Remaining Django-template leftovers
