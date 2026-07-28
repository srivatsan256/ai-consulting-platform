"""Seed LevelModule records from the static LEVEL_REQUIREMENTS definitions."""
from django.core.management.base import BaseCommand
from verification.models import (
    LevelModule, LevelMustInclude, LevelRecommended,
    LevelKeyPrompt, LevelRequiredDoc, LevelRequirementItem,
)
from verification.level_data import LEVEL_REQUIREMENTS, TOTAL_LEVELS


class Command(BaseCommand):
    help = "Seed level modules from static definitions in level_data.py"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for level_num, config in LEVEL_REQUIREMENTS.items():
            module, created = LevelModule.objects.update_or_create(
                level=level_num,
                defaults={
                    "title": config["title"],
                    "icon": config.get("icon", "folder"),
                    "color": config.get("color", "gray"),
                    "description": config.get("description", ""),
                    "is_active": True,
                    "order": level_num,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(f"  Created Level {level_num}: {config['title']}")
            else:
                updated_count += 1
                self.stdout.write(f"  Updated Level {level_num}: {config['title']}")

            # Clear and recreate child items
            module.must_include_items.all().delete()
            for i, text in enumerate(config.get("must_include", [])):
                LevelMustInclude.objects.create(module=module, text=text, order=i)

            module.recommended_items.all().delete()
            for i, text in enumerate(config.get("recommended", [])):
                LevelRecommended.objects.create(module=module, text=text, order=i)

            module.key_prompts_items.all().delete()
            for i, text in enumerate(config.get("key_prompts", [])):
                LevelKeyPrompt.objects.create(module=module, text=text, order=i)

            module.required_doc_items.all().delete()
            for i, doc in enumerate(config.get("required_documents", [])):
                LevelRequiredDoc.objects.create(
                    module=module, doc_type=doc["doc_type"], label=doc["label"], order=i
                )

            module.requirement_items.all().delete()
            for i, req in enumerate(config.get("requirements", [])):
                LevelRequirementItem.objects.create(
                    module=module,
                    key=req["key"],
                    label=req["label"],
                    is_required=req.get("required", True),
                    aliases=req.get("aliases", []),
                    order=i,
                )

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created: {created_count}, Updated: {updated_count} level modules."
        ))
