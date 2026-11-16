import sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
from etere_banners import font, text_c, fit, badge, header, lh, cover, INK, CREAM, GOLD, RED, ADDR1, ADDR2

W, H = 1080, 1920

def caption(name, small, big, gold=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for y in range(500): d.line([(0, y), (W, y)], fill=INK + (int(150 * (1 - y / 500) ** 1.3),))
    header(d, W, 250)
    fs = font("SemiBold", 46); fb = [fit(d, b, "Black", 104, W - 140) for b in big]; fg = font("Black", 120) if gold else None
    h = (lh(fs) + 24 if small else 0) + sum(lh(f) + 10 for f in fb) + (lh(fg) + 20 if gold else 0)
    y0 = 1180 - h // 2
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([50, y0 - 50, W - 50, y0 + h + 40], 36, fill=INK + (195,))
    img = Image.alpha_composite(box, img); d = ImageDraw.Draw(img); y = y0
    if small: y = text_c(d, W, y, small, fs, CREAM) + 24
    for b, f in zip(big, fb): y = text_c(d, W, y, b, f, "white") + 10
    if gold: text_c(d, W, y + 10, gold, fg, GOLD)
    badge(d, W - 175, 640, 115)
    img.save(f"tmp/{name}.png")

caption("ovA", "Пловдив, бъди готова…", ["BLACK FRIDAY", "В АУТЛЕТА"])
caption("ovB", "Студът идва", ["ЗИМНИ ЯКЕТА", "И ПАЛТА"])
caption("ovC", "Всеки ден", ["НОВА ОФЕРТА", "НА ЗАКАЧАЛКИТЕ"])
caption("ovD", "2 седмици", ["16–29 НОЕМВРИ"], "до −80%")

bg = cover(Image.open("src/p1.jpg").convert("RGB"), W, H).filter(ImageFilter.GaussianBlur(18)).convert("RGBA")
bg = Image.alpha_composite(bg, Image.new("RGBA", (W, H), INK + (200,))); d = ImageDraw.Draw(bg)
header(d, W, 250)
y = 560
y = text_c(d, W, y, "BLACK FRIDAY", font("Black", 120), "white") + 20
y = text_c(d, W, y, "16–29 ноември", font("Black", 84), GOLD) + 18
y = text_c(d, W, y, "всеки ден 10:00–18:00", font("SemiBold", 50), CREAM) + 40
badge(d, W // 2, y + 120, 120)
y += 300
y = text_c(d, W, y, "+ мъжка мода SANTINELLI", font("SemiBold", 44), CREAM) + 50
d.rounded_rectangle([60, y, W - 60, y + 210], 30, fill=CREAM)
yy = text_c(d, W, y + 40, ADDR1, font("ExtraBold", 50), INK) + 18
text_c(d, W, yy, ADDR2, font("SemiBold", 42), INK)
bg.convert("RGB").save("tmp/endcard.png")
print("ok")
