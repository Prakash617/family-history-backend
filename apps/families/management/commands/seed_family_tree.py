from django.core.management.base import BaseCommand
from django.db import transaction
from apps.events.models import Event
from apps.families.models import Family, FamilyMembership
from apps.media.models import Media
from apps.members.models import Person
from apps.notifications.models import Notification
from apps.relationships.models import MarriagePartnership, Relationship
from apps.stories.models import Story
from apps.users.models import User

class Command(BaseCommand):
    help = "Clear current data and seed the authentic Thapa Parivar Vamshavali (थापा परिवार वंशावली)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Clearing existing family tree data...")

        # 1. Clean existing records
        Relationship.objects.all().delete()
        MarriagePartnership.objects.all().delete()
        Event.objects.all().delete()
        Story.objects.all().delete()
        Media.objects.all().delete()
        Person.objects.all().delete()
        FamilyMembership.objects.all().delete()
        Family.objects.all().delete()

        # 2. Ensure Demo User exists
        user, _ = User.objects.get_or_create(
            email="demo@familytree.local",
            defaults={
                "first_name": "थापा",
                "last_name": "परिवार",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.set_password("Demo1234!")
        user.first_name = "थापा"
        user.last_name = "परिवार"
        user.save()

        # 3. Create Family: थापा परिवार वंशावली
        family = Family.objects.create(
            name="थापा परिवार वंशावली",
            description="बाघ सिंह थापाबाट सुरु भएको थापा परिवारको पुर्ख्यौली वंशावली, सम्बन्ध र ऐतिहासिक अभिलेख।",
            owner=user,
            privacy=Family.Privacy.PUBLIC,
        )
        FamilyMembership.objects.create(
            family=family,
            user=user,
            role=FamilyMembership.Role.OWNER,
        )
        self.stdout.write(f"Family '{family.name}' created.")

        # Helper to create person
        def make_person(first, last="थापा", gender=Person.Gender.MALE, approx_year="", living=False, bio=""):
            return Person.objects.create(
                family=family,
                first_name=first,
                last_name=last,
                gender=gender,
                birth_year_approx=approx_year,
                is_living=living,
                biography=bio,
            )

        # Helper to link parent-child
        def link_child(parent, child, subtype="BIOLOGICAL"):
            Relationship.objects.create(
                family=family,
                person_a=parent,
                person_b=child,
                relationship_type=Relationship.Type.PARENT_CHILD,
                relationship_subtype=subtype,
            )

        # Helper to link spouses
        def link_spouses(p1, p2):
            MarriagePartnership.objects.create(
                family=family,
                partner_1=p1,
                partner_2=p2,
                partnership_type=MarriagePartnership.PartnershipType.MARRIAGE,
                end_reason=MarriagePartnership.EndReason.ONGOING if (p1.is_living or p2.is_living) else MarriagePartnership.EndReason.DEATH,
            )
            Relationship.objects.create(
                family=family,
                person_a=p1,
                person_b=p2,
                relationship_type=Relationship.Type.SPOUSE,
            )

        # ==========================================
        # GENERATION 1 (मूल पुर्खा / Root Ancestor)
        # ==========================================
        bagh_singh = make_person(
            first="बाघ सिंह",
            last="थापा",
            gender=Person.Gender.MALE,
            approx_year="पहिलो पुस्ता",
            living=False,
            bio="थापा परिवारको मूल पुर्खा।",
        )

        # ==========================================
        # GENERATION 2
        # ==========================================
        hasta_bahadur = make_person(
            first="हस्त बहादुर",
            last="थापा",
            gender=Person.Gender.MALE,
            approx_year="दोस्रो पुस्ता",
            living=False,
            bio="बाघ सिंह थापाका सुपुत्र।",
        )
        link_child(bagh_singh, hasta_bahadur)

        # ==========================================
        # GENERATION 3 (Children of Hasta Bahadur)
        # ==========================================
        nain_bahadur = make_person(first="नैन बहादुर", last="थापा", gender=Person.Gender.MALE, approx_year="तेस्रो पुस्ता")
        nani_bahadur = make_person(first="नानी बहादुर", last="थापा", gender=Person.Gender.MALE, approx_year="तेस्रो पुस्ता")
        dilli_thapa_g3 = make_person(first="डिल्ली", last="थापा", gender=Person.Gender.MALE, approx_year="तेस्रो पुस्ता")
        kanchha_thapa = make_person(first="कान्छ", last="थापा", gender=Person.Gender.MALE, approx_year="तेस्रो पुस्ता")

        for child in [nain_bahadur, nani_bahadur, dilli_thapa_g3, kanchha_thapa]:
            link_child(hasta_bahadur, child)

        # Spouse of Nani Bahadur:
        man_kumari = make_person(
            first="मानकुमारी",
            last="थापा",
            gender=Person.Gender.FEMALE,
            approx_year="तेस्रो पुस्ता",
            living=False,
        )
        link_spouses(nani_bahadur, man_kumari)

        # ==========================================
        # GENERATION 4 (Children of Nani Bahadur & Man Kumari)
        # ==========================================
        shiva_thapa = make_person(first="शिव", last="थापा", gender=Person.Gender.MALE, approx_year="चौथो पुस्ता")
        som_bahadur = make_person(first="सोम बहादुर", last="थापा", gender=Person.Gender.MALE, approx_year="चौथो पुस्ता")
        dilli_thapa_g4 = make_person(first="डिल्ली", last="थापा", gender=Person.Gender.MALE, approx_year="चौथो पुस्ता")
        krishna_thapa = make_person(first="कृष्ण", last="थापा", gender=Person.Gender.MALE, approx_year="चौथो पुस्ता")
        bishnu_thapa = make_person(first="बिष्णु", last="थापा", gender=Person.Gender.MALE, approx_year="चौथो पुस्ता")
        shantaram_thapa = make_person(first="शान्ताराम", last="थापा", gender=Person.Gender.MALE, approx_year="चौथो पुस्ता")

        for child in [shiva_thapa, som_bahadur, dilli_thapa_g4, krishna_thapa, bishnu_thapa, shantaram_thapa]:
            link_child(nani_bahadur, child)
            link_child(man_kumari, child)

        # Spouse of Som Bahadur:
        khum_kumari = make_person(
            first="खुम कुमारी",
            last="थापा",
            gender=Person.Gender.FEMALE,
            approx_year="चौथो पुस्ता",
            living=False,
        )
        link_spouses(som_bahadur, khum_kumari)

        # ==========================================
        # GENERATION 5 (Children of Som Bahadur & Khum Kumari)
        # ==========================================
        indra_bahadur = make_person(
            first="इन्द्र बहादुर",
            last="थापा",
            gender=Person.Gender.MALE,
            approx_year="पाँचौँ पुस्ता",
            living=True,
        )
        kshetra_bahadur = make_person(
            first="क्षत्र बहादुर",
            last="थापा",
            gender=Person.Gender.MALE,
            approx_year="पाँचौँ पुस्ता",
            living=True,
        )

        for child in [indra_bahadur, kshetra_bahadur]:
            link_child(som_bahadur, child)
            link_child(khum_kumari, child)

        # Spouses of Generation 5:
        radhika = make_person(first="राधिका", last="थापा", gender=Person.Gender.FEMALE, approx_year="पाँचौँ पुस्ता", living=True)
        link_spouses(indra_bahadur, radhika)

        saraswati = make_person(first="सरस्वती", last="थापा", gender=Person.Gender.FEMALE, approx_year="पाँचौँ पुस्ता", living=True)
        link_spouses(kshetra_bahadur, saraswati)

        # ==========================================
        # GENERATION 6
        # ==========================================
        # Children of Indra Bahadur & Radhika:
        rajashi = make_person(first="राजषी", last="थापा", gender=Person.Gender.FEMALE, approx_year="छैटौँ पुस्ता", living=True)
        ujjwal = make_person(first="उज्ज्वल", last="थापा", gender=Person.Gender.MALE, approx_year="छैटौँ पुस्ता", living=True)
        uday = make_person(first="उदय", last="थापा", gender=Person.Gender.MALE, approx_year="छैटौँ पुस्ता", living=True)

        for child in [rajashi, ujjwal, uday]:
            link_child(indra_bahadur, child)
            link_child(radhika, child)

        # Children of Kshetra Bahadur & Saraswati:
        nil_bahadur = make_person(first="निल बहादुर", last="थापा", gender=Person.Gender.MALE, approx_year="छैटौँ पुस्ता", living=True)
        nilisa = make_person(first="निलिसा", last="थापा", gender=Person.Gender.FEMALE, approx_year="छैटौँ पुस्ता", living=True)

        for child in [nil_bahadur, nilisa]:
            link_child(kshetra_bahadur, child)
            link_child(saraswati, child)

        # ==========================================
        # STORIES & MEMORIES (इतिहास तथा स्मृतिहरू)
        # ==========================================
        Story.objects.create(
            family=family,
            author=user,
            title="थापा परिवारको ऐतिहासिक पुर्ख्यौली तथा उद्गम",
            content=(
                "# थापा परिवार वंशावली इतिहास\n\n"
                "यो वंशावली आदरणीय मूल पुर्खा **बाघ सिंह थापा**बाट प्रारम्भ भई छैटौँ पुस्तासम्म फैलिएको ऐतिहासिक पारिवारिक अभिलेख हो।\n\n"
                "दोस्रो पुस्ताका **हस्त बहादुर थापा**का चार सुपुत्रहरू: नैन बहादुर, नानी बहादुर, डिल्ली र कान्छ थापामध्ये "
                "नानी बहादुर थापा तथा मानकुमारी थापाको शाखाबाट सोम बहादुर थापा हुँदै आजको नयाँ पुस्तासम्म वंशावली विस्तार भएको छ।"
            ),
            status=Story.Status.PUBLISHED,
        )

        # ==========================================
        # NOTIFICATION
        # ==========================================
        Notification.objects.create(
            user=user,
            family=family,
            notification_type="VAMSHAVALI_LOADED",
            title="थापा परिवार वंशावली सफलतापूर्वक प्रविष्ट भयो",
            message="तपाईंको थापा परिवार वंशावली (६ पुस्ता, २३ सदस्यहरू) सफलतापूर्वक लोड भएको छ।",
            action_url=f"/family/{family.id}/tree",
            is_read=False,
        )

        from django.core.management import call_command
        call_command("generate_sample_avatars")

        self.stdout.write(
            self.style.SUCCESS(
                "सफलतापूर्वक पुरानो डाटा हटाई 'थापा परिवार वंशावली' का ६ पुस्ता (२३ सदस्यहरू) प्रविष्ट गरियो!"
            )
        )
