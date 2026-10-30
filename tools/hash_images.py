"""Добавляет хэш содержимого к именам картинок в img/ и обновляет ссылки в *.html.
Нужно потому, что /img/* кэшируется на неделю (vercel.json): замена фото под тем же
именем не видна посетителям. Запуск после любого добавления/замены фото:
    python3 tools/hash_images.py
Новое фото кладите под обычным именем (img/hero.jpg) - скрипт сам переименует его
и удалит предыдущую хэшированную версию с тем же базовым именем."""
import hashlib, pathlib, re
root = pathlib.Path(__file__).resolve().parent.parent
pat = re.compile(r'^(?P<stem>.+)\.(?P<h>[0-9a-f]{8})$')
htmls = list(root.glob('*.html'))
texts = {p: p.read_text(encoding='utf-8') for p in htmls}
for f in sorted((root / 'img').rglob('*')):
    if not f.is_file() or pat.match(f.stem):
        continue
    h = hashlib.md5(f.read_bytes()).hexdigest()[:8]
    new = f.with_name(f'{f.stem}.{h}{f.suffix}')
    old_rel = f.relative_to(root).as_posix()
    # старые хэшированные версии того же файла
    olds = [o for o in f.parent.glob(f'{f.stem}.*{f.suffix}') if o != f and pat.match(o.stem) and pat.match(o.stem)['stem'] == f.stem]
    f.rename(new)
    new_rel = new.relative_to(root).as_posix()
    for p in texts:
        t = texts[p].replace(old_rel, new_rel)
        for o in olds:
            t = t.replace(o.relative_to(root).as_posix(), new_rel)
        texts[p] = t
    for o in olds:
        if o != new: o.unlink()
    print(old_rel, '->', new_rel)
for p, t in texts.items():
    p.write_text(t, encoding='utf-8')
missing = sorted({m for t in texts.values() for m in re.findall(r'img/[\w./-]+\.(?:jpg|png|webp)', t) if not (root / m).exists()})
print('битые ссылки:', missing or 'нет')
