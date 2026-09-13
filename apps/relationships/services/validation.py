from collections import deque

from rest_framework.exceptions import ValidationError

from apps.relationships.models import Relationship


def validate_no_ancestor_cycle(parent_id, child_id):
    """
    Ensures that adding a PARENT_CHILD edge (parent_id -> child_id)
    does not create a cycle. Specifically, child_id must not already be an
    ancestor of parent_id.
    """
    if parent_id == child_id:
        raise ValidationError("A person cannot be their own parent or child.")

    # BFS upwards from parent_id: find all ancestors of parent_id
    queue = deque([parent_id])
    visited = {parent_id}

    while queue:
        curr = queue.popleft()
        # Find all parents of curr (curr is person_b)
        parent_edges = Relationship.objects.filter(
            person_b_id=curr,
            relationship_type=Relationship.Type.PARENT_CHILD,
        ).values_list("person_a_id", flat=True)

        for p_id in parent_edges:
            if p_id == child_id:
                raise ValidationError(
                    "Invalid relationship: The child is already an ancestor of the parent (cycle detected)."
                )
            if p_id not in visited:
                visited.add(p_id)
                queue.append(p_id)
