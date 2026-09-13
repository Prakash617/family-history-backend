import datetime

import pytest
from rest_framework.exceptions import ValidationError

from apps.families.models import Family
from apps.members.models import Person
from apps.relationships.models import Relationship
from apps.relationships.services.tree_engine import TreeEngine
from apps.relationships.services.validation import validate_no_ancestor_cycle
from apps.users.models import User


@pytest.mark.django_db
def test_cycle_detection():
    user = User.objects.create_user(email="cycle@test.local", password="Password123!")
    family = Family.objects.create(name="Cycle Test Family", owner=user)
    grandparent = Person.objects.create(family=family, first_name="Grandparent")
    parent = Person.objects.create(family=family, first_name="Parent")
    child = Person.objects.create(family=family, first_name="Child")

    # Grandparent -> Parent
    Relationship.objects.create(family=family, person_a=grandparent, person_b=parent, relationship_type=Relationship.Type.PARENT_CHILD)
    # Parent -> Child
    Relationship.objects.create(family=family, person_a=parent, person_b=child, relationship_type=Relationship.Type.PARENT_CHILD)

    # Attempting to make Child -> Grandparent must raise ValidationError!
    with pytest.raises(ValidationError):
        validate_no_ancestor_cycle(child.id, grandparent.id)


@pytest.mark.django_db
def test_tree_engine_nodes_and_edges():
    user = User.objects.create_user(email="engine@test.local", password="Password123!")
    family = Family.objects.create(name="Engine Test Family", owner=user)
    p1 = Person.objects.create(family=family, first_name="Father", birth_date=datetime.date(1950, 1, 1), gender=Person.Gender.MALE)
    p2 = Person.objects.create(family=family, first_name="Mother", birth_date=datetime.date(1952, 2, 2), gender=Person.Gender.FEMALE)
    c1 = Person.objects.create(family=family, first_name="Son", birth_date=datetime.date(1980, 3, 3), gender=Person.Gender.MALE)

    Relationship.objects.create(family=family, person_a=p1, person_b=p2, relationship_type=Relationship.Type.SPOUSE)
    Relationship.objects.create(family=family, person_a=p1, person_b=c1, relationship_type=Relationship.Type.PARENT_CHILD)
    Relationship.objects.create(family=family, person_a=p2, person_b=c1, relationship_type=Relationship.Type.PARENT_CHILD)

    engine = TreeEngine(family=family, depth=3)
    graph = engine.build_tree()

    assert graph["meta"]["totalNodes"] == 3
    assert len(graph["nodes"]) == 3
    assert len(graph["edges"]) == 3  # 1 spouse edge + 2 parent-child edges
