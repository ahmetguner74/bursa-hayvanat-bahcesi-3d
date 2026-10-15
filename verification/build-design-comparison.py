"""Evidence contact sheets; preserve screenshot pixels/aspect, never app assets."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "design/2026-10-15-sade-kesif"
QA = DESIGN / "qa"
source = Image.open(DESIGN / "sade-kesif-mockup.png").convert("RGB")
states = [
    ("Overview", (8, 44, 1440, 555), "overview-desktop.jpg"),
    ("Habitat", (8, 599, 720, 1077), "aviary-desktop.jpg"),
    ("Animal", (728, 599, 1440, 1077), "flamingo-desktop.jpg"),
]
sheet = Image.new("RGB", (2560, 2232), "#f8f7ef")
draw = ImageDraw.Draw(sheet)
for index, (name, crop, file) in enumerate(states):
    top = index * 744
    draw.text((12, top + 6), name + " - reference / presentation frame", fill="#193c30")
    draw.text((1292, top + 6), name + " - actual browser 1280 x 720", fill="#193c30")
    reference = ImageOps.pad(source.crop(crop), (1280, 720), color="#f8f7ef")
    actual = Image.open(QA / file).convert("RGB")
    assert actual.size == (1280, 720)
    sheet.paste(reference, (0, top + 24))
    sheet.paste(actual, (1280, top + 24))
sheet.save(QA / "comparison-full.jpg", quality=94)

# Native-pixel UI comparison; no upscaling of the mini presentation frames.
focus = Image.new("RGB", (900, 250), "#f8f7ef")
focus.paste(source.crop((740, 610, 1125, 670)), (12, 35))
actual = Image.open(QA / "flamingo-desktop.jpg")
focus.paste(actual.crop((18, 18, 403, 78)), (462, 35))
draw = ImageDraw.Draw(focus)
draw.text((12, 12), "Reference header - native pixels", fill="#193c30")
draw.text((462, 12), "Browser header - native pixels", fill="#193c30")
focus.paste(source.crop((1045, 830, 1165, 900)), (12, 140))
focus.paste(actual.crop((580, 135, 700, 215)), (462, 140))
draw.text((12, 116), "Reference name / hover treatment", fill="#193c30")
draw.text((462, 116), "Browser name / selected treatment", fill="#193c30")
focus.save(QA / "comparison-ui.jpg", quality=95)
print(QA / "comparison-full.jpg")
print(QA / "comparison-ui.jpg")
