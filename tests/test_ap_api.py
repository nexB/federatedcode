#
# Copyright (c) nexB Inc. and others. All rights reserved.
# VulnerableCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/vulnerablecode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import datetime
import json
from datetime import datetime
from datetime import timedelta

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.models import AccessToken
from oauth2_provider.models import Application
from rest_framework.test import APIClient

from fedcode.activitypub import AP_CONTEXT
from fedcode.models import Follow
from fedcode.models import Note
from fedcode.models import Person
from fedcode.models import Review
from fedcode.models import Vulnerability
from fedcode.utils import generate_webfinger
from federatedcode.settings import AP_CONTENT_TYPE

from .test_models import follow
from .test_models import mute_post_save_signal
from .test_models import note
from .test_models import package
from .test_models import person
from .test_models import repo
from .test_models import review
from .test_models import service
from .test_models import vulnerability


def create_token(user):
    app = Application.objects.create(
        client_type=Application.CLIENT_CONFIDENTIAL,
        authorization_grant_type=Application.GRANT_PASSWORD,
        redirect_uris="https://127.0.0.1:8000/",
        name="purl-sync",
        user=user,
    )
    token = AccessToken.objects.create(
        user=user,
        scope="read write",
        expires=datetime.now() + timedelta(seconds=500),
        token="fake-access-key",
        application=app,
    )
    return f"Bearer {token}"


@pytest.mark.django_db
def test_get_ap_profile_user(person, service):
    client = APIClient()
    response_person = client.get(
        reverse("user-ap-profile", args=[person.user.username]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )

    response_service = client.get(
        reverse("user-ap-profile", args=[service.user.username]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )

    assert json.loads(response_person.content) == {
        "type": "Person",
        "name": "ziad",
        "summary": "Hello World",
        "following": "https://127.0.0.1:8000/api/v0/users/@ziad/following/",
        "id": "https://127.0.0.1:8000/api/v0/users/@ziad",
        "image": "https://127.0.0.1:8000/media/favicon-16x16.png",
        "inbox": "https://127.0.0.1:8000/api/v0/users/@ziad/inbox",
        "outbox": "https://127.0.0.1:8000/api/v0/users/@ziad/outbox",
        "publicKey": {
            "id": "https://127.0.0.1:8000/api/v0/users/@ziad",
            "owner": "https://127.0.0.1:8000/api/v0/users/@ziad",
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC " "KEY-----",
        },
    }

    assert json.loads(response_service.content) == {"name": "vcio", "type": "Service"}


@pytest.mark.django_db
def test_get_ap_profile_package(package):
    client = APIClient()
    response = client.get(
        reverse("purl-ap-profile", args=[package.purl]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )
    assert json.loads(response.content) == {
        "id": "https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/",
        "type": "Package",
        "purl": "pkg:maven/org.apache.logging",
        "name": "vcio",
        "followers": "https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/followers/",
        "inbox": "https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/inbox",
        "outbox": "https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/outbox",
        "publicKey": {
            "id": "https://127.0.0.1:8000/api/v0/purls/@pkg:maven/org.apache.logging/",
            "owner": "https://127.0.0.1:8000/api/v0/users/@vcio",
            "publicKeyPem": "-----BEGIN PUBLIC KEY-----...-----END PUBLIC " "KEY-----",
        },
    }


@pytest.mark.django_db
def test_get_user_inbox_empty(person):
    client = APIClient()
    auth = create_token(person.user)
    client.credentials(HTTP_AUTHORIZATION=auth)
    response = client.get(
        reverse("user-inbox", args=[person.user.username]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )

    assert json.loads(response.content) == {
        "notes": {"type": "OrderedCollection", "totalItems": 0, "orderedItems": []},
        "reviews": {"type": "OrderedCollection", "totalItems": 0, "orderedItems": []},
    }

    assert response.headers["Content-Type"] == AP_CONTENT_TYPE
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_user_inbox(person, vulnerability, review, package):
    note1 = Note.objects.create(acct=package.acct, content="yaml data1")
    note2 = Note.objects.create(acct=package.acct, content="yaml data2")
    Follow.objects.create(person=person, package=package)

    client = APIClient(enforce_csrf_checks=True)
    auth = create_token(person.user)
    client.credentials(HTTP_AUTHORIZATION=auth)
    path = reverse("user-inbox", args=[person.user.username])
    response = client.get(
        path,
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )

    assert response.headers["Content-Type"] == AP_CONTENT_TYPE
    assert response.status_code == 200
    assert json.loads(response.content) == {
        "notes": {
            "type": "OrderedCollection",
            "totalItems": 2,
            "orderedItems": [
                {
                    "id": f"https://127.0.0.1:8000/notes/{note1.id}",
                    "type": "Note",
                    "author": "pkg:maven/org.apache.logging@127.0.0.1:8000",
                    "content": "yaml data1",
                },
                {
                    "id": f"https://127.0.0.1:8000/notes/{note2.id}",
                    "type": "Note",
                    "author": "pkg:maven/org.apache.logging@127.0.0.1:8000",
                    "content": "yaml data2",
                },
            ],
        },
        "reviews": {
            "type": "OrderedCollection",
            "totalItems": 1,
            "orderedItems": [
                {
                    "id": f"https://127.0.0.1:8000/reviews/{review.id}/",
                    "type": "Review",
                    "author": "https://127.0.0.1:8000/api/v0/users/@ziad",
                    "headline": review.headline,
                    "repository": str(review.repository.id),
                    "filepath": review.filepath,
                    "content": review.data,
                    "commit": review.commit,
                    "comments": {
                        "type": "OrderedCollection",
                        "totalItems": 0,
                        "orderedItems": [],
                    },
                    "published": review.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
                    "updated": review.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
                }
            ],
        },
    }


@pytest.mark.django_db
def test_get_user_outbox_empty(person):
    client = APIClient()
    path = reverse(
        "user-outbox",
        args=[person.user.username],
    )
    response = client.get(
        path,
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )
    assert json.loads(response.content) == {
        "notes": {"type": "OrderedCollection", "totalItems": 0, "orderedItems": []},
        "reviews": {"type": "OrderedCollection", "totalItems": 0, "orderedItems": []},
    }
    assert response.headers["Content-Type"] == AP_CONTENT_TYPE
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_user_outbox(person, vulnerability, review, note):
    client = APIClient(enforce_csrf_checks=True)
    response = client.get(
        reverse("user-outbox", args=[person.user.username]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )
    assert json.loads(response.content) == {
        "notes": {"type": "OrderedCollection", "totalItems": 0, "orderedItems": []},
        "reviews": {
            "type": "OrderedCollection",
            "totalItems": 1,
            "orderedItems": [
                {
                    "id": f"https://127.0.0.1:8000/reviews/{review.id}/",
                    "type": "Review",
                    "author": f"https://127.0.0.1:8000/api/v0/users/@{review.author.user.username}",
                    "headline": review.headline,
                    "repository": str(review.repository.id),
                    "filepath": review.filepath,
                    "content": review.data,
                    "commit": review.commit,
                    "comments": {
                        "type": "OrderedCollection",
                        "totalItems": 0,
                        "orderedItems": [],
                    },
                    "published": review.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
                    "updated": review.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z",
                }
            ],
        },
    }

    assert response.headers["Content-Type"] == AP_CONTENT_TYPE
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_user_outbox(person):
    client = APIClient()
    auth = create_token(person.user)
    client.credentials(HTTP_AUTHORIZATION=auth)
    path = reverse("user-outbox", args=[person.user.username])
    response = client.post(
        path,
        {
            **AP_CONTEXT,
            "type": "Create",
            "actor": f"https://127.0.0.1:8000/api/v0/users/@{person.user.username}",
            "object": {
                "type": "Note",
                "content": "we should fix this purl",
            },
        },
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )
    assert Note.objects.count() == 1


@pytest.mark.django_db
def test_get_package_inbox_empty(package, service):
    client = APIClient()
    auth = create_token(service.user)
    client.credentials(HTTP_AUTHORIZATION=auth)

    response = client.get(
        reverse("purl-inbox", args=[package.purl]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )

    assert json.loads(response.content) == {
        "notes": {"type": "OrderedCollection", "totalItems": 0, "orderedItems": []},
    }


@pytest.mark.django_db
def test_get_package_inbox(package, service):
    note1 = Note.objects.create(
        acct=package.acct,
        content="""purl: pkg:maven/org.apache.logging@2.23-r0?arch=aarch64&distroversion=edge&reponame=community
         affected_by_vulnerabilities: [] fixing_vulnerabilities: []""",
    )
    package.notes.add(note1)
    client = APIClient()
    auth = create_token(service.user)
    client.credentials(HTTP_AUTHORIZATION=auth)

    response = client.get(
        reverse("purl-inbox", args=[package.purl]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )

    assert json.loads(response.content) == {
        "notes": {
            "orderedItems": [
                {
                    "author": "pkg:maven/org.apache.logging@127.0.0.1:8000",
                    "content": "purl: "
                    "pkg:maven/org.apache.logging@2.23-r0?arch=aarch64&distroversion=edge&reponame=community\n"
                    "         affected_by_vulnerabilities: "
                    "[] fixing_vulnerabilities: []",
                    "id": f"https://127.0.0.1:8000/notes/{note1.id}",
                    "type": "Note",
                }
            ],
            "totalItems": 1,
            "type": "OrderedCollection",
        }
    }


@pytest.mark.django_db
def test_get_package_outbox(service, package):
    client = APIClient()
    auth = create_token(service.user)
    client.credentials(HTTP_AUTHORIZATION=auth)
    note1 = Note.objects.create(acct=package.acct, content="yaml data1")
    package.notes.add(note1)

    response = client.get(
        reverse("purl-outbox", args=[package.purl]),
        headers={"Content-Type": AP_CONTENT_TYPE},
        format="json",
    )

    assert json.loads(response.content) == {
        "notes": {
            "orderedItems": [
                {
                    "author": "pkg:maven/org.apache.logging@127.0.0.1:8000",
                    "content": "yaml data1",
                    "id": f"https://127.0.0.1:8000/notes/{note1.id}",
                    "type": "Note",
                }
            ],
            "totalItems": 1,
            "type": "OrderedCollection",
        }
    }
