import time
import requests

# ==========================================================
# ⚙️ CONFIGURACIÓN DEL RADAR WALLAPOPED
# ==========================================================
TELEGRAM_TOKEN = "8862830996:AAF52_KGwAZwoWzmOwG6Ku4yW38ZlcE4VUo"
TELEGRAM_CHAT_ID = "-1004329396328"

# Lista de todas las consolas a rastrear y su precio tope de chollo en €
CONSOLAS_OBJETIVO = [
    {"termino": "Nintendo DS", "max_precio": 35},
    {"termino": "Nintendo DSi XL", "max_precio": 55},
    {"termino": "Nintendo 2DS", "max_precio": 50},
    {"termino": "New Nintendo 2DS XL", "max_precio": 120},
    {"termino": "Nintendo 3DS", "max_precio": 70},
    {"termino": "Nintendo 3DS XL", "max_precio": 110},
    {"termino": "New Nintendo 3DS", "max_precio": 130},
    {"termino": "New Nintendo 3DS XL", "max_precio": 160},
]

INTERVALO_ENTRE_CONSULTAS = 8  # segundos entre cada consola para evitar bloqueos
# ==========================================================

anuncios_vistos = set()

def enviar_telegram(mensaje, foto_url=None):
    """Envía la alerta al grupo de Telegram."""
    if foto_url:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            res = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "caption": mensaje, "parse_mode": "HTML"}, json={"photo": foto_url}, timeout=10)
            if res.status_code == 200:
                return
        except Exception:
            pass

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Error Telegram: {e}")

def buscar_chollo(termino, max_precio):
    """Realiza la búsqueda con cabeceras completas de navegador para evitar el error 403."""
    url = "https://api.wallapop.com/api/v3/general/search"
    params = {
        "keywords": termino,
        "max_sale_price": max_precio,
        "order_by": "newest"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8,fr;q=0.7,it;q=0.6",
        "Origin": "https://es.wallapop.com",
        "Referer": "https://es.wallapop.com/",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "X-DeviceOS": "0"
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=12)
        if r.status_code == 200:
            items = r.json().get("search_objects", [])
            for item in items:
                item_id = item.get("id")
                if not item_id or item_id in anuncios_vistos:
                    continue

                anuncios_vistos.add(item_id)
                titulo = item.get("title", "Sin título")
                precio = item.get("price", 0)
                slug = item.get("web_slug", "")
                link = f"https://es.wallapop.com/item/{slug}" if slug else "https://es.wallapop.com"
                img = item.get("images", [{}])[0].get("original")

                mensaje = (
                    f"🔥 <b>¡CHOLLO DETECTADO!</b>\n\n"
                    f"🎯 <b>Búsqueda:</b> {termino}\n"
                    f"🕹️ <b>Título:</b> {titulo}\n"
                    f"💶 <b>Precio:</b> {precio} €\n\n"
                    f"🔗 <a href='{link}'>Ver en Wallapop</a>"
                )
                print(f"✅ Notificando: {titulo} ({precio}€)")
                enviar_telegram(mensaje, img)
        elif r.status_code == 403:
            print(f"⚠️ Wallapop 403 temporal para '{termino}'. Pasando a la siguiente...")
        else:
            print(f"Respuesta {r.status_code} para {termino}")
    except Exception as err:
        print(f"Error escaneando {termino}: {err}")

if __name__ == "__main__":
    print("📡 Radar Wallapoped activado para toda la gama Nintendo DS / 3DS")
    enviar_telegram("🚀 <b>Radar Wallapoped Activo 24/7</b>\nMonitoreando toda la gama Nintendo DS / 2DS / 3DS.")

    while True:
        for consola in CONSOLAS_OBJETIVO:
            buscar_chollo(consola["termino"], consola["max_precio"])
            time.sleep(INTERVALO_ENTRE_CONSULTAS)
        time.sleep(20)  # pausa antes de reiniciar la ronda