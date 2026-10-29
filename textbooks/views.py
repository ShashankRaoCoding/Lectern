from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .ai import AIError, extract_slides, generate_explainer
from .forms import AddContentForm, PreferencesForm, SignUpForm, TextbookForm
from .models import Profile, Section, Textbook


def _profile(user) -> Profile:
    return Profile.objects.get_or_create(user=user)[0]


def signup(request):
    if request.user.is_authenticated:
        return redirect("textbook_list")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to Lectern! Add your AI API key under Preferences to get started.")
            return redirect("textbook_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def textbook_list(request):
    if request.method == "POST":
        form = TextbookForm(request.POST)
        if form.is_valid():
            tb = Textbook.objects.create(owner=request.user, title=form.cleaned_data["title"])
            return redirect("textbook_detail", pk=tb.pk)
    else:
        form = TextbookForm()
    books = request.user.textbooks.all()
    return render(request, "textbooks/list.html", {"books": books, "form": form})


@login_required
def textbook_detail(request, pk):
    tb = get_object_or_404(Textbook, pk=pk, owner=request.user)
    return render(request, "textbooks/detail.html", {"tb": tb, "sections": tb.sections.all()})


@login_required
@require_POST
def textbook_delete(request, pk):
    tb = get_object_or_404(Textbook, pk=pk, owner=request.user)
    tb.delete()
    messages.success(request, "Textbook deleted.")
    return redirect("textbook_list")


@login_required
def textbook_read(request, pk):
    tb = get_object_or_404(Textbook, pk=pk, owner=request.user)
    return render(request, "textbooks/read.html", {"tb": tb, "sections": tb.sections.all()})


@login_required
def add_content(request, pk):
    tb = get_object_or_404(Textbook, pk=pk, owner=request.user)

    if request.method == "POST":
        form = AddContentForm(request.POST, request.FILES, textbook=tb)
        if form.is_valid():
            data = form.cleaned_data
            upload = data["pptx"]
            title = data["title"] or (upload.name.rsplit(".", 1)[0] if upload else "Untitled")
            text = data["text"]
            source = ""
            if upload:
                profile = _profile(request.user)
                api_key = profile.get_api_key()
                if not api_key:
                    messages.warning(request, "Add your AI API key in Preferences to use .pptx upload.")
                    return redirect("preferences")
                try:
                    slides = extract_slides(upload)
                    text = generate_explainer(api_key, slides, title, profile.ai_model)
                except AIError as exc:
                    messages.error(request, str(exc))
                    return render(request, "textbooks/add_content.html", {"tb": tb, "form": form})
                source = upload.name

            target = data["append_to"]
            if target:
                target.markdown = target.markdown.rstrip() + "\n\n" + text
                target.save()
                messages.success(request, f"Appended to “{target.title}”.")
                return redirect("section_read", pk=tb.pk, section_pk=target.pk)
            section = Section.objects.create(
                textbook=tb,
                title=title,
                source_filename=source,
                markdown=text,
                position=tb.sections.count(),
            )
            messages.success(request, "Section added.")
            return redirect("section_read", pk=tb.pk, section_pk=section.pk)
    else:
        initial = {}
        if request.GET.get("section", "").isdigit():
            initial["append_to"] = int(request.GET["section"])
        form = AddContentForm(textbook=tb, initial=initial)
    return render(request, "textbooks/add_content.html", {"tb": tb, "form": form})


@login_required
def section_read(request, pk, section_pk):
    tb = get_object_or_404(Textbook, pk=pk, owner=request.user)
    section = get_object_or_404(Section, pk=section_pk, textbook=tb)
    return render(request, "textbooks/section.html", {"tb": tb, "section": section})


@login_required
@require_POST
def section_reorder(request, pk, section_pk):
    tb = get_object_or_404(Textbook, pk=pk, owner=request.user)
    section = get_object_or_404(Section, pk=section_pk, textbook=tb)
    direction = request.POST.get("direction")

    sections = list(tb.sections.order_by("position", "created_at", "id"))
    index = next((i for i, item in enumerate(sections) if item.pk == section.pk), None)
    if index is None:
        return redirect("textbook_detail", pk=tb.pk)

    if direction == "up":
        target_index = index - 1
    elif direction == "down":
        target_index = index + 1
    else:
        return redirect("textbook_detail", pk=tb.pk)

    if 0 <= target_index < len(sections):
        sections[index], sections[target_index] = sections[target_index], sections[index]
        for new_position, item in enumerate(sections, start=1):
            if item.position != new_position:
                item.position = new_position
                item.save(update_fields=["position"])

    return redirect("textbook_detail", pk=tb.pk)


@login_required
@require_POST
def section_delete(request, pk, section_pk):
    tb = get_object_or_404(Textbook, pk=pk, owner=request.user)
    get_object_or_404(Section, pk=section_pk, textbook=tb).delete()
    messages.success(request, "Section deleted.")
    return redirect("textbook_detail", pk=tb.pk)


@login_required
def preferences(request):
    profile = _profile(request.user)
    if request.method == "POST":
        form = PreferencesForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["clear_key"]:
                profile.set_api_key("")
                messages.success(request, "API key removed.")
            elif form.cleaned_data["api_key"]:
                profile.set_api_key(form.cleaned_data["api_key"])
                messages.success(request, "API key saved.")
            profile.ai_model = form.cleaned_data["ai_model"]
            profile.save()
            return redirect("preferences")
    else:
        form = PreferencesForm(initial={"ai_model": profile.ai_model})
    return render(request, "textbooks/preferences.html", {"form": form, "profile": profile})
