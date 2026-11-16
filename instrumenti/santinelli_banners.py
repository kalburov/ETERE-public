from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

F = "/usr/share/fonts/opentype/inter/"
def font(w, s): return ImageFont.truetype(F + f"Inter-{w}.otf", s)

NAVY = (16, 22, 36)
CREAM = (246, 238, 222)
GOLD = (214, 170, 92)
RED = (200, 38, 44)

ADDR1 = "Аутлет ETERE · Пловдив"
ADDR2 = "бул. „6-ти Септември“ 260"

def cover(img, W, H, fx=0.5, fy=0.5):
    iw, ih = img.size
    s = max(W / iw, H / ih)
    img = img.resize((round(iw * s), round(ih * s)), Image.LANCZOS)
    iw, ih = img.size
    x = int((iw - W) * fx); y = int((ih - H) * fy)
    return img.crop((x, y, x + W, y + H))

def grade(img):
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.06)
    return ImageEnhance.Sharpness(img).enhance(1.15)

def gradient(W, H, top_h, bot_h, top_a=200, bot_a=235):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for y in range(top_h):
        a = int(top_a * (1 - y / top_h) ** 1.4)
        d.line([(0, y), (W, y)], fill=NAVY + (a,))
    for y in range(bot_h):
        a = int(bot_a * (y / bot_h) ** 1.2)
        d.line([(0, H - bot_h + y), (W, H - bot_h + y)], fill=NAVY + (a,))
    return g

def text_c(d, W, y, txt, f, fill, track=0):
    if track:
        widths = [d.textlength(c, font=f) + track for c in txt]
        x = (W - (sum(widths) - track)) / 2
        for c, w in zip(txt, widths):
            d.text((x, y), c, font=f, fill=fill); x += w
    else:
        w = d.textlength(txt, font=f)
        d.text(((W - w) / 2, y), txt, font=f, fill=fill)
    b = f.getbbox("ЙАgy")
    return y + (b[3] - b[1])

def fit(d, txt, weight, size, maxw):
    while size > 20:
        f = font(weight, size)
        if d.textlength(txt, font=f) <= maxw: return f
        size -= 2
    return font(weight, size)

def badge(d, cx, cy, r, line1, line2):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    f1 = font("ExtraBold", int(r * 0.30)); f2 = font("Black", int(r * 0.62))
    w1 = d.textlength(line1, font=f1); w2 = d.textlength(line2, font=f2)
    d.text((cx - w1 / 2, cy - r * 0.55), line1, font=f1, fill="white")
    d.text((cx - w2 / 2, cy - r * 0.25), line2, font=f2, fill="white")

def render(photo, out, W, H, fx, fy, kicker, head, sub, price=None, badge_txt=("ДО", "−80%")):
    img = grade(cover(Image.open(photo).convert("RGB"), W, H, fx, fy)).convert("RGBA")
    tall = H / W > 1.5
    img = Image.alpha_composite(img, gradient(W, H, int(H * (0.30 if tall else 0.34)), int(H * (0.55 if tall else 0.58)), 210, 250))
    base = img
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = int(W * 0.07)
    # top brand
    y = int(H * (0.12 if tall else 0.05))
    y = text_c(d, W, y, "SANTINELLI", font("Bold", int(W * 0.05)), CREAM, track=int(W * 0.018))
    y = text_c(d, W, y + int(W * 0.012), "МЪЖКО ОБЛЕКЛО · В АУТЛЕТА НА ETERE", font("Medium", int(W * 0.024)), GOLD, track=3)
    # badge
    br = int(W * 0.12)
    badge(d, W - m - br + 10, int(H * (0.26 if tall else 0.25)), br, *badge_txt)
    # bottom block
    lines = []
    fk = font("SemiBold", int(W * 0.04))
    fh = [fit(d, h, "Black", int(W * 0.095), W - 2 * m) for h in head]
    fs = fit(d, sub or "", "Medium", int(W * 0.034), W - 2 * m)
    fa = font("SemiBold", int(W * 0.03))
    block = []
    if kicker: block.append((kicker, fk, CREAM, 14))
    for h, f in zip(head, fh): block.append((h, f, "white", 6))
    if price: block.append((price, font("Black", int(W * 0.13)), GOLD, 10))
    if sub: block.append((sub, fs, CREAM, 26))
    # measure
    def lh(f):
        b = f.getbbox("ЙАgy"); return b[3] - b[1]
    total = sum(lh(f) + gap for _, f, _, gap in block)
    foot_h = int(1350 * 0.115) + 78
    safe = 250 if tall else 0
    y = H - safe - foot_h - int(H * 0.035) - total
    for t, f, c, gap in block:
        y = text_c(d, W, y, t, f, c) + gap
    # footer bar
    fy0 = H - safe - foot_h
    # shadow under text
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(img.getchannel("A").point(lambda a: int(a * 0.85)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(Image.alpha_composite(base, sh), img)
    d = ImageDraw.Draw(img)
    d.rectangle([0, fy0, W, fy0 + foot_h], fill=CREAM)
    d.rectangle([0, fy0, W, fy0 + 78], fill=(12, 12, 12))
    text_c(d, W, fy0 + 16, "BLACK FRIDAY · 16–29.11 · 10–18 ч", font("Black", 40), "white")
    if safe: d.rectangle([0, fy0 + foot_h, W, H], fill=NAVY)
    pin = "📍"
    y2 = fy0 + 78 + 22
    y2 = text_c(d, W, y2, ADDR1, font("ExtraBold", int(W * 0.036)), NAVY)
    text_c(d, W, y2 + 8, ADDR2, fa, NAVY)
    img.convert("RGB").save(out, quality=93)

if __name__ == "__main__":
    S = "src/"
    jobs = [
        # name, photo, fx, fy, kicker, head lines, price, sub
        ("01_dokato_tya", "p4.jpg", 0.55, 0.5, "Докато тя пазарува…",
         ["ТИ НАМИРАШ", "САКО ПОД 80 €"], None, "Италиански и английски сака от реномиран производител"),
        ("02_sako_60", "p1.jpg", 0.5, 0.45, "Вълнено сако",
         ["СЕГА САМО"], "60 €", "Цял щанд сака · пробваш на място"),
        ("03_tuid", "p3.jpg", 0.3, 0.5, "Британски туид",
         ["УНИКАЛНИ НАХОДКИ", "ЗА 60 €"], None, "Сака, които в бутик не си виждал на тази цена"),
        ("04_palto_80", "p2.jpg", 0.5, 0.45, "Мъжко вълнено палто",
         ["ЗА ЗИМАТА —"], "80 €", "Палта и сака · ограничени бройки и размери"),
    ]
    os.makedirs("out/banners", exist_ok=True)
    for name, p, fx, fy, k, h, price, sub in jobs:
        render(S + p, f"out/banners/{name}_4x5.jpg", 1080, 1350, fx, fy, k, h, sub, price)
        render(S + p, f"out/banners/{name}_9x16.jpg", 1080, 1920, fx, fy, k, h, sub, price)
    print("ok")
