from collections import deque
from typing import Any, Dict, List, Optional, Set
from django.db.models import Q
from apps.members.models import Person
from apps.relationships.models import MarriagePartnership, Relationship

class TreeEngine:
    """
    Constructs a React Flow compatible graph of nodes and edges
    optimized for rendering clean, readable genealogical lineages.
    """

    def __init__(self, family, root_person_id: Optional[str] = None, depth: int = 10, direction: str = "both", request=None):
        self.family = family
        self.root_person_id = root_person_id
        self.max_depth = min(max(1, depth), 12)
        self.direction = direction
        self.request = request

    def build_tree(self) -> Dict[str, Any]:
        family_members = Person.objects.filter(family=self.family)
        if not family_members.exists():
            return {"meta": {"totalNodes": 0, "totalEdges": 0}, "nodes": [], "edges": []}

        # 1. Resolve Root Person
        root_person = None
        if self.root_person_id:
            root_person = family_members.filter(id=self.root_person_id).first()

        if not root_person:
            child_person_ids = Relationship.objects.filter(
                family=self.family,
                relationship_type=Relationship.Type.PARENT_CHILD,
            ).values_list("person_b_id", flat=True)

            root_candidates = family_members.exclude(id__in=child_person_ids).order_by("birth_date", "created_at")
            root_person = root_candidates.first() or family_members.first()

        # 2. Graph Traversal: BFS
        visited_people: Dict[str, Person] = {str(root_person.id): root_person}
        generation_map: Dict[str, int] = {str(root_person.id): 0}

        # Traverse Ancestors (Upward)
        if self.direction in ("ancestors", "both"):
            self._traverse_ancestors(str(root_person.id), visited_people, generation_map)

        # Traverse Descendants (Downward)
        if self.direction in ("descendants", "both"):
            self._traverse_descendants(str(root_person.id), visited_people, generation_map)

        # Include any remaining unvisited members of the family (e.g. newly added members or separate branches)
        remaining = family_members.exclude(id__in=[p.id for p in visited_people.values()])
        for rem in remaining:
            rem_id = str(rem.id)
            if rem_id not in visited_people:
                visited_people[rem_id] = rem
                generation_map[rem_id] = 0
                if self.direction in ("descendants", "both"):
                    self._traverse_descendants(rem_id, visited_people, generation_map)
                if self.direction in ("ancestors", "both"):
                    self._traverse_ancestors(rem_id, visited_people, generation_map)

        # 3. Discover Spouses for all traversed people
        visited_ids = set(visited_people.keys())
        spouse_pairs = self._find_spouses_for_nodes(visited_ids, visited_people, generation_map)

        # 4. Generate Nodes & Edges
        nodes = []
        edges = []
        edge_ids_seen = set()

        for person_id, person in visited_people.items():
            gen = generation_map.get(person_id, 0)
            nodes.append({
                "id": f"person-{person.id}",
                "type": "personNode",
                "position": {"x": 0, "y": 0},
                "data": {
                    "id": str(person.id),
                    "firstName": person.first_name,
                    "middleName": person.middle_name,
                    "lastName": person.last_name,
                    "fullName": person.full_name,
                    "gender": person.gender,
                    "birthDisplay": person.birth_display,
                    "deathDisplay": person.death_display,
                    "lifespan": person.lifespan,
                    "birthPlace": person.birth_place,
                    "isLiving": person.is_living,
                    "occupation": person.occupation,
                    "photoUrl": (
                        self.request.build_absolute_uri(person.profile_photo.url)
                        if self.request and person.profile_photo
                        else (person.profile_photo.url if person.profile_photo else None)
                    ),
                    "generation": gen,
                },
            })

        # 5. Parent-Child Edges: Deduplicate per child so there is only 1 clean orthogonal lineage line
        parent_relationships = Relationship.objects.filter(
            family=self.family,
            relationship_type=Relationship.Type.PARENT_CHILD,
            person_a_id__in=visited_ids,
            person_b_id__in=visited_ids,
        ).select_related("person_a", "person_b")

        # Sort so male/father parent comes first to avoid criss-crossing double lines
        sorted_parent_rels = sorted(
            parent_relationships,
            key=lambda r: 0 if r.person_a.gender == Person.Gender.MALE else 1
        )

        child_line_seen = set()
        for rel in sorted_parent_rels:
            child_id = str(rel.person_b_id)
            if child_id in child_line_seen:
                continue
            child_line_seen.add(child_id)

            edge_id = f"edge-pc-{rel.person_a_id}-{rel.person_b_id}"
            if edge_id not in edge_ids_seen:
                edge_ids_seen.add(edge_id)
                edges.append({
                    "id": edge_id,
                    "source": f"person-{rel.person_a_id}",
                    "target": f"person-{rel.person_b_id}",
                    "type": "smoothstep",
                    "animated": False,
                    "style": {"stroke": "#475569", "strokeWidth": 2.5},
                    "data": {
                        "relationshipType": "PARENT_CHILD",
                        "subtype": rel.relationship_subtype,
                    },
                })

        # 6. Spouse Edges between married couples with wedding ring styling
        for p1_id, p2_id, partnership_type, end_reason in spouse_pairs:
            edge_id = f"edge-sp-{min(p1_id, p2_id)}-{max(p1_id, p2_id)}"
            if edge_id not in edge_ids_seen:
                edge_ids_seen.add(edge_id)
                edges.append({
                    "id": edge_id,
                    "source": f"person-{p1_id}",
                    "target": f"person-{p2_id}",
                    "sourceHandle": "spouse-right",
                    "targetHandle": "spouse-left",
                    "type": "straight",
                    "animated": False,
                    "label": "⚭",
                    "labelStyle": {"fill": "#d97706", "fontWeight": 700, "fontSize": 18},
                    "labelBgPadding": [4, 4],
                    "labelBgBorderRadius": 6,
                    "labelBgStyle": {"fill": "#fffbeb", "stroke": "#fbbf24", "strokeWidth": 1},
                    "style": {"stroke": "#d97706", "strokeWidth": 2},
                    "data": {
                        "relationshipType": "SPOUSE",
                        "partnershipType": partnership_type,
                        "endReason": end_reason,
                    },
                })

        return {
            "meta": {
                "familyId": str(self.family.id),
                "rootPersonId": str(root_person.id),
                "rootPersonName": root_person.full_name,
                "totalNodes": len(nodes),
                "totalEdges": len(edges),
                "depth": self.max_depth,
            },
            "nodes": nodes,
            "edges": edges,
        }

    def _traverse_ancestors(self, root_id: str, visited: Dict[str, Person], gen_map: Dict[str, int]):
        queue = deque([(root_id, 0)])
        while queue:
            curr_id, curr_depth = queue.popleft()
            if curr_depth >= self.max_depth:
                continue

            parent_rels = Relationship.objects.filter(
                family=self.family,
                person_b_id=curr_id,
                relationship_type=Relationship.Type.PARENT_CHILD,
            ).select_related("person_a")

            for rel in parent_rels:
                parent = rel.person_a
                parent_id = str(parent.id)
                if parent_id not in visited:
                    visited[parent_id] = parent
                    gen_map[parent_id] = gen_map[curr_id] - 1
                    queue.append((parent_id, curr_depth + 1))

    def _traverse_descendants(self, root_id: str, visited: Dict[str, Person], gen_map: Dict[str, int]):
        queue = deque([(root_id, 0)])
        while queue:
            curr_id, curr_depth = queue.popleft()
            if curr_depth >= self.max_depth:
                continue

            child_rels = Relationship.objects.filter(
                family=self.family,
                person_a_id=curr_id,
                relationship_type=Relationship.Type.PARENT_CHILD,
            ).select_related("person_b")

            for rel in child_rels:
                child = rel.person_b
                child_id = str(child.id)
                if child_id not in visited:
                    visited[child_id] = child
                    gen_map[child_id] = gen_map[curr_id] + 1
                    queue.append((child_id, curr_depth + 1))

    def _find_spouses_for_nodes(self, visited_ids: Set[str], visited: Dict[str, Person], gen_map: Dict[str, int]):
        spouse_pairs = []

        # From MarriagePartnership
        marriages = MarriagePartnership.objects.filter(
            family=self.family
        ).filter(
            Q(partner_1_id__in=visited_ids) | Q(partner_2_id__in=visited_ids)
        ).select_related("partner_1", "partner_2")

        for m in marriages:
            p1_id, p2_id = str(m.partner_1_id), str(m.partner_2_id)
            if p1_id not in visited and p2_id in visited:
                visited[p1_id] = m.partner_1
                gen_map[p1_id] = gen_map[p2_id]
                visited_ids.add(p1_id)
            elif p2_id not in visited and p1_id in visited:
                visited[p2_id] = m.partner_2
                gen_map[p2_id] = gen_map[p1_id]
                visited_ids.add(p2_id)

            spouse_pairs.append((p1_id, p2_id, m.partnership_type, m.end_reason))

        # Also check Relationship SPOUSE
        spouse_rels = Relationship.objects.filter(
            family=self.family,
            relationship_type__in=[Relationship.Type.SPOUSE, Relationship.Type.PARTNER],
        ).filter(
            Q(person_a_id__in=visited_ids) | Q(person_b_id__in=visited_ids)
        ).select_related("person_a", "person_b")

        for r in spouse_rels:
            pa_id, pb_id = str(r.person_a_id), str(r.person_b_id)
            if pa_id not in visited and pb_id in visited:
                visited[pa_id] = r.person_a
                gen_map[pa_id] = gen_map[pb_id]
                visited_ids.add(pa_id)
            elif pb_id not in visited and pa_id in visited:
                visited[pb_id] = r.person_b
                gen_map[pb_id] = gen_map[pa_id]
                visited_ids.add(pb_id)

            spouse_pairs.append((pa_id, pb_id, "MARRIAGE", "ONGOING"))

        return spouse_pairs
