"""Cache-Control helpers for static file serving (WhiteNoise).

Hashed Vite/Django assets stay long-cached via WhiteNoise's immutable detection.
HTML entry documents (notably the collected SPA ``index.html`` under ``/static/``)
must revalidate on every request so deploys cannot leave tabs on a stale shell.
"""


def whitenoise_add_headers(headers, path, url):
    """Force no-cache on HTML entry documents; leave other assets unchanged.

    Wired as ``WHITENOISE_ADD_HEADERS_FUNCTION``. WhiteNoise calls this for every
    static file after applying its default Cache-Control (``max-age=60`` for
    non-hashed files, immutable forever for hashed ones).
    """
    path_s = path or ""
    url_s = url or ""
    if path_s.endswith(".html") or url_s.endswith(".html"):
        headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
