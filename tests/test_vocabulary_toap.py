import pytest

from .test_models import mute_post_save_signal
from .test_models import note
from .test_models import package
from .test_models import person
from .test_models import rep
from .test_models import repo
from .test_models import review
from .test_models import service
from .test_models import vulnerability


@pytest.mark.django_db
def test_actors_to_ap(person, package, service):
    assert person.to_ap == {
        "id": "https://127.0.0.1:8000/api/v0/users/@ziad",
        "type": "Person",
        "name": "ziad",
        "summary": "Hello World",
        "following": "https://127.0.0.1:8000/api/v0/users/@ziad/following/",
        "image": "https://127.0.0.1:8000/media/favicon-16x16.png",
        "inbox": "https://127.0.0.1:8000/api/v0/users/@ziad/inbox",
        "outbox": "https://127.0.0.1:8000/api/v0/users/@ziad/outbox",
        "publicKey": {
            "id": "https://127.0.0.1:8000/api/v0/users/@ziad",
            "owner": "https://127.0.0.1:8000/api/v0/users/@ziad",
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----",
        },
    }
    assert package.to_ap == {
        "id": f"https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/",
        "type": "Package",
        "purl": "pkg:maven/org.apache.logging",
        "name": "vcio",
        "followers": f"https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/followers/",
        "inbox": f"https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/inbox",
        "outbox": f"https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/outbox",
        "publicKey": {
            "id": "https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/",
            "owner": "https://127.0.0.1:8000/api/v0/users/@vcio",
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC KEY-----",
        },
    }
    assert service.to_ap == {
        "type": "Service",
        "name": "vcio",
    }


@pytest.mark.django_db
def test_objects_to_ap(repo, review, vulnerability, note, rep, mute_post_save_signal):
    assert repo.to_ap == {
        "id": f"https://127.0.0.1:8000/repository/{repo.id}/",
        "type": "Repository",
        "url": "https://github.com/nexB/fake-repo",
    }

    assert review.to_ap == {
        "id": f"https://127.0.0.1:8000/reviews/{review.id}/",
        "type": "Review",
        "headline": review.headline,
        "content": review.data,
        "author": f"https://127.0.0.1:8000/api/v0/users/@{review.author.user.username}",
        "comments": {"orderedItems": [], "totalItems": 0, "type": "OrderedCollection"},
        "commit": review.commit,
        "published": review.created_at,
        "updated": review.updated_at,
        "repository": str(repo.id),
        "filepath": review.filepath,
    }
    assert vulnerability.to_ap == {
        "id": f"https://127.0.0.1:8000/vulnerability/{vulnerability.id}/",
        "type": "Vulnerability",
        "repository": f"https://127.0.0.1:8000/repository/{vulnerability.repo.id}/",
    }

    assert note.to_ap == {
        "type": "Note",
        "id": f"https://127.0.0.1:8000/notes/{note.id}",
        "author": note.acct,
        "content": note.content,
    }

    assert rep.to_ap == {
        "type": "Like",
        "actor": "ziad@vcio",
        "object": {
            "type": "Note",
            "id": f"https://127.0.0.1:8000/notes/{note.id}",
            "author": note.acct,
            "content": note.content,
        },
    }
