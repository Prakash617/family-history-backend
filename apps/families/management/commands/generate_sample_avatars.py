import os
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.management.base import BaseCommand
from apps.members.models import Person

male_palettes = [
    ((30, 58, 138), (59, 130, 246), (219, 234, 254)),    # Royal Blue
    ((20, 83, 45), (34, 197, 94), (220, 252, 231)),      # Emerald
    ((120, 53, 15), (217, 119, 6), (254, 243, 199)),    # Amber/Gold
    ((88, 28, 135), (147, 51, 234), (243, 232, 255)),   # Purple
    ((15, 76, 92), (13, 148, 136), (204, 251, 241)),    # Deep Teal
    ((124, 45, 18), (234, 88, 12), (255, 237, 213)),    # Terracotta
    ((15, 23, 42), (71, 85, 105), (241, 245, 249)),     # Slate
    ((67, 56, 202), (99, 102, 241), (224, 231, 255)),   # Indigo
]

female_palettes = [
    ((131, 24, 67), (236, 72, 153), (252, 231, 243)),   # Rose Pink
    ((136, 19, 55), (225, 29, 72), (255, 228, 230)),    # Crimson / Ruby
    ((107, 33, 168), (192, 132, 252), (250, 245, 255)), # Violet / Orchid
    ((154, 52, 18), (251, 146, 60), (255, 237, 213)),   # Warm Coral
    ((13, 148, 136), (45, 212, 191), (204, 251, 241)),  # Mint / Aquamarine
    ((162, 28, 175), (232, 121, 249), (250, 232, 255)), # Magenta
]

def generate_avatar(person, index, output_path):
    size = 256
    img = Image.new("RGB", (size, size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    gender = person.gender

    if gender == "FEMALE":
        dark, primary, light = female_palettes[index % len(female_palettes)]
    else:
        dark, primary, light = male_palettes[index % len(male_palettes)]

    # Background gradient
    for y in range(size):
        factor = y / size
        r = int(light[0] * (1 - factor) + primary[0] * factor * 0.35 + light[0] * 0.65)
        g = int(light[1] * (1 - factor) + primary[1] * factor * 0.35 + light[1] * 0.65)
        b = int(light[2] * (1 - factor) + primary[2] * factor * 0.35 + light[2] * 0.65)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # Outer ring
    draw.ellipse([6, 6, size - 6, size - 6], outline=primary, width=3)

    if gender == "FEMALE":
        # Hair back
        draw.ellipse([65, 55, size - 65, 170], fill=(40, 25, 22))

        # Shoulders / Kurtha
        draw.ellipse([34, 155, size - 34, size + 80], fill=dark)
        # Saree shawl / scarf
        draw.polygon([(60, 165), (110, 256), (145, 256), (90, 160)], fill=primary)

        # Neck
        draw.rectangle([112, 125, 144, 160], fill=(235, 198, 165))

        # Head
        draw.ellipse([86, 68, size - 86, 152], fill=(245, 212, 182))

        # Hair front / parted
        draw.chord([84, 60, size - 84, 115], 180, 360, fill=(40, 25, 22))
        draw.polygon([(84, 85), (128, 75), (105, 105)], fill=(40, 25, 22))
        draw.polygon([(size - 84, 85), (128, 75), (size - 105, 105)], fill=(40, 25, 22))

        # Facial features
        draw.arc([102, 98, 116, 108], 0, 180, fill=(60, 40, 35), width=2)
        draw.arc([140, 98, 154, 108], 0, 180, fill=(60, 40, 35), width=2)
        draw.arc([100, 92, 118, 102], 180, 360, fill=(50, 30, 25), width=2)
        draw.arc([138, 92, 156, 102], 180, 360, fill=(50, 30, 25), width=2)
        draw.arc([118, 120, 138, 132], 0, 180, fill=(190, 60, 60), width=2)
        # Red Bindi
        draw.ellipse([125, 90, 131, 96], fill=(220, 38, 38))
    else:
        # Shoulders / Daura Suruwal coat
        draw.ellipse([34, 155, size - 34, size + 80], fill=dark)
        # Coat collar v-neck
        draw.polygon([(114, 150), (128, 185), (142, 150)], fill=(245, 245, 245))

        # Neck
        draw.rectangle([112, 125, 144, 155], fill=(235, 198, 165))

        # Head
        draw.ellipse([86, 68, size - 86, 152], fill=(245, 212, 182))

        # Dhaka topi / Nepali cap
        topi_color = (185, 28, 28) if (index % 2 == 0) else (30, 41, 59)
        topi_points = [(84, 86), (94, 46), (128, 38), (162, 48), (172, 86)]
        draw.polygon(topi_points, fill=topi_color)
        draw.line([(91, 66), (165, 68)], fill=(245, 158, 11), width=3)

        # Facial features
        draw.arc([102, 98, 116, 108], 0, 180, fill=(60, 40, 35), width=2)
        draw.arc([140, 98, 154, 108], 0, 180, fill=(60, 40, 35), width=2)
        draw.arc([100, 92, 118, 102], 180, 360, fill=(50, 30, 25), width=2)
        draw.arc([138, 92, 156, 102], 180, 360, fill=(50, 30, 25), width=2)
        draw.arc([118, 122, 138, 134], 0, 180, fill=(180, 50, 50), width=2)

        # Mustache for patriarchs and elders
        if index < 5 or (index % 3 == 0):
            draw.arc([112, 116, 128, 126], 0, 180, fill=(40, 30, 25), width=3)
            draw.arc([128, 116, 144, 126], 0, 180, fill=(40, 30, 25), width=3)

    # Initial badge on bottom right
    badge_r = 28
    bx, by = size - 42, size - 42
    draw.ellipse([bx - badge_r, by - badge_r, bx + badge_r, by + badge_r], fill=primary, outline=(255, 255, 255), width=3)

    char = person.first_name[0] if person.first_name else (person.full_name[0] if person.full_name else "?")
    is_ascii = ord(char) < 128
    try:
        if is_ascii:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 24)
            char = char.upper()
        else:
            font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansDevanagariUI-Bold.ttf", 24)
        bbox = draw.textbbox((0, 0), char, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((bx - tw / 2, by - th / 2 - 3), char, fill=(255, 255, 255), font=font)
    except Exception:
        pass

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, quality=95)


class Command(BaseCommand):
    help = "Generate sample portrait avatar images for all family tree members."

    def handle(self, *args, **options):
        media_dir = os.path.join(settings.MEDIA_ROOT, "profiles")
        os.makedirs(media_dir, exist_ok=True)

        people = Person.objects.all().order_by("birth_date", "created_at")
        count = 0
        for idx, person in enumerate(people):
            filename = f"person_{person.id}.png"
            full_path = os.path.join(media_dir, filename)
            generate_avatar(person, idx, full_path)
            person.profile_photo = f"profiles/{filename}"
            person.save(update_fields=["profile_photo"])
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Generated sample portraits for {count} members."))
