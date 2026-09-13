import os
import random
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

from apps.users.models import User
from apps.families.models import Family, FamilyMembership
from apps.members.models import Person
from apps.relationships.models import Relationship, MarriagePartnership
from apps.events.models import Event
from apps.stories.models import Story
from apps.media.models import Media
from apps.families.management.commands.generate_sample_avatars import generate_avatar

def get_font(size=20, bold=False):
    font_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_vintage_photo(title_text, subtitle_text, output_path, theme="sepia"):
    width, height = 800, 560
    img = Image.new("RGB", (width, height), color=(245, 240, 230))
    draw = ImageDraw.Draw(img)

    if theme == "sepia":
        base_color = (210, 185, 150)
        grad_color = (165, 130, 95)
        border_col = (90, 60, 35)
    elif theme == "temple":
        base_color = (230, 190, 140)
        grad_color = (180, 80, 50)
        border_col = (130, 30, 20)
    else: # blue/slate certificate/doc
        base_color = (220, 230, 240)
        grad_color = (140, 160, 190)
        border_col = (30, 50, 80)

    # Gradient background
    for y in range(height):
        ratio = y / height
        r = int(base_color[0] * (1 - ratio) + grad_color[0] * ratio)
        g = int(base_color[1] * (1 - ratio) + grad_color[1] * ratio)
        b = int(base_color[2] * (1 - ratio) + grad_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Inner ornate frame
    draw.rectangle([25, 25, width - 25, height - 25], outline=border_col, width=4)
    draw.rectangle([35, 35, width - 35, height - 35], outline=border_col, width=1)

    # Decorative corner diamonds
    for cx, cy in [(25, 25), (width - 25, 25), (25, height - 25), (width - 25, height - 25)]:
        draw.polygon([(cx, cy - 10), (cx + 10, cy), (cx, cy + 10), (cx - 10, cy)], fill=border_col)

    # Draw scenic / illustration silhouette
    if theme == "sepia":
        # Draw traditional hill & pagoda house silhouette
        draw.polygon([(100, 380), (250, 290), (400, 380)], fill=(70, 50, 35))
        draw.polygon([(400, 390), (550, 310), (700, 390)], fill=(85, 60, 40))
        # Mountain peaks background
        draw.polygon([(50, 290), (200, 180), (350, 290)], fill=(120, 95, 75))
        draw.polygon([(300, 290), (450, 160), (600, 290)], fill=(130, 105, 85))
        draw.polygon([(520, 290), (660, 190), (760, 290)], fill=(110, 85, 65))
        # Sun/moon
        draw.ellipse([640, 70, 710, 140], fill=(245, 230, 190), outline=border_col, width=2)
    elif theme == "temple":
        # Temple pagoda silhouette
        cx = width // 2
        draw.polygon([(cx - 180, 380), (cx, 280), (cx + 180, 380)], fill=(120, 35, 25))
        draw.polygon([(cx - 130, 290), (cx, 210), (cx + 130, 290)], fill=(140, 45, 30))
        draw.polygon([(cx - 80, 220), (cx, 160), (cx + 80, 220)], fill=(160, 55, 35))
        draw.polygon([(cx - 15, 165), (cx, 120), (cx + 15, 165)], fill=(212, 175, 55)) # Gajur
        draw.rectangle([cx - 90, 380, cx + 90, 430], fill=(70, 20, 15))
    else: # document / parchment
        # Certificate lines and emblem
        cx = width // 2
        draw.ellipse([cx - 45, 100, cx + 45, 190], fill=(185, 28, 28), outline=(212, 175, 55), width=3)
        draw.polygon([(cx - 20, 185), (cx - 35, 235), (cx, 210)], fill=(185, 28, 28))
        draw.polygon([(cx + 20, 185), (cx + 35, 235), (cx, 210)], fill=(185, 28, 28))
        for line_y in range(250, 400, 25):
            draw.line([(120, line_y), (width - 120, line_y)], fill=(100, 120, 150), width=1)

    # Bottom caption plaque
    plaque_y = height - 110
    draw.rectangle([60, plaque_y, width - 60, height - 45], fill=(255, 253, 245), outline=border_col, width=2)

    font_title = get_font(22, bold=True)
    font_sub = get_font(15, bold=False)

    draw.text((width // 2, plaque_y + 14), title_text, fill=(30, 25, 20), font=font_title, anchor="mt")
    draw.text((width // 2, plaque_y + 40), subtitle_text, fill=(80, 70, 60), font=font_sub, anchor="mt")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=92)

class Command(BaseCommand):
    help = "Seeds comprehensive, rich demo data across Timeline Events, Historical Stories, and Media Archives for all family trees"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting demo data seeding..."))

        demo_user = User.objects.filter(email="demo@familytree.local").first()
        if not demo_user:
            demo_user = User.objects.create_user(
                email="demo@familytree.local",
                password="DemoUser1234!",
                first_name="Prakash",
                last_name="Thapa",
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f"Created demo user: {demo_user.email}"))

        # =========================================================================
        # 1. PRIMARY FAMILY: थापा परिवार वंशावली
        # =========================================================================
        thapa_family = Family.objects.filter(name__icontains="थापा परिवार").first()
        if not thapa_family:
            thapa_family = Family.objects.create(
                name="थापा परिवार वंशावली",
                description="दोलखा, भिमेश्वरबाट उद्भव भई हाल काठमाडौं उपत्यका तथा विश्वभर फैलिएको ऐतिहासिक थापा कुल वंशावली।",
                owner=demo_user,
                privacy="PRIVATE"
            )

        FamilyMembership.objects.get_or_create(family=thapa_family, user=demo_user, defaults={"role": "OWNER"})

        # Enrich member details with birth dates and biographies if empty
        bagh_singh = Person.objects.filter(family=thapa_family, first_name__icontains="बाघ").first()
        if bagh_singh:
            bagh_singh.birth_date = datetime.date(1915, 4, 12)
            bagh_singh.death_date = datetime.date(1988, 11, 25)
            bagh_singh.is_living = False
            bagh_singh.birth_place = "दोलखा, भिमेश्वर"
            bagh_singh.occupation = "गाउँका मुखिया / समाजसेवी"
            bagh_singh.biography = "दोलखा भिमेश्वरका कुलशिरोमणि, समाजसेवी तथा न्यायप्रेमी व्यक्तित्व। उहाँले स्थानीय समाजमा शिक्षा र मेलमिलापका लागि अतुलनीय योगदान पुर्‍याउनुभयो।"
            bagh_singh.save()

        hasta_bahadur = Person.objects.filter(family=thapa_family, first_name__icontains="हस्त").first()
        if hasta_bahadur:
            hasta_bahadur.birth_date = datetime.date(1938, 8, 10)
            hasta_bahadur.death_date = datetime.date(2012, 3, 14)
            hasta_bahadur.is_living = False
            hasta_bahadur.birth_place = "दोलखा"
            hasta_bahadur.occupation = "शाही नेपाली सेना (सुवेदार)"
            hasta_bahadur.biography = "सैन्य सेवामा लामो समय राष्ट्र सेवा गर्नुभएको इमानदार तथा अनुशासित योद्धा।"
            hasta_bahadur.save()

        som_bahadur = Person.objects.filter(family=thapa_family, first_name__icontains="सोम").first()
        if som_bahadur:
            som_bahadur.birth_date = datetime.date(1942, 6, 18)
            som_bahadur.is_living = True
            som_bahadur.birth_place = "दोलखा"
            som_bahadur.occupation = "संस्कृत शिक्षक / पण्डित"
            som_bahadur.biography = "संस्कृत तथा सनातन संस्कृतिका अध्येता, कुल परम्परा तथा देवाली पूजाका प्रमुख संरक्षक।"
            som_bahadur.save()

        prakash_thapa = Person.objects.filter(family=thapa_family, first_name__icontains="Prakash").first() or Person.objects.filter(family=thapa_family, first_name__icontains="प्रकाश").first()
        if prakash_thapa:
            prakash_thapa.birth_date = datetime.date(1968, 9, 21)
            prakash_thapa.is_living = True
            prakash_thapa.birth_place = "दोलखा"
            prakash_thapa.occupation = "सिभिल इन्जिनियर / प्राध्यापक"
            prakash_thapa.biography = "पुल्चोक क्याम्पसबाट इन्जिनियरिङ स्नातक गरी नेपालका ठूला जलविद्युत तथा पूर्वाधार परियोजनाहरूमा नेतृत्वदायी भूमिका निर्वाह।"
            prakash_thapa.save()

        ujwal_thapa = Person.objects.filter(family=thapa_family, first_name__icontains="उज्ज्वल").first()
        if ujwal_thapa:
            ujwal_thapa.birth_date = datetime.date(1995, 3, 15)
            ujwal_thapa.is_living = True
            ujwal_thapa.birth_place = "काठमाडौं"
            ujwal_thapa.occupation = "सफ्टवेयर इन्जिनियर"
            ujwal_thapa.biography = "आधुनिक प्रविधि तथा कम्प्युटर विज्ञानमा स्नातक, वंशावली डिजिटलाइजेसन परियोजनाका अभियन्ता।"
            ujwal_thapa.save()

        # Seed Events for थापा परिवार
        thapa_events = [
            {
                "event_type": Event.EventType.BIRTH,
                "title": "बाघ सिंह थापाको जन्म (दोलखा, भिमेश्वर)",
                "date": datetime.date(1915, 4, 12),
                "place": "दोलखा, भिमेश्वर",
                "description": "दोलखाको ऐतिहासिक भिमेश्वर गाउँमा कुल शिरोमणि बाघ सिंह थापाको जन्म भएको थियो।",
                "person": bagh_singh,
            },
            {
                "event_type": Event.EventType.MARRIAGE,
                "title": "बाघ सिंह थापा तथा मानकुमारीको शुभविवाह",
                "date": datetime.date(1935, 2, 18),
                "place": "दोलखा",
                "description": "वैदिक विधिपूर्वक सम्पन्न भएको ऐतिहासिक विवाह जसले कुललाई निरन्तरता दियो।",
                "person": bagh_singh,
            },
            {
                "event_type": Event.EventType.BIRTH,
                "title": "ज्येष्ठ सुपुत्र हस्त बहादुर थापाको जन्म",
                "date": datetime.date(1938, 8, 10),
                "place": "दोलखा",
                "description": "दोश्रो पुस्ताका अगुवा हस्त बहादुर थापाको जन्म।",
                "person": hasta_bahadur,
            },
            {
                "event_type": Event.EventType.MILITARY,
                "title": "हस्त बहादुर थापाको शाही नेपाली सेनामा प्रवेश",
                "date": datetime.date(1962, 11, 15),
                "place": "काठमाडौं छाउनी",
                "description": "राष्ट्र सेवाको उद्देश्यसहित शाही नेपाली सेनामा भर्ना हुनुभएको ऐतिहासिक क्षण।",
                "person": hasta_bahadur,
            },
            {
                "event_type": Event.EventType.MARRIAGE,
                "title": "पण्डित सोम बहादुर थापाको शुभविवाह",
                "date": datetime.date(1968, 5, 20),
                "place": "सिन्धुपाल्चोक",
                "description": "धार्मिक तथा सामाजिक उत्सवका रूपमा सम्पन्न भव्य वैवाहिक समारोह।",
                "person": som_bahadur,
            },
            {
                "event_type": Event.EventType.MIGRATION,
                "title": "दोलखाबाट काठमाडौं उपत्यकामा बसाइँसराइ (Migration)",
                "date": datetime.date(1975, 3, 10),
                "place": "काठमाडौं, बानेश्वर",
                "description": "परिवारका सन्तानहरूको उच्च शिक्षा तथा रोजगारीका लागि दोलखाबाट काठमाडौं बसाइँ सरेको ऐतिहासिक घटना।",
                "person": hasta_bahadur,
            },
            {
                "event_type": Event.EventType.CAREER,
                "title": "सरकारी निजामती सेवामा अधिकृत स्तरमा नियुक्ति",
                "date": datetime.date(1985, 9, 1),
                "place": "सिंहदरबार, काठमाडौं",
                "description": "लोकसेवा आयोग उत्तीर्ण गरी देश सेवामा समर्पित हुनुभएको गौरवमय अवसर।",
                "person": None,
            },
            {
                "event_type": Event.EventType.EDUCATION,
                "title": "प्रकाश थापाद्वारा प्रवेशिका परीक्षा (SLC) विशिष्ट श्रेणीमा उत्तीर्ण",
                "date": datetime.date(1990, 7, 14),
                "place": "काठमाडौं",
                "description": "परिवारमा पहिलो पटक डिस्टिङ्कसन सहित एस.एल.सी. उत्तीर्ण गरी गौरव बढाएको अवसर।",
                "person": prakash_thapa,
            },
            {
                "event_type": Event.EventType.OTHER,
                "title": "ऐतिहासिक कुल मन्दिर पुनर्निर्माण तथा प्राण प्रतिष्ठा",
                "date": datetime.date(2010, 4, 25),
                "place": "दोलखा पैतृक थलो",
                "description": "सम्पूर्ण थापा खलक एकै स्थानमा भेला भई कुल देवताको भव्य मन्दिर पुनर्निर्माण सम्पन्न गरियो।",
                "person": None,
            },
            {
                "event_type": Event.EventType.OTHER,
                "title": "थापा वंशावली प्रथम डिजिटल महासम्मेलन",
                "date": datetime.date(2020, 11, 20),
                "place": "काठमाडौं / भर्चुअल",
                "description": "देशविदेशमा रहेका सम्पूर्ण थापा दाजुभाइ तथा दिदीबहिनीहरू बीच पहिलो भर्चुअल वंशावली सम्मेलन सम्पन्न।",
                "person": ujwal_thapa,
            },
        ]

        for ev in thapa_events:
            Event.objects.update_or_create(
                family=thapa_family,
                title=ev["title"],
                defaults={
                    "event_type": ev["event_type"],
                    "date": ev["date"],
                    "place": ev["place"],
                    "description": ev["description"],
                    "person": ev["person"],
                }
            )
        self.stdout.write(self.style.SUCCESS(f"Populated {len(thapa_events)} Events for थापा परिवार वंशावली"))

        # Seed Stories for थापा परिवार
        story_cover_1 = os.path.join(settings.MEDIA_ROOT, "story_covers", "story_thapa_origins.jpg")
        story_cover_2 = os.path.join(settings.MEDIA_ROOT, "story_covers", "story_thapa_migration.jpg")
        story_cover_3 = os.path.join(settings.MEDIA_ROOT, "story_covers", "story_thapa_kulpuja.jpg")
        story_cover_4 = os.path.join(settings.MEDIA_ROOT, "story_covers", "story_thapa_modern.jpg")

        draw_vintage_photo("दोलखाको पैतृक थलो", "बाघ सिंह थापा र कुल उद्भव", story_cover_1, theme="sepia")
        draw_vintage_photo("वि.सं. २०३१ को काठमाडौं यात्रा", "पैदल यात्रा र बसाइँसराइको स्मृति", story_cover_2, theme="sepia")
        draw_vintage_photo("कुल मन्दिर र देवाली अनुष्ठान", "दोलखा भिमेश्वर कुल पूजा", story_cover_3, theme="temple")
        draw_vintage_photo("नयाँ पुस्ताको विश्वव्यापी फैलावट", "डिजिटल युग र अग्रगमन", story_cover_4, theme="doc")

        thapa_stories = [
            {
                "title": "दोलखाको पैतृक थलो र बाघ सिंह थापाको योगदान",
                "cover_image": "story_covers/story_thapa_origins.jpg",
                "content": """# दोलखाको पैतृक थलो र बाघ सिंह थापाको ऐतिहासिक योगदान

हाम्रो कुलको गौरवमय इतिहास दोलखाको भिमेश्वर डाँडाबाट सुरु हुन्छ। वि.सं. १९७० को दशकमा हाम्रा जिजुहजुरबुबा **बाघ सिंह थापा**ले यस भेगमा समाज सुधार, शिक्षा र आपसी भाइचाराको जग बसाल्नुभएको थियो।

### समाज सेवा र मुखियाको जिम्मेवारी
त्यस समयमा सरकारी प्रशासन दुर्गम ठाउँहरूमा न्यून थियो। बाघ सिंह थापाले स्थानीय विवादहरूको शान्तिपूर्ण समाधान, गरिब किसानहरूलाई अन्न-बीउको सहयोग, र धार्मिक पर्वहरूमा सामूहिक सहकार्यको परम्परा स्थापना गर्नुभयो।

> "सत्य, निष्ठा र कुलको मर्यादा नै जीवनको सबैभन्दा ठूलो सम्पत्ति हो।" — बाघ सिंह थापा

### आजको सान्दर्भिकता
आज हाम्रो परिवार दोलखाबाट देशविदेशका विभिन्न शहरमा फैलिए तापनि उहाँले सिकाउनुभएको सरलता, अनुशासन र परोपकारको भावना नै हाम्रो वंशको मूल पहिचान बनेर रहेको छ।""",
                "associated": [bagh_singh, hasta_bahadur],
            },
            {
                "title": "वि.सं. २०३१ को काठमाडौं यात्रा र बसाइँसराइको सम्झना",
                "cover_image": "story_covers/story_thapa_migration.jpg",
                "content": """# वि.सं. २०३१ को काठमाडौं यात्रा र बसाइँसराइको सम्झना

दोलखाबाट काठमाडौं उपत्यकामा बसाइँ सर्ने निर्णय हाम्रो परिवारको इतिहासमा एक युगीन मोड थियो। त्यस बेला अरनिको राजमार्ग बनेको भर्खरै मात्र थियो र यातायातका साधनहरू अत्यन्त सीमित थिए।

### पैदल यात्रा र भारी बोकेर गरिएको यात्रा
परिवारका अग्रजहरू, साना बालबच्चा र आवश्यक भाँडाकुँडा, काठका बाकस र ऐतिहासिक कागजातहरू बोकेर ३ दिनको पैदल यात्रा गरी बानेश्वर आइपुगेको सम्झना अझै ताजा छ।

* **पहिलो बास:** चरिकोटबाट तामाकोशी किनार
* **दोश्रो बास:** सिन्धुपाल्चोकको खाडीचौर
* **तेस्रो दिन:** धुलिखेल हुँदै काठमाडौं उपत्यका प्रवेश

काठमाडौंमा आएपछि सुरुका दिनहरू सहज थिएनन्। तर सबै दाजुभाइहरूको कडा परिश्रम, बचत गर्ने बानी र शिक्षाप्रतिको लगावका कारण परिवारले छोटो समयमै आफ्नै घर निर्माण गर्न सफल भयो।""",
                "associated": [hasta_bahadur, som_bahadur],
            },
            {
                "title": "कुलदेवताको पूजा र देवाली परम्परा",
                "cover_image": "story_covers/story_thapa_kulpuja.jpg",
                "content": """# कुलदेवताको पूजा र देवाली परम्परा

हाम्रो थापा खलकको कुल परम्परा अनुसार प्रत्येक १२ वर्षमा महापूजा तथा वार्षिक रूपमा देवाली पूजा गर्ने परम्परा पुस्तौंदेखि निरन्तर चलिआएको छ।

### देवाली पूजाको विधि
१. **शुद्धि र व्रत:** पूजाको ३ दिन अगाडिदेखि चोखो खानेकुरा खाने र ब्रत बस्ने परम्परा छ।
२. **ध्वजा स्थापना:** कुल थानमा रातो र सेतो ध्वजा फहराइन्छ।
३. **प्रसाद वितरण र खलक भेला:** देशविदेशबाट आएका सम्पूर्ण दाजुभाइहरू एउटै आँगनमा बसेर कुलको प्रसाद ग्रहण गर्दछन्।

यस अनुष्ठानले हाम्रो वंशका नयाँ पुस्तालाई आफ्ना दाजुभाइ, दिदीबहिनी तथा पुर्खाको इतिहाससँग प्रत्यक्ष जोड्ने अतुलनीय सेतुको काम गरिरहेको छ।""",
                "associated": [som_bahadur],
            },
            {
                "title": "नयाँ पुस्ताको विश्वव्यापी फैलावट र आधुनिक उपलब्धि",
                "cover_image": "story_covers/story_thapa_modern.jpg",
                "content": """# नयाँ पुस्ताको विश्वव्यापी फैलावट र आधुनिक उपलब्धि

वि.सं. २०५० पछि जन्मेको नयाँ पुस्ताले प्रविधि, विज्ञान, चिकित्सा तथा व्यवस्थापन क्षेत्रमा राष्ट्रिय तथा अन्तर्राष्ट्रिय स्तरमा उल्लेखनीय सफलता हासिल गरेको छ।

### विविधता र विश्वव्यापी उपस्थिति
आज हाम्रो थापा परिवारका सदस्यहरू काठमाडौंका अतिरिक्त अष्ट्रेलिया, अमेरिका, क्यानडा, बेलायत र युरोपका प्रमुख सहरहरूमा पेशागत रूपमा कार्यरत हुनुहुन्छ।

* **इन्जिनियरिङ र आईटी:** देशको पूर्वाधार निर्माण र विश्वव्यापी टेक कम्पनीहरूमा सफ्टवेयर विकास।
* **चिकित्सा सेवा:** विशेषज्ञ डाक्टरका रूपमा हजारौं बिरामीहरूको जीवन रक्षा।
* **शिक्षा तथा अनुसन्धान:** विश्वविद्यालयहरूमा प्राध्यापन र अनुसन्धान।

भौगोलिक दूरी जतिसुकै टाढा भए पनि हाम्रो डिजिटल वंशावली पोर्टल मार्फत सम्पूर्ण परिवार एउटै मालामा गाँसिएर रहन सफल भएको छ।""",
                "associated": [prakash_thapa, ujwal_thapa],
            },
        ]

        for st in thapa_stories:
            story_obj, _ = Story.objects.update_or_create(
                family=thapa_family,
                title=st["title"],
                defaults={
                    "author": demo_user,
                    "content": st["content"],
                    "cover_image": st["cover_image"],
                    "status": Story.Status.PUBLISHED,
                    "published_at": datetime.datetime.now(),
                }
            )
            associated_valid = [p for p in st["associated"] if p]
            if associated_valid:
                story_obj.associated_people.set(associated_valid)
        self.stdout.write(self.style.SUCCESS(f"Populated {len(thapa_stories)} Stories for थापा परिवार वंशावली"))

        # Seed Media for थापा परिवार
        media_items_thapa = [
            {
                "title": "बाघ सिंह थापाको ऐतिहासिक तस्विर (वि.सं. २०२५)",
                "description": "दोलखा भिमेश्वर पैतृक निवास अगाडि खिचिएको दुर्लभ ऐतिहासिक तस्विर।",
                "media_type": Media.MediaType.PHOTO,
                "person": bagh_singh,
                "captured_date": datetime.date(1968, 10, 15),
                "theme": "sepia",
                "filename": "media_bagh_singh_portrait.jpg",
                "sub": "दोलखा भिमेश्वर — वि.सं. २०२५",
            },
            {
                "title": "दोलखाको पुर्ख्यौली थापा निवास (वि.सं. २०३०)",
                "description": "काठ र ढुङ्गाले बनेको परम्परागत नेपाली तीनतले पैतृक घर।",
                "media_type": Media.MediaType.PHOTO,
                "person": None,
                "captured_date": datetime.date(1973, 5, 20),
                "theme": "sepia",
                "filename": "media_ancestral_house_dolakha.jpg",
                "sub": "पुर्ख्यौली निवास — दोलखा",
            },
            {
                "title": "वि.सं. २०२८ को पैतृक जग्गाधनी प्रमाण पुर्जा (Land Deed)",
                "description": "श्री ५ को सरकार, भूमिसुधार मन्त्रालयद्वारा जारी गरिएको ऐतिहासिक लालपुर्जा।",
                "media_type": Media.MediaType.DOCUMENT,
                "person": bagh_singh,
                "captured_date": datetime.date(1971, 2, 10),
                "theme": "doc",
                "filename": "media_historical_lalpurja_1971.jpg",
                "sub": "भूमि प्रशासन — ऐतिहासिक लालपुर्जा",
            },
            {
                "title": "हस्त बहादुर थापाको सैन्य पदक तथा कदरपत्र (वि.सं. २०४०)",
                "description": "शाही नेपाली सेनामा उत्कृष्ट सेवाबापत प्रदान गरिएको सम्मानपत्र तथा कदरपत्र।",
                "media_type": Media.MediaType.CERTIFICATE,
                "person": hasta_bahadur,
                "captured_date": datetime.date(1983, 12, 1),
                "theme": "doc",
                "filename": "media_hasta_military_certificate.jpg",
                "sub": "शाही नेपाली सेना — सेवा पदक",
            },
            {
                "title": "प्रकाश थापाको एस.एल.सी. चारित्रिक प्रमाणपत्र (वि.सं. २०४७)",
                "description": "काठमाडौं परीक्षा नियन्त्रण कार्यालयबाट प्राप्त बोर्ड प्रमाणपत्र।",
                "media_type": Media.MediaType.CERTIFICATE,
                "person": prakash_thapa,
                "captured_date": datetime.date(1990, 8, 5),
                "theme": "doc",
                "filename": "media_prakash_slc_certificate.jpg",
                "sub": "परीक्षा नियन्त्रण कार्यालय — २०४७",
            },
            {
                "title": "वि.सं. २०५० को संयुक्त परिवार देवाली भेला",
                "description": "दोलखामा आयोजित कुल पूजा तथा देवाली उत्सवमा सम्पूर्ण खलकको संयुक्त समूह तस्विर।",
                "media_type": Media.MediaType.PHOTO,
                "person": None,
                "captured_date": datetime.date(1993, 4, 18),
                "theme": "temple",
                "filename": "media_thapa_dewali_gathering_1993.jpg",
                "sub": "देवाली महापूजा — वि.सं. २०५०",
            },
            {
                "title": "काठमाडौं बसाइँसराइको ऐतिहासिक सिफारिस पत्र (वि.सं. २०३२)",
                "description": "गाउँ पञ्चायतबाट काठमाडौं स्थानान्तरणका लागि जारी गरिएको आधिकारिक पत्र।",
                "media_type": Media.MediaType.DOCUMENT,
                "person": hasta_bahadur,
                "captured_date": datetime.date(1975, 4, 1),
                "theme": "doc",
                "filename": "media_migration_letter_1975.jpg",
                "sub": "गाउँ पञ्चायत कार्यालय — २०३२",
            },
            {
                "title": "वि.सं. २०७८ को कुल मन्दिर पुनर्निर्माण उत्सव",
                "description": "दोलखा कुल मन्दिरको जीर्णोद्धार सम्पन्न भएपछि गरिएको सामूहिक पूजा र आरती।",
                "media_type": Media.MediaType.PHOTO,
                "person": ujwal_thapa,
                "captured_date": datetime.date(2021, 10, 12),
                "theme": "temple",
                "filename": "media_mandir_celebration_2021.jpg",
                "sub": "कुल मन्दिर जीर्णोद्धार — २०७८",
            },
        ]

        for m in media_items_thapa:
            file_rel = os.path.join("family_media", m["filename"])
            abs_path = os.path.join(settings.MEDIA_ROOT, file_rel)
            draw_vintage_photo(m["title"], m["sub"], abs_path, theme=m["theme"])
            Media.objects.update_or_create(
                family=thapa_family,
                title=m["title"],
                defaults={
                    "uploader": demo_user,
                    "description": m["description"],
                    "file": file_rel,
                    "media_type": m["media_type"],
                    "person": m["person"],
                    "captured_date": m["captured_date"],
                    "visibility": Media.Visibility.FAMILY_ONLY,
                    "file_size": os.path.getsize(abs_path),
                    "mime_type": "image/jpeg",
                }
            )
        self.stdout.write(self.style.SUCCESS(f"Populated {len(media_items_thapa)} Media Archives for थापा परिवार"))

        # =========================================================================
        # 2. SECOND FAMILY: naya thapa (Branch Lineage)
        # =========================================================================
        naya_family = Family.objects.filter(id="820c043c-f89a-4813-8509-42babe367b1c").first() or Family.objects.filter(name__icontains="naya").first()
        if naya_family:
            FamilyMembership.objects.get_or_create(family=naya_family, user=demo_user, defaults={"role": "OWNER"})
            naya_members = list(naya_family.members.all())
            m1 = naya_members[0] if len(naya_members) > 0 else None
            m2 = naya_members[1] if len(naya_members) > 1 else None

            naya_events = [
                {
                    "event_type": Event.EventType.BIRTH,
                    "title": "शाखा कुल संस्थापकको जन्म (पोखरा)",
                    "date": datetime.date(1955, 3, 12),
                    "place": "पोखरा, कास्की",
                    "description": "कास्की शाखा कुलका अग्रजको जन्म।",
                    "person": m1,
                },
                {
                    "event_type": Event.EventType.MARRIAGE,
                    "title": "पोखरामा वैवाहिक बन्धन",
                    "date": datetime.date(1978, 6, 22),
                    "place": "पोखरा",
                    "description": "स्थानीय रीतिरिवाज अनुसार सम्पन्न पवित्र विवाह।",
                    "person": m1,
                },
                {
                    "event_type": Event.EventType.CAREER,
                    "title": "व्यवसाय विस्तार तथा नयाँ प्रतिष्ठान",
                    "date": datetime.date(1995, 1, 10),
                    "place": "काठमाडौं",
                    "description": "पर्यटन तथा होटल व्यवसायमा नयाँ आयामको थालनी।",
                    "person": m2,
                },
            ]
            for ev in naya_events:
                Event.objects.update_or_create(
                    family=naya_family,
                    title=ev["title"],
                    defaults={
                        "event_type": ev["event_type"],
                        "date": ev["date"],
                        "place": ev["place"],
                        "description": ev["description"],
                        "person": ev["person"],
                    }
                )

            # Story for naya thapa
            s_cover_naya = os.path.join(settings.MEDIA_ROOT, "story_covers", "story_naya_pokhara.jpg")
            draw_vintage_photo("पोखरा शाखाको उद्भव", "कास्की तथा पोखराको इतिहास", s_cover_naya, theme="sepia")
            Story.objects.update_or_create(
                family=naya_family,
                title="कास्की पोखरा शाखाको प्रारम्भिक यात्रा",
                defaults={
                    "author": demo_user,
                    "content": """# कास्की पोखरा शाखाको प्रारम्भिक यात्रा

हाम्रो यस शाखा कुलले वि.सं. २०३० को दशकमा पोखरा उपत्यकामा आफ्नो व्यवसाय र बसोबास विस्तार गरेको हो। 

फेवातालको किनार र अन्नपूर्ण हिमशृङ्खलाको काखमा बसेर अग्रजहरूले पर्यटन र व्यापारमा पुर्‍याउनुभएको योगदान अनुकरणीय छ। आउने पुस्ताले पनि यस एकता र कर्मशीलतालाई कायम राख्नेछन्।""",
                    "cover_image": "story_covers/story_naya_pokhara.jpg",
                    "status": Story.Status.PUBLISHED,
                    "published_at": datetime.datetime.now(),
                }
            )

            # Media for naya thapa
            naya_m_path = os.path.join(settings.MEDIA_ROOT, "family_media", "media_naya_pokhara_vintage.jpg")
            draw_vintage_photo("पोखरा पैतृक घर (वि.सं. २०४०)", "कास्की — वि.सं. २०४०", naya_m_path, theme="sepia")
            Media.objects.update_or_create(
                family=naya_family,
                title="पोखरा पैतृक घर (वि.सं. २०४०)",
                defaults={
                    "uploader": demo_user,
                    "description": "पोखरा शाखा कुलको पुरानो निवास।",
                    "file": "family_media/media_naya_pokhara_vintage.jpg",
                    "media_type": Media.MediaType.PHOTO,
                    "person": m1,
                    "captured_date": datetime.date(1983, 7, 10),
                    "visibility": Media.Visibility.FAMILY_ONLY,
                    "file_size": os.path.getsize(naya_m_path),
                    "mime_type": "image/jpeg",
                }
            )
            self.stdout.write(self.style.SUCCESS("Populated demo data for naya thapa"))

        # =========================================================================
        # 3. THIRD FAMILY: कार्की परिवार (मावली खलक - Maternal Lineage)
        # =========================================================================
        karki_family, created = Family.objects.get_or_create(
            name="कार्की परिवार (मावली खलक)",
            defaults={
                "description": "ओखलढुङ्गा रुम्झाटारबाट उद्भव भई धरान तथा काठमाडौंमा विस्तारित मावली खलक वंशावली।",
                "owner": demo_user,
                "privacy": "PRIVATE"
            }
        )
        FamilyMembership.objects.get_or_create(family=karki_family, user=demo_user, defaults={"role": "OWNER"})

        # People for Karki family
        k_members_data = [
            {"first": "जीत बहादुर", "last": "कार्की", "gender": "MALE", "birth": datetime.date(1940, 2, 14), "death": datetime.date(2018, 5, 20), "living": False, "place": "ओखलढुङ्गा", "occ": "प्रधानअध्यापक / समाजसेवी", "bio": "ओखलढुङ्गाका प्रख्यात शिक्षक तथा मावली हजुरबुबा।"},
            {"first": "धनमाया", "last": "कार्की", "gender": "FEMALE", "birth": datetime.date(1944, 7, 19), "death": None, "living": True, "place": "ओखलढुङ्गा", "occ": "गृहणी", "bio": "मावली हजुरआमा, स्नेह र पारिवारिक एकताका स्तम्भ।"},
            {"first": "कृष्ण बहादुर", "last": "कार्की", "gender": "MALE", "birth": datetime.date(1968, 11, 5), "death": None, "living": True, "place": "ओखलढुङ्गा", "occ": "वरिष्ठ बैंक अधिकृत", "bio": "मामा, धरान तथा काठमाडौंमा बैंकिङ क्षेत्रमा कार्यरत।"},
            {"first": "सीता", "last": "कार्की", "gender": "FEMALE", "birth": datetime.date(1972, 4, 12), "death": None, "living": True, "place": "धरान", "occ": "शिक्षिका", "bio": "माइजु, माध्यमिक विद्यालय शिक्षिका।"},
            {"first": "कमला", "last": "कार्की", "gender": "FEMALE", "birth": datetime.date(1970, 8, 25), "death": None, "living": True, "place": "ओखलढुङ्गा", "occ": "समाजसेवी", "bio": "आमा, थापा परिवारमा विवाह भई आउनुभएको।"},
            {"first": "रमेश", "last": "कार्की", "gender": "MALE", "birth": datetime.date(1976, 1, 30), "death": None, "living": True, "place": "धरान", "occ": "सिभिल इन्जिनियर", "bio": "कान्छा मामा, सडक तथा पुल निर्माण विशेषज्ञ।"},
            {"first": "अनुप", "last": "कार्की", "gender": "MALE", "birth": datetime.date(1998, 9, 14), "death": None, "living": True, "place": "काठमाडौं", "occ": "मेडिकल डाक्टर", "bio": "मामाको छोरा, त्रि.वि. शिक्षण अस्पतालमा कार्यरत।"},
            {"first": "रोशनी", "last": "कार्की", "gender": "FEMALE", "birth": datetime.date(2002, 12, 3), "death": None, "living": True, "place": "काठमाडौं", "occ": "कम्प्युटर इन्जिनियरिङ विद्यार्थी", "bio": "मामाकी छोरी, विश्वविद्यालय अध्ययनरत।"},
        ]

        created_karki_people = {}
        for idx, km in enumerate(k_members_data):
            p, _ = Person.objects.update_or_create(
                family=karki_family,
                first_name=km["first"],
                last_name=km["last"],
                defaults={
                    "gender": km["gender"],
                    "birth_date": km["birth"],
                    "death_date": km["death"],
                    "is_living": km["living"],
                    "birth_place": km["place"],
                    "occupation": km["occ"],
                    "biography": km["bio"],
                    "privacy": "FAMILY_ONLY",
                }
            )
            # Generate avatar
            avatar_path = os.path.join(settings.MEDIA_ROOT, "profile_photos", f"avatar_karki_{p.id}.png")
            generate_avatar(p, idx, avatar_path)
            p.profile_photo = f"profile_photos/avatar_karki_{p.id}.png"
            p.save()
            created_karki_people[km["first"]] = p

        # Relationships for Karki family
        jit = created_karki_people.get("जीत बहादुर")
        dhan = created_karki_people.get("धनमाया")
        krishna = created_karki_people.get("कृष्ण बहादुर")
        sita = created_karki_people.get("सीता")
        kamala = created_karki_people.get("कमला")
        ramesh = created_karki_people.get("रमेश")
        anup = created_karki_people.get("अनुप")
        roshani = created_karki_people.get("रोशनी")

        def link_karki_child(parent, child):
            if parent and child:
                Relationship.objects.get_or_create(
                    family=karki_family,
                    person_a=parent,
                    person_b=child,
                    relationship_type=Relationship.Type.PARENT_CHILD,
                    defaults={"relationship_subtype": Relationship.Subtype.BIOLOGICAL},
                )

        def link_karki_spouses(p1, p2):
            if p1 and p2:
                MarriagePartnership.objects.get_or_create(
                    family=karki_family,
                    partner_1=p1,
                    partner_2=p2,
                    defaults={
                        "partnership_type": MarriagePartnership.PartnershipType.MARRIAGE,
                        "end_reason": MarriagePartnership.EndReason.ONGOING if (p1.is_living or p2.is_living) else MarriagePartnership.EndReason.DEATH,
                    },
                )
                Relationship.objects.get_or_create(
                    family=karki_family,
                    person_a=p1,
                    person_b=p2,
                    relationship_type=Relationship.Type.SPOUSE,
                )

        link_karki_spouses(jit, dhan)
        link_karki_spouses(krishna, sita)

        for child in [krishna, kamala, ramesh]:
            link_karki_child(jit, child)
            link_karki_child(dhan, child)

        for child in [anup, roshani]:
            link_karki_child(krishna, child)
            link_karki_child(sita, child)

        # Events for Karki family
        k_events = [
            {
                "event_type": Event.EventType.BIRTH,
                "title": "जीत बहादुर कार्कीको जन्म (ओखलढुङ्गा)",
                "date": datetime.date(1940, 2, 14),
                "place": "ओखलढुङ्गा, रुम्झाटार",
                "description": "मावली खलकका कुलपुरुष जीत बहादुर कार्कीको जन्म।",
                "person": jit,
            },
            {
                "event_type": Event.EventType.MARRIAGE,
                "title": "जीत बहादुर तथा धनमायाको शुभविवाह",
                "date": datetime.date(1960, 5, 10),
                "place": "ओखलढुङ्गा",
                "description": "ओखलढुङ्गामा सम्पन्न भएको परम्परागत वैवाहिक समारोह।",
                "person": jit,
            },
            {
                "event_type": Event.EventType.MIGRATION,
                "title": "धरान उपमहानगरपालिकामा बसाइँसराइ",
                "date": datetime.date(1982, 11, 20),
                "place": "धरान, सुनसरी",
                "description": "पहाडबाट पूर्वी नेपालको व्यापारिक केन्द्र धरानमा स्थानान्तरण।",
                "person": jit,
            },
            {
                "event_type": Event.EventType.EDUCATION,
                "title": "डा. अनुप कार्कीको एम.बि.बि.एस. (MBBS) उपाधि",
                "date": datetime.date(2022, 9, 15),
                "place": "काठमाडौं",
                "description": "मावली खलकमा पहिलो डाक्टर बन्न सफल भएको ऐतिहासिक गौरवमय क्षण।",
                "person": anup,
            },
        ]
        for ev in k_events:
            Event.objects.update_or_create(
                family=karki_family,
                title=ev["title"],
                defaults={
                    "event_type": ev["event_type"],
                    "date": ev["date"],
                    "place": ev["place"],
                    "description": ev["description"],
                    "person": ev["person"],
                }
            )

        # Stories for Karki family
        s_karki_1 = os.path.join(settings.MEDIA_ROOT, "story_covers", "story_karki_rumjatar.jpg")
        s_karki_2 = os.path.join(settings.MEDIA_ROOT, "story_covers", "story_karki_dharan.jpg")
        draw_vintage_photo("ओखलढुङ्गा रुम्झाटारको मावली थलो", "जीत बहादुर कार्कीको जीवनकथा", s_karki_1, theme="sepia")
        draw_vintage_photo("धरानको बसाइँ र नयाँ अध्याय", "पूर्वी नेपालको यात्रा", s_karki_2, theme="temple")

        karki_stories = [
            {
                "title": "ओखलढुङ्गा रुम्झाटारको मावली थलो र जीत बहादुरको योगदान",
                "cover_image": "story_covers/story_karki_rumjatar.jpg",
                "content": """# ओखलढुङ्गा रुम्झाटारको मावली थलो र जीत बहादुरको योगदान

ओखलढुङ्गाको रुम्झाटार डाँडामा हाम्रा मावली हजुरबुबा **जीत बहादुर कार्की**ले गाउँको विद्यालय स्थापनामा नेतृत्वदायी भूमिका खेल्नुभएको थियो।

उहाँले आफ्नै जग्गा दान गरेर गाउँका बालबालिकाहरूका लागि प्राथमिक पाठशाला खोल्नुभयो। उहाँको यस त्यागले सयौं बालबालिकाले अक्षर चिन्न पाए। मावली खलकमा उहाँको नाम सधैं उच्च सम्मानका साथ लिइन्छ।""",
                "associated": [jit, dhan],
            },
            {
                "title": "धरानको बसाइँ र नयाँ शैक्षिक आयाम",
                "cover_image": "story_covers/story_karki_dharan.jpg",
                "content": """# धरानको बसाइँ र नयाँ शैक्षिक आयाम

वि.सं. २०३९ सालमा ओखलढुङ्गाबाट धरान झरेपछि परिवारले शिक्षा र व्यवसायलाई मुख्य प्राथमिकता दियो।

धरानको विजयपुर डाँडा, पिण्डेश्वर मन्दिर र बजार क्षेत्रमा हुर्केका दोश्रो र तेस्रो पुस्ताका सन्तानहरू आज चिकित्सा, बैंकिङ तथा प्राविधिक क्षेत्रमा राष्ट्रिय स्तरमा स्थापित हुन सफल भएका छन्।""",
                "associated": [krishna, sita, anup],
            },
        ]
        for st in karki_stories:
            s_obj, _ = Story.objects.update_or_create(
                family=karki_family,
                title=st["title"],
                defaults={
                    "author": demo_user,
                    "content": st["content"],
                    "cover_image": st["cover_image"],
                    "status": Story.Status.PUBLISHED,
                    "published_at": datetime.datetime.now(),
                }
            )
            s_obj.associated_people.set([p for p in st["associated"] if p])

        # Media for Karki family
        karki_media = [
            {
                "title": "जीत बहादुर कार्कीको ऐतिहासिक तस्विर (वि.सं. २०३२)",
                "sub": "ओखलढुङ्गा — वि.सं. २०३२",
                "desc": "रुम्झाटार विद्यालय प्रांगणमा खिचिएको दुर्लभ तस्विर।",
                "theme": "sepia",
                "file": "family_media/media_karki_jit_portrait.jpg",
                "type": Media.MediaType.PHOTO,
                "person": jit,
                "date": datetime.date(1975, 11, 20),
            },
            {
                "title": "रुम्झाटार पैतृक घर (वि.सं. २०४०)",
                "sub": "पैतृक निवास — रुम्झाटार",
                "desc": "ओखलढुङ्गाको परम्परागत नेपाली घर।",
                "theme": "sepia",
                "file": "family_media/media_karki_house.jpg",
                "type": Media.MediaType.PHOTO,
                "person": None,
                "date": datetime.date(1983, 4, 15),
            },
            {
                "title": "डा. अनुप कार्कीको दीक्षान्त कदरपत्र (वि.सं. २०७९)",
                "sub": "त्रिभुवन विश्वविद्यालय — दीक्षान्त",
                "desc": "चिकित्सा शास्त्र अध्ययन संस्थानबाट प्राप्त उपाधि।",
                "theme": "doc",
                "file": "family_media/media_karki_anup_degree.jpg",
                "type": Media.MediaType.CERTIFICATE,
                "person": anup,
                "date": datetime.date(2022, 12, 10),
            },
        ]
        for km in karki_media:
            abs_p = os.path.join(settings.MEDIA_ROOT, km["file"])
            draw_vintage_photo(km["title"], km["sub"], abs_p, theme=km["theme"])
            Media.objects.update_or_create(
                family=karki_family,
                title=km["title"],
                defaults={
                    "uploader": demo_user,
                    "description": km["desc"],
                    "file": km["file"],
                    "media_type": km["type"],
                    "person": km["person"],
                    "captured_date": km["date"],
                    "visibility": Media.Visibility.FAMILY_ONLY,
                    "file_size": os.path.getsize(abs_p),
                    "mime_type": "image/jpeg",
                }
            )
        self.stdout.write(self.style.SUCCESS("Populated full demo data for कार्की परिवार (मावली खलक)"))

        self.stdout.write(self.style.SUCCESS("\n========================================================"))
        self.stdout.write(self.style.SUCCESS("ALL DEMO DATA POPULATED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS("========================================================"))
