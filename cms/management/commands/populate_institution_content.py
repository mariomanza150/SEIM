"""Institution-agnostic alias for the example CMS seed command."""

from cms.management.commands.populate_uadec_content import Command as PopulateCommand


class Command(PopulateCommand):
    help = (
        "Populate CMS with configured institution example content "
        "(alias of populate_uadec_content; UAdeC names unless INSTITUTION_* is set)."
    )
