import datetime

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.events.models import Event
from apps.families.models import Family, FamilyMembership
from apps.members.models import Person
from apps.notifications.models import Notification
from apps.relationships.models import MarriagePartnership, Relationship
from apps.stories.models import Story
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed database with 4 generations of a realistic family tree, stories, events, and media."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        # 1. Create or get Demo User
        user, created = User.objects.get_or_create(
            email="demo@familytree.local",
            defaults={
                "first_name": "Demo",
                "last_name": "Explorer",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password("Demo1234!")
        user.save()
        self.stdout.write("User demo@familytree.local configured.")

        # 2. Create Family
        family, _ = Family.objects.get_or_create(
            name="Thapa & Shrestha Historical Lineage",
            defaults={
                "description": "Historical records, memories, and ancestral tree of the Thapa family starting from Kathmandu Valley.",
                "owner": user,
                "privacy": Family.Privacy.PUBLIC,
            },
        )
        FamilyMembership.objects.get_or_create(
            family=family,
            user=user,
            defaults={"role": FamilyMembership.Role.OWNER},
        )
        self.stdout.write(f"Family '{family.name}' ready.")

        # 3. Create Generation 1: Grandparents
        ram = Person.objects.create(
            family=family,
            first_name="Ram",
            middle_name="Bahadur",
            last_name="Thapa",
            gender=Person.Gender.MALE,
            birth_date=datetime.date(1938, 3, 15),
            death_date=datetime.date(2018, 11, 20),
            birth_place="Kathmandu, Nepal",
            death_place="Kathmandu, Nepal",
            is_living=False,
            occupation="Civil Engineer & Historian",
            biography="Pioneered civic planning initiatives in Kathmandu. Avid mountaineer and preserver of traditional oral histories.",
        )
        sita = Person.objects.create(
            family=family,
            first_name="Sita",
            middle_name="Devi",
            last_name="Thapa",
            gender=Person.Gender.FEMALE,
            birth_date=datetime.date(1942, 7, 10),
            death_date=datetime.date(2021, 4, 5),
            birth_place="Patan, Lalitpur",
            death_place="Kathmandu, Nepal",
            is_living=False,
            occupation="Educator & Writer",
            biography="Taught literature for four decades and published several compendiums of traditional folklore.",
        )

        MarriagePartnership.objects.create(
            family=family,
            partner_1=ram,
            partner_2=sita,
            start_date=datetime.date(1960, 5, 2),
            start_place="Kathmandu, Nepal",
            end_reason=MarriagePartnership.EndReason.DEATH,
        )
        Relationship.objects.create(
            family=family,
            person_a=ram,
            person_b=sita,
            relationship_type=Relationship.Type.SPOUSE,
        )

        # 4. Create Generation 2: Children of Ram & Sita
        rajesh = Person.objects.create(
            family=family,
            first_name="Rajesh",
            last_name="Thapa",
            gender=Person.Gender.MALE,
            birth_date=datetime.date(1963, 8, 22),
            birth_place="Kathmandu, Nepal",
            is_living=True,
            occupation="Architect",
            biography="Specializes in sustainable heritage architecture and preservation across South Asia.",
        )
        sunita = Person.objects.create(
            family=family,
            first_name="Sunita",
            last_name="Shrestha",
            gender=Person.Gender.FEMALE,
            birth_date=datetime.date(1966, 12, 14),
            birth_place="Bhaktapur, Nepal",
            is_living=True,
            occupation="Professor of Botany",
            biography="Researches alpine flora and ethnobotany in the Himalayas.",
        )
        MarriagePartnership.objects.create(
            family=family,
            partner_1=rajesh,
            partner_2=sunita,
            start_date=datetime.date(1990, 2, 18),
            start_place="Kathmandu",
            end_reason=MarriagePartnership.EndReason.ONGOING,
        )
        Relationship.objects.create(family=family, person_a=rajesh, person_b=sunita, relationship_type=Relationship.Type.SPOUSE)

        # Parent-child links for Rajesh
        Relationship.objects.create(family=family, person_a=ram, person_b=rajesh, relationship_type=Relationship.Type.PARENT_CHILD)
        Relationship.objects.create(family=family, person_a=sita, person_b=rajesh, relationship_type=Relationship.Type.PARENT_CHILD)

        # Second sibling: Bikash Thapa
        bikash = Person.objects.create(
            family=family,
            first_name="Bikash",
            last_name="Thapa",
            gender=Person.Gender.MALE,
            birth_date=datetime.date(1968, 4, 30),
            birth_place="Kathmandu, Nepal",
            is_living=True,
            occupation="Cardiologist",
        )
        maya_g = Person.objects.create(
            family=family,
            first_name="Maya",
            last_name="Gurung",
            gender=Person.Gender.FEMALE,
            birth_date=datetime.date(1971, 9, 8),
            birth_place="Pokhara, Nepal",
            is_living=True,
            occupation="Public Health Specialist",
        )
        MarriagePartnership.objects.create(family=family, partner_1=bikash, partner_2=maya_g, start_date=datetime.date(1995, 11, 12))
        Relationship.objects.create(family=family, person_a=bikash, person_b=maya_g, relationship_type=Relationship.Type.SPOUSE)
        Relationship.objects.create(family=family, person_a=ram, person_b=bikash, relationship_type=Relationship.Type.PARENT_CHILD)
        Relationship.objects.create(family=family, person_a=sita, person_b=bikash, relationship_type=Relationship.Type.PARENT_CHILD)

        # 5. Create Generation 3: Grandchildren
        aarav = Person.objects.create(
            family=family,
            first_name="Aarav",
            last_name="Thapa",
            gender=Person.Gender.MALE,
            birth_date=datetime.date(1993, 6, 17),
            birth_place="Kathmandu, Nepal",
            is_living=True,
            occupation="Software Engineer",
            biography="Full-stack developer building open source tools and genealogical engines.",
        )
        priya = Person.objects.create(
            family=family,
            first_name="Priya",
            last_name="Thapa",
            gender=Person.Gender.FEMALE,
            birth_date=datetime.date(1997, 10, 25),
            birth_place="Kathmandu, Nepal",
            is_living=True,
            occupation="Visual Designer",
        )
        rohan = Person.objects.create(
            family=family,
            first_name="Rohan",
            last_name="Thapa",
            gender=Person.Gender.MALE,
            birth_date=datetime.date(1999, 1, 14),
            birth_place="Pokhara, Nepal",
            is_living=True,
            occupation="Medical Resident",
        )

        # Connect Aarav & Priya to Rajesh & Sunita
        for child in [aarav, priya]:
            Relationship.objects.create(family=family, person_a=rajesh, person_b=child, relationship_type=Relationship.Type.PARENT_CHILD)
            Relationship.objects.create(family=family, person_a=sunita, person_b=child, relationship_type=Relationship.Type.PARENT_CHILD)

        # Connect Rohan to Bikash & Maya
        Relationship.objects.create(family=family, person_a=bikash, person_b=rohan, relationship_type=Relationship.Type.PARENT_CHILD)
        Relationship.objects.create(family=family, person_a=maya_g, person_b=rohan, relationship_type=Relationship.Type.PARENT_CHILD)

        # 6. Create Generation 4: Great-Granddaughter
        elena = Person.objects.create(
            family=family,
            first_name="Elena",
            last_name="Thapa",
            gender=Person.Gender.FEMALE,
            birth_date=datetime.date(2023, 3, 5),
            birth_place="Kathmandu, Nepal",
            is_living=True,
            biography="The newest bright addition to the family!",
        )
        Relationship.objects.create(family=family, person_a=aarav, person_b=elena, relationship_type=Relationship.Type.PARENT_CHILD)

        # 7. Create Historical Events & Milestones
        Event.objects.create(
            family=family,
            person=ram,
            event_type=Event.EventType.BIRTH,
            title="Birth of Ram Bahadur Thapa",
            date=datetime.date(1938, 3, 15),
            place="Kathmandu, Nepal",
            description="Born in the historic center of old Kathmandu.",
        )
        Event.objects.create(
            family=family,
            person=ram,
            event_type=Event.EventType.MARRIAGE,
            title="Marriage of Ram & Sita",
            date=datetime.date(1960, 5, 2),
            place="Kathmandu, Nepal",
            description="Traditional ceremony celebrated with extended relatives.",
        )
        Event.objects.create(
            family=family,
            person=rajesh,
            event_type=Event.EventType.EDUCATION,
            title="Graduation in Architecture",
            date=datetime.date(1987, 7, 20),
            place="Roorkee, India",
            description="Awarded distinction honors for heritage restoration research.",
        )
        Event.objects.create(
            family=family,
            person=aarav,
            event_type=Event.EventType.CAREER,
            title="Launch of Global Open Source Initiative",
            date=datetime.date(2021, 9, 1),
            place="Kathmandu",
            description="Founded community digital preservation lab.",
        )

        # 8. Create Stories
        s1 = Story.objects.create(
            family=family,
            author=user,
            title="The Grandfather's Journal: Journey Across the Himalayan Passes",
            content=(
                "# The Journey of 1958\n\n"
                "In the spring of 1958, Grandfather Ram Bahadur undertook a historic surveying trek "
                "through the high valleys of Langtang and Manang.\n\n"
                "Equipped with brass instruments, hand-drawn topographic parchment, and two pack mules, "
                "his party documented forgotten trails and natural water springs that continue to supply local villages today.\n\n"
                "> *'True heritage is not mere stone and dust; it is the enduring care we carry for the earth and those who come after.'*\n\n"
                "This collection of notes remains preserved in the family archives."
            ),
            status=Story.Status.PUBLISHED,
            published_at=datetime.datetime(2024, 1, 15, 10, 0, tzinfo=datetime.timezone.utc),
        )
        s1.associated_people.set([ram, rajesh])

        s2 = Story.objects.create(
            family=family,
            author=user,
            title="Our Traditional Courtyard: Memories of Sita Devi's Garden",
            content=(
                "# Morning Light in the Courtyard\n\n"
                "Grandmother Sita Devi believed that every brick in our ancestral house held a story. "
                "Her courtyard was famed throughout Patan for fragrant jasmine, night-blooming parijat, "
                "and shelves of medicinal herbs.\n\n"
                "Every Dashain festival, all four generations gathered beneath the walnut tree to receive blessings."
            ),
            status=Story.Status.PUBLISHED,
            published_at=datetime.datetime(2024, 2, 20, 14, 30, tzinfo=datetime.timezone.utc),
        )
        s2.associated_people.set([sita, priya, aarav])

        # 9. Create Notifications
        Notification.objects.create(
            user=user,
            family=family,
            notification_type="WELCOME",
            title="Welcome to Family Historical Tree",
            message="Your family tree 'Thapa & Shrestha Historical Lineage' has been initialized with 4 generations!",
            action_url=f"/family/{family.id}/tree",
            is_read=False,
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded 4 generations, events, stories, and relationships!"))
