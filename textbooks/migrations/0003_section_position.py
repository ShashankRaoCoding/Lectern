from django.db import migrations, models


def assign_positions(apps, schema_editor):
    Section = apps.get_model("textbooks", "Section")
    for textbook_id in Section.objects.values_list("textbook_id", flat=True).distinct():
        sections = list(Section.objects.filter(textbook_id=textbook_id).order_by("created_at", "id"))
        for index, section in enumerate(sections, start=1):
            section.position = index
            section.save(update_fields=["position"])


class Migration(migrations.Migration):
    dependencies = [
        ("textbooks", "0002_profile_ai_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="section",
            name="position",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(assign_positions, migrations.RunPython.noop),
    ]
