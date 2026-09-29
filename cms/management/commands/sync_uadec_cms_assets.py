"""Download uadec.mx CMS assets and attach hero images to key landing pages."""

from django.core.management.base import BaseCommand

from cms.context_processors import refresh_cms_assets_manifest
from cms.models import HomePage, InternationalHomePage, MovilidadLandingPage
from cms.utils.official_assets import (
    download_all_cms_assets,
    get_or_create_wagtail_image,
    images_dir,
    logos_dir,
)


class Command(BaseCommand):
    help = (
        "Download official uadec.mx logos, CGRI photos, and homepage slides; "
        "attach MI2026 hero to HomePage, InternationalHomePage, and MovilidadLandingPage."
    )

    def handle(self, *args, **options):
        self.stdout.write("Downloading uadec.mx CMS assets...")

        try:
            saved = download_all_cms_assets()
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Download failed: {exc}"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"  Saved {len(saved)} files to branding/uadec/")
        )

        manifest_path = refresh_cms_assets_manifest()
        self.stdout.write(self.style.SUCCESS(f"  Wrote asset manifest: {manifest_path}"))

        hero_path = saved.get("mi2026.jpg") or logos_dir() / "mi2026.jpg"
        if not hero_path.exists():
            self.stdout.write(self.style.WARNING("  mi2026.jpg not found; skipping heroes"))
            return

        hero_image = get_or_create_wagtail_image("mi2026.jpg", hero_path)
        updated = []

        for model, slug, label in (
            (HomePage, "home", "HomePage"),
            (InternationalHomePage, "internacional", "InternationalHomePage"),
            (MovilidadLandingPage, "movilidad-estudiantil", "MovilidadLandingPage"),
        ):
            page = model.objects.filter(slug=slug).first()
            if not page:
                self.stdout.write(self.style.WARNING(f"  {label} ({slug}) not found"))
                continue
            page.hero_image = hero_image
            page.save_revision().publish()
            updated.append(label)

        if updated:
            self.stdout.write(
                self.style.SUCCESS(f"  Hero image attached to: {', '.join(updated)}")
            )

        slide_count = len(list(images_dir().glob("homepage-slide-*.png")))
        cgri_count = len(list(images_dir().glob("cgri-*.jpg")))
        webp_count = len(list(images_dir().glob("*.webp")))
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {cgri_count} CGRI photos, {slide_count} homepage slides, "
                f"{webp_count} WebP variants ready."
            )
        )
