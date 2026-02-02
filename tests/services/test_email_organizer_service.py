import pytest
from unittest.mock import MagicMock

from app.services.email_organizer import EmailOrganizerService


@pytest.fixture
def fake_table():
    table = MagicMock()
    table._items = {}

    def put_item(Item):
        table._items[Item["groupId"]] = Item

    def get_item(Key):
        item = table._items.get(Key["groupId"])
        return {"Item": item} if item else {}

    def delete_item(Key):
        table._items.pop(Key["groupId"], None)

    def update_item(Key, UpdateExpression, ExpressionAttributeValues, **kwargs):
        item = table._items[Key["groupId"]]
        for k, v in ExpressionAttributeValues.items():
            field = k.replace(":", "")
            item[field] = v
        table._items[Key["groupId"]] = item
        return {"Attributes": item}

    table.put_item.side_effect = put_item
    table.get_item.side_effect = get_item
    table.delete_item.side_effect = delete_item
    table.update_item.side_effect = update_item

    return table


@pytest.fixture
def service(fake_table):
    return EmailOrganizerService(db_table=fake_table)


# =======================
# GROUPS
# =======================
def test_create_group(service, fake_table):
    group = service.create_group("g1", "Marketing", managers=["u1"])

    assert group["groupId"] == "g1"
    assert group["groupName"] == "Marketing"
    assert group["managers"] == ["u1"]
    assert group["recipients"] == []
    assert "g1" in fake_table._items


def test_get_group(service):
    service.create_group("g1", "Sales")
    group = service.get_group("g1")

    assert group["groupName"] == "Sales"


def test_update_group(service):
    service.create_group("g1", "Old Name")
    res = service.update_group("g1", {"groupName": "New Name"})

    assert res["message"] == "Group g1 updated"
    assert service.get_group("g1")["groupName"] == "New Name"


def test_delete_group(service, fake_table):
    service.create_group("g1", "Temp")
    service.delete_group("g1")

    assert "g1" not in fake_table._items


# =======================
# RECIPIENTS
# =======================
def test_add_recipients(service):
    service.create_group("g1", "Team")

    recipients = service.add_recipients("g1", ["a@test.com", "b@test.com"])
    recipients = service.add_recipients("g1", ["a@test.com", "c@test.com"])

    assert set(recipients) == {"a@test.com", "b@test.com", "c@test.com"}


def test_replace_recipients(service):
    service.create_group("g1", "Team")

    recipients = service.replace_recipients("g1", ["x@test.com"])
    assert recipients == ["x@test.com"]


def test_remove_recipient(service):
    service.create_group("g1", "Team")
    service.add_recipients("g1", ["a@test.com", "b@test.com"])

    recipients = service.remove_recipient("g1", "a@test.com")
    assert recipients == ["b@test.com"]


def test_add_recipients_group_not_found(service):
    assert service.add_recipients("missing", ["a@test.com"]) is None


# =======================
# MANAGERS
# =======================
def test_add_manager(service):
    service.create_group("g1", "Team")

    managers = service.add_manager("g1", "u1")
    managers = service.add_manager("g1", "u1")

    assert managers == ["u1"]


def test_remove_manager(service):
    service.create_group("g1", "Team", managers=["u1", "u2"])

    managers = service.remove_manager("g1", "u1")
    assert managers == ["u2"]


# =======================
# LOGS
# =======================
def test_add_and_get_logs(service):
    service.create_group("g1", "Team")

    logs = service.add_log("g1", "EMAIL_SENT")
    logs = service.add_log("g1", "RECIPIENT_ADDED")

    assert len(logs) == 2
    assert logs[0]["action"] == "EMAIL_SENT"
    assert logs[1]["action"] == "RECIPIENT_ADDED"

    fetched_logs = service.get_logs("g1")
    assert fetched_logs == logs
