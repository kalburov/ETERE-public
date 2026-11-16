from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, sys

F = "/usr/share/fonts/opentype/inter/"
def font(w, s): return ImageFont.truetype(F + f"Inter-{w}.otf", s)

INK = (14, 14, 16)
CREAM = (246, 238, 222)
RED = (206, 30, 44)
GOLD = (222, 184, 120)
ADDR1 = "Аутлет ETERE · Пловдив"
ADDR2 = "бул. „6-ти Септември“ 260"
BF = "BLACK FRIDAY · 16–29.11 · 10–18 ч"

def cover(img, W, H, fx=0.5, fy=0.5):
    iw, ih = img.size; s = max(W / iw, H / ih)
    img = img.resize((round(iw * s), round(ih * s)), Image.LANCZOS); iw, ih = img.size
    x = int((iw - W) * fx); y = int((ih - H) * fy)
    return img.crop((x, y, x + W, y + H))

def grade(img):
    img = ImageEnhance.Contrast(img).enhance(1.08); img = ImageEnhance.Color(img).enhance(1.05)
    return ImageEnhance.Sharpness(img).enhance(1.1)

def lh(f): b = f.getbbox("ЙАgy"); return b[3] - b[1]

def text_c(d, W, y, txt, f, fill, track=0):
    if track:
        ws = [d.textlength(c, font=f) + track for c in txt]; x = (W - (sum(ws) - track)) / 2
        for c, w in zip(txt, ws): d.text((x, y), c, font=f, fill=fill); x += w
    else:
        d.text(((W - d.textlength(txt, font=f)) / 2, y), txt, font=f, fill=fill)
    return y + lh(f)

def fit(d, txt, w, size, maxw):
    while size > 20 and d.textlength(txt, font=font(w, size)) > maxw: size -= 2
    return font(w, size)

def gradient(W, H, top_h, bot_h, top_a=200, bot_a=245):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for y in range(top_h): d.line([(0, y), (W, y)], fill=INK + (int(top_a * (1 - y / top_h) ** 1.4),))
    for y in range(bot_h): d.line([(0, H - bot_h + y), (W, H - bot_h + y)], fill=INK + (int(bot_a * (y / bot_h) ** 1.2),))
    return g

def badge(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    f1 = font("ExtraBold", int(r * .30)); f2 = font("Black", int(r * .62))
    d.text((cx - d.textlength("ДО", font=f1) / 2, cy - r * .55), "ДО", font=f1, fill="white")
    d.text((cx - d.textlength("−80%", font=f2) / 2, cy - r * .25), "−80%", font=f2, fill="white")

def shadowed(base, layer):
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); sh.putalpha(layer.getchannel("A").point(lambda a: int(a * .85)))
    return Image.alpha_composite(Image.alpha_composite(base, sh.filter(ImageFilter.GaussianBlur(10))), layer)

def header(d, W, y):
    y = text_c(d, W, y, "ETERE", font("Bold", int(W * .062)), CREAM, track=int(W * .03))
    return text_c(d, W, y + int(W * .012), "ДАМСКА МОДА · АУТЛЕТ ПЛОВДИВ", font("Medium", int(W * .024)), GOLD, track=3)

def footer(d, W, H, safe):
    foot_h = 155 + 78; fy0 = H - safe - foot_h
    d.rectangle([0, fy0, W, H - safe], fill=CREAM)
    d.rectangle([0, fy0, W, fy0 + 78], fill=INK)
    text_c(d, W, fy0 + 16, BF, font("Black", 40), "white")
    y2 = text_c(d, W, fy0 + 100, ADDR1, font("ExtraBold", int(W * .036)), INK)
    text_c(d, W, y2 + 8, ADDR2, font("SemiBold", int(W * .03)), INK)
    if safe: d.rectangle([0, H - safe, W, H], fill=INK)
    return fy0

def photo_banner(photo, out, W, H, fx, fy, kicker, head, sub, big=None):
    tall = H / W > 1.5; safe = 250 if tall else 0
    base = Image.alpha_composite(grade(cover(Image.open(photo).convert("RGB"), W, H, fx, fy)).convert("RGBA"),
                                 gradient(W, H, int(H * (.30 if tall else .32)), int(H * (.58 if tall else .62))))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    header(d, W, int(H * (.12 if tall else .05)))
    m = int(W * .07)
    block = []
    if kicker: block.append((kicker, font("SemiBold", int(W * .042)), CREAM, 14))
    for h in head: block.append((h, fit(d, h, "Black", int(W * .095), W - 2 * m), "white", 6))
    if big: block.append((big, font("Black", int(W * .13)), GOLD, 10))
    if sub: block.append((sub, fit(d, sub, "Medium", int(W * .034), W - 2 * m), CREAM, 26))
    total = sum(lh(f) + g for _, f, _, g in block)
    y = H - safe - 233 - int(H * .035) - total
    for t, f, c, g in block: y = text_c(d, W, y, t, f, c) + g
    img = shadowed(base, lay); d = ImageDraw.Draw(img)
    badge(d, W - m - int(W * .12) + 10, int(H * (.26 if tall else .25)), int(W * .12))
    footer(d, W, H, safe)
    img.convert("RGB").save(out, quality=93)

def card_banner(photo, out, W, H, fx, fy, title, rows, cta):
    """Info card: blurred store bg + list of rows (icon, bold, light)."""
    tall = H / W > 1.5; safe = 250 if tall else 0
    bg = cover(Image.open(photo).convert("RGB"), W, H, fx, fy).filter(ImageFilter.GaussianBlur(14)).convert("RGBA")
    img = Image.alpha_composite(bg, Image.new("RGBA", (W, H), INK + (205,)))
    d = ImageDraw.Draw(img)
    y = header(d, W, int(H * (.12 if tall else .05)))
    y += int(H * (.06 if tall else .035))
    y = text_c(d, W, y, title, fit(d, title, "Black", 78, W - 120), "white") + int(H * .03)
    m = 80
    fb = font("ExtraBold", 46 if tall else 40); fl = font("Medium", 36 if tall else 32)
    gap = 54 if tall else 14
    for ic, b, l in rows:
        d.ellipse([m, y + 2, m + 56, y + 58], fill=RED)
        d.text((m + 28 - d.textlength(ic, font=font("Black", 30)) / 2, y + 10), ic, font=font("Black", 30), fill="white")
        d.text((m + 80, y), b, font=fb, fill="white")
        yy = y + lh(fb) + 8
        if l: d.text((m + 80, yy), l, font=fl, fill=CREAM); yy += lh(fl)
        y = yy + gap
    if cta:
        y += 6
        d.rounded_rectangle([m, y, W - m, y + 100], 24, fill=GOLD)
        text_c(d, W, y + 24, cta, fit(d, cta, "Black", 50, W - 2 * m - 40), INK)
    footer(d, W, H, safe)
    img.convert("RGB").save(out, quality=93)

if __name__ == "__main__":
    os.makedirs("out/banners", exist_ok=True)
    P = "src/p1.jpg"; FW = "frames/f_IMG_3059_3.5.jpg"; FS = "frames/f_IMG_3060_8.5.jpg"; FQ = "frames/f_IMG_3060_6.5.jpg"; FN = "frames/f_IMG_3061_8.2.jpg"
    for W, H, tag in [(1080, 1350, "4x5"), (1080, 1920, "9x16")]:
        photo_banner(P, f"out/banners/E1_black_friday_{tag}.jpg", W, H, .5, .55, "2 седмици в аутлета на ETERE",
                     ["BLACK FRIDAY", "В АУТЛЕТА"], "Нова оферта всеки ден · 16–29 ноември")
        photo_banner(FW, f"out/banners/E2_zimni_yaketa_{tag}.jpg", W, H, .5, .45, "Студът идва. Ние сме готови.",
                     ["ЗИМНИ ЯКЕТА", "И ПАЛТА"], "Якета с качулки, палта, сака · на аутлет цени")
        card_banner(FS, f"out/banners/E3_kak_da_ni_namerish_{tag}.jpg", W, H, .5, .5, "КАК ДА НИ НАМЕРИШ",
                    [("1", "бул. „6-ти Септември“ 260", "фабриката на Вени стил, Пловдив"),
                     ("2", "„Етере Пловдив“ в Google Maps", "търси точно така и следвай пинчето"),
                     ("3", "Паркинг пред сградата", "идваш с колата, без да търсиш място"),
                     ("4", "Всеки ден 10:00 – 18:00", "вкл. събота и неделя, 16–29.11")],
                    "Изгубиш ли се? 0889 716 776")
        card_banner(FQ, f"out/banners/E4_chzv_{tag}.jpg", W, H, .5, .5, "ВЪПРОСИ? ОТГОВОРИ.",
                    [("?", "Докога продължава?", "до 29 ноември, всеки ден 10–18 ч"),
                     ("?", "Къде точно сте?", "бул. „6-ти Септември“ 260, Пловдив"),
                     ("?", "Има ли паркинг?", "да, пред сградата"),
                     ("?", "Само дамско ли е?", "не, има и мъжко облекло SANTINELLI")],
                    "Обади се: 0889 716 776")
        photo_banner(FN, f"out/banners/E5_nova_oferta_{tag}.jpg", W, H, .5, .4, "Всеки ден нещо ново на закачалките",
                     ["ОФЕРТА", "НА ДЕНЯ"], "Пуловери, якета, рокли · ела по-рано, бройките са малко")
    print("ok")
