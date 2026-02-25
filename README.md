# 🐍 Serpens

> *Serpens, Latince'de yılan anlamına gelir ve gökyüzündeki tek ikiye bölünmüş takımyıldızının adıdır — Ophiuchus (Yılancı) tarafından Serpens Caput (yılanın başı) ve Serpens Cauda (yılanın kuyruğu) olarak ikiye ayrılır.*

Klasik yılan oyununun 5 levelli versiyonu. Her level yeni bir zorluk getirir.

## Kurulum

Python ve pygame yüklü olmalı:

```bash
pip install pygame
python serpens_game.py
```

## Nasıl Oynanır

| Tuş | Hareket |
|-----|---------|
| ← → ↑ ↓ | Yılanı yönlendir |
| Sol Shift | Hızlan |

Yemi topla, leveli tamamla. Duvara veya kendi gövdene çarparsan oyun biter.

## Levellar

| Level | Hedef | Özellik |
|-------|-------|---------|
| 1 | 15 yiyecek | Klasik oyun |
| 2 | 10 yiyecek | Daha hızlı yılan |
| 3 | 5 yiyecek | Engeller |
| 4 | 3 yiyecek | Engeller + hareketli yem |
| 5 | 1 yiyecek | Çok hızlı hareketli yem |

Her level geçişinde yılanın boyutu sıfırlanır. İlerleme `checkpoint.json` dosyasına kaydedilir, aynı isimle girince kaldığın yerden devam edebilirsin.

## Gereksinimler

- Python 3.x
- pygame
- PressStart2P-Regular.ttf (repoda mevcut)
