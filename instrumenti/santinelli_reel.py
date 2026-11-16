from PIL import Image, ImageDraw, ImageFilter
import sys
sys.path.insert(0, ".")
from santinelli_banners import font, text_c, fit, badge, NAVY, CREAM, GOLD, RED, ADDR1, ADDR2, cover

W, H = 1080, 1920

def brand(d):
    y = text_c(d, W, 250, "SANTINELLI", font("Bold", 52), CREAM, track=19)
    text_c(d, W, y + 12, "МЪЖКО ОБЛЕКЛО · В АУТЛЕТА НА ETERE", font("Medium", 26), GOLD, track=3)

def caption(name, small, big, price=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # top dim band for brand legibility
    for y in range(480):
        a = int(150 * (1 - y / 480) ** 1.3)
        d.line([(0, y), (W, y)], fill=NAVY + (a,))
    brand(d)
    fs = font("SemiBold", 46)
    fb = [fit(d, b, "Black", 104, W - 140) for b in big]
    fp = font("Black", 150) if price else None
    lh = lambda f: f.getbbox("ЙАgy")[3] - f.getbbox("ЙАgy")[1]
    h = (lh(fs) + 24 if small else 0) + sum(lh(f) + 10 for f in fb) + (lh(fp) + 20 if price else 0)
    y0 = 1180 - h // 2
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([50, y0 - 50, W - 50, y0 + h + 40], 36, fill=NAVY + (190,))
    img = Image.alpha_composite(box, img)
    d = ImageDraw.Draw(img)
    y = y0
    if small: y = text_c(d, W, y, small, fs, CREAM) + 24
    for b, f in zip(big, fb): y = text_c(d, W, y, b, f, "white") + 10
    if price: text_c(d, W, y + 10, price, fp, GOLD)
    badge(d, W - 175, 610, 115, "ДО", "−80%")
    img.save(f"tmp/{name}.png")

caption("ovA", None, ["ДОКАТО ТЯ", "ПАЗАРУВА…"])
caption("ovB", "…ти намираш", ["УНИКАЛНИ САКА", "ПОД 80 €"])
caption("ovC", "Мъжко вълнено палто", ["ЗА ЗИМАТА"], "80 €")
caption("ovD", "Британски туид", ["ВЪЛНЕНО САКО"], "60 €")

# end card on blurred store photo
bg = cover(Image.open("src/p4.jpg").convert("RGB"), W, H, 0.55, 0.5).filter(ImageFilter.GaussianBlur(18)).convert("RGBA")
bg = Image.alpha_composite(bg, Image.new("RGBA", (W, H), NAVY + (195,)))
d = ImageDraw.Draw(bg)
brand(d)
y = 560
y = text_c(d, W, y, "Италиански и английски", font("SemiBold", 52), CREAM) + 14
y = text_c(d, W, y, "сака от реномиран", font("SemiBold", 52), CREAM) + 14
y = text_c(d, W, y, "производител", font("SemiBold", 52), CREAM) + 50
y = text_c(d, W, y, "САКА 60 €", font("Black", 120), GOLD) + 20
y = text_c(d, W, y, "ПАЛТА 80 €", font("Black", 120), GOLD) + 60
badge(d, W // 2, y + 110, 110, "ДО", "−80%")
y += 460
d.rounded_rectangle([60, y, W - 60, y + 210], 30, fill=CREAM)
text_c(d, W, y - 170, "BLACK FRIDAY · 16–29.11", font("Black", 62), "white")
text_c(d, W, y - 90, "всеки ден 10–18 ч", font("SemiBold", 40), CREAM)
yy = text_c(d, W, y + 40, ADDR1, font("ExtraBold", 50), NAVY) + 18
text_c(d, W, yy, ADDR2, font("SemiBold", 42), NAVY)
bg.convert("RGB").save("tmp/endcard.png")
print("ok")
