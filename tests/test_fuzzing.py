import pytest
from django.contrib.auth.models import User
from django.core.management import call_command
from django.urls import reverse
from faker import Faker
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from accounts.models import UserProfile
from articles.forms import ArticleForm
from articles.models import Article, Category
from reviews.forms import ReviewForm
from reviews.models import Review


fake = Faker()
Faker.seed(20260520)


def fuzz_text_cases(count, min_words=3, max_words=14):
    return [
        " ".join(fake.words(nb=fake.random_int(min=min_words, max=max_words))).capitalize()
        for _ in range(count)
    ]


ARTICLE_TITLES = fuzz_text_cases(25, 2, 8)
ARTICLE_ABSTRACTS = fuzz_text_cases(25, 8, 18)
ARTICLE_CONTENTS = fuzz_text_cases(25, 20, 45)
REVIEW_COMMENTS = fuzz_text_cases(20, 8, 28)


@pytest.fixture
def category(db):
    return Category.objects.create(
        name=fake.unique.word().capitalize(),
        description=fake.sentence(),
    )


@pytest.fixture
def author(db):
    user = User.objects.create_user(username=f"author_{fake.unique.pyint()}", password="pass12345")
    user.profile.role = UserProfile.Role.AUTHOR
    user.profile.full_name = fake.name()
    user.profile.save()
    return user


@pytest.fixture
def other_author(db):
    user = User.objects.create_user(username=f"other_{fake.unique.pyint()}", password="pass12345")
    user.profile.role = UserProfile.Role.AUTHOR
    user.profile.save()
    return user


@pytest.fixture
def reviewer(db):
    user = User.objects.create_user(username=f"reviewer_{fake.unique.pyint()}", password="pass12345")
    user.profile.role = UserProfile.Role.REVIEWER
    user.profile.full_name = fake.name()
    user.profile.save()
    return user


@pytest.fixture
def article_factory(category, author, reviewer):
    def make_article(status=Article.Status.DRAFT, assigned_reviewer=None, owner=None):
        return Article.objects.create(
            title=fake.sentence(nb_words=5),
            abstract=fake.paragraph(nb_sentences=2),
            content=fake.paragraph(nb_sentences=8),
            author=owner or author,
            category=category,
            status=status,
            reviewer=assigned_reviewer,
        )

    return make_article


@pytest.mark.django_db
@pytest.mark.parametrize(
    "title,abstract,content",
    list(zip(ARTICLE_TITLES, ARTICLE_ABSTRACTS, ARTICLE_CONTENTS)),
)
def test_article_form_accepts_fuzzed_text_payloads(category, title, abstract, content):
    form = ArticleForm(
        data={
            "title": title,
            "abstract": abstract,
            "content": content,
            "category": category.id,
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
@pytest.mark.parametrize("comment", REVIEW_COMMENTS)
def test_review_form_accepts_fuzzed_comments(comment):
    form = ReviewForm(data={"comment": comment, "decision": Review.Decision.ACCEPTED})

    assert form.is_valid(), form.errors


@pytest.mark.django_db
@pytest.mark.parametrize("status", Article.Status.values)
def test_article_model_edit_flags_match_status(article_factory, status):
    article = article_factory(status=status)

    assert article.can_be_edited is (status in {Article.Status.DRAFT, Article.Status.REVISION_REQUIRED})


@pytest.mark.django_db
@pytest.mark.parametrize("status", Article.Status.values)
@pytest.mark.parametrize("as_owner", [True, False])
def test_author_edit_permission_matrix(client, article_factory, author, other_author, status, as_owner):
    article = article_factory(status=status)
    user = author if as_owner else other_author
    client.force_login(user)
    client.raise_request_exception = False

    response = client.get(reverse("articles:edit", args=[article.id]))

    if as_owner and status in {Article.Status.DRAFT, Article.Status.REVISION_REQUIRED}:
        assert response.status_code == 200
    elif as_owner:
        assert response.status_code == 302
    else:
        assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("status", Article.Status.values)
@pytest.mark.parametrize("as_owner", [True, False])
def test_submit_permission_matrix(client, article_factory, author, other_author, status, as_owner):
    article = article_factory(status=status)
    user = author if as_owner else other_author
    client.force_login(user)
    client.raise_request_exception = False

    response = client.post(reverse("articles:submit", args=[article.id]))
    article.refresh_from_db()

    if as_owner and status in {Article.Status.DRAFT, Article.Status.REVISION_REQUIRED}:
        assert response.status_code == 302
        assert article.status == Article.Status.SUBMITTED
    elif as_owner:
        assert response.status_code == 302
        assert article.status == status
    else:
        assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize("decision", Review.Decision.values)
def test_review_decision_updates_article_status(article_factory, reviewer, decision):
    article = article_factory(status=Article.Status.UNDER_REVIEW, assigned_reviewer=reviewer)

    Review.objects.create(
        article=article,
        reviewer=reviewer,
        comment=fake.paragraph(nb_sentences=2),
        decision=decision,
    )
    article.refresh_from_db()

    assert article.status == decision


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role,expected_status",
    [
        (UserProfile.Role.AUTHOR, 403),
        (UserProfile.Role.REVIEWER, 200),
        (UserProfile.Role.ADMIN, 403),
    ],
)
def test_reviewer_section_role_access(client, reviewer, role, expected_status):
    reviewer.profile.role = role
    reviewer.profile.save()
    client.force_login(reviewer)
    client.raise_request_exception = False

    response = client.get(reverse("articles:reviewer_list"))

    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name,args",
    [
        ("articles:list", []),
        ("articles:create", []),
        ("articles:reviewer_list", []),
        ("accounts:dashboard", []),
        ("articles:detail", [1]),
        ("reviews:list", [1]),
    ],
)
def test_anonymous_users_are_redirected(client, url_name, args):
    response = client.get(reverse(url_name, args=args))

    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "article_status,assigned,expected_status",
    [
        (Article.Status.SUBMITTED, True, 200),
        (Article.Status.UNDER_REVIEW, True, 200),
        (Article.Status.REVISION_REQUIRED, True, 200),
        (Article.Status.ACCEPTED, True, 302),
        (Article.Status.REJECTED, True, 302),
        (Article.Status.UNDER_REVIEW, False, 403),
        (Article.Status.SUBMITTED, False, 403),
        (Article.Status.REVISION_REQUIRED, False, 403),
        (Article.Status.DRAFT, False, 403),
    ],
)
def test_review_create_access_matrix(client, article_factory, reviewer, article_status, assigned, expected_status):
    article = article_factory(
        status=article_status,
        assigned_reviewer=reviewer if assigned else None,
    )
    client.force_login(reviewer)
    client.raise_request_exception = False

    response = client.get(reverse("reviews:create", args=[article.id]))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_seed_data_command_creates_demo_records():
    call_command("seed_data", verbosity=0)

    assert User.objects.filter(username="admin", is_superuser=True).exists()
    assert User.objects.filter(username="author", profile__role=UserProfile.Role.AUTHOR).exists()
    assert User.objects.filter(username="reviewer", profile__role=UserProfile.Role.REVIEWER).exists()
    assert Category.objects.count() >= 3
    assert Article.objects.count() >= 5
    assert Review.objects.count() >= 2


@pytest.mark.django_db
@settings(
    max_examples=1,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    title=st.text(min_size=1, max_size=255),
    abstract=st.text(min_size=1, max_size=1000),
    content=st.text(min_size=1, max_size=3000),
)
def test_article_form_hypothesis_minimal_text(category, title, abstract, content):
    form = ArticleForm(
        data={
            "title": title,
            "abstract": abstract,
            "content": content,
            "category": category.id,
        }
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
@settings(max_examples=1, deadline=None)
@given(comment=st.text(min_size=1, max_size=2000))
def test_review_form_hypothesis_minimal_comment(comment):
    form = ReviewForm(data={"comment": comment, "decision": Review.Decision.REVISION_REQUIRED})

    assert form.is_valid(), form.errors
