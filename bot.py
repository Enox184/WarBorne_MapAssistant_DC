import discord
from discord import app_commands
from discord.ext import commands
import datetime
import json

import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)
client.map_times = {}

SUROWCE = [
    "small scrap post", "medium scrap post", "big scrap post",
    "green orb", "blue orb", "purple orb", "gold orb",
    "green chest", "blue chest", "purple chest", "gold chest",
    "scrap iron", "resin"
]

DATA_FILE = "map_data.json"

# ---------- Pomocnicze funkcje ----------

def format_time(delta):
    minutes, seconds = divmod(int(delta.total_seconds()), 60)
    return f"{minutes:02}:{seconds:02}"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            client.map_times = json.load(f)
    except FileNotFoundError:
        client.map_times = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(client.map_times, f)

client.save_data = save_data
client.load_data = load_data



# ---------- Komenda /regentimer ----------

@client.tree.command(name="regentimer", description="Ustaw timer dla konkretnego kontentu na mapie")
@app_commands.describe(mapa="Nazwa mapy", czas="Czas w minutach", kontent="Typ kontentu")
async def regentimer(interaction: discord.Interaction, mapa: str, czas: int, kontent: str):
    now = datetime.datetime.utcnow().isoformat()

    # Zmieniamy czas na sekundy (czas był podawany w minutach, więc przeliczamy na sekundy)
    czas_w_sekundach = czas * 60

    if mapa not in client.map_times:
        client.map_times[mapa] = []

    client.map_times[mapa].append({
        "surowiec": kontent,
        "czas": czas_w_sekundach,
        "start": now
    })

    client.save_data()

    await interaction.response.send_message(
        f"⏱️ Ustawiono timer dla **{kontent}** na mapie **{mapa}** ({czas} minut)"
    )



# ---------- Autouzupełnianie do /regentimer ----------
@regentimer.autocomplete("mapa")
async def regentimer_mapa_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=mapa, value=mapa)
        for mapa in client.map_times.keys()
        if current.lower() in mapa.lower()
    ]

@regentimer.autocomplete("kontent")
async def regentimer_kontent_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=kontent, value=kontent)
        for kontent in SUROWCE if current.lower() in kontent.lower()
    ]



# ---------- Komenda /droplist ----------
@client.tree.command(name="droplist", description="Wyświetl informacje o dostępnych timerach")
@app_commands.describe(type="Wybierz widok: bymap / kontent list")
async def droplist(interaction: discord.Interaction, type: str):
    now = datetime.datetime.utcnow()
    to_remove = []

    if type == "bymap":
        result = ""
        for mapa, entries in client.map_times.items():
            result += f"**{mapa}**\n"
            for entry in entries:
                start = datetime.datetime.fromisoformat(entry["start"])
                delta = datetime.timedelta(seconds=entry["czas"])
                end = start + delta
                remaining = end - now

                if remaining.total_seconds() > 0:
                    minutes = int(remaining.total_seconds() // 60)
                    seconds = int(remaining.total_seconds() % 60)
                    result += f"🟢 {entry['surowiec']} – {minutes}:{seconds:02}\n"
                else:
                    elapsed = abs(remaining.total_seconds())
                    if elapsed <= 300:
                        minutes = int(elapsed // 60)
                        seconds = int(elapsed % 60)
                        result += f"⚪ {entry['surowiec']} – -{minutes}:{seconds:02}\n"
                    else:
                        to_remove.append((mapa, entry))  # oznacz do usunięcia
            result += "\n"

        # usuń tylko przeterminowane kontenty, nie całą mapę
        for mapa, entry in to_remove:
            if mapa in client.map_times:
                if entry in client.map_times[mapa]:
                    client.map_times[mapa].remove(entry)
                if not client.map_times[mapa]:
                    del client.map_times[mapa]

        client.save_data()
        await interaction.response.send_message(result or "Brak danych.")

    elif type == "kontent list":
        kontenty = {}
        for mapa, entries in client.map_times.items():
            for entry in entries:
                start = datetime.datetime.fromisoformat(entry["start"])
                delta = datetime.timedelta(seconds=entry["czas"])
                end = start + delta
                remaining = end - now

                if remaining.total_seconds() > 0:
                    minutes = int(remaining.total_seconds() // 60)
                    seconds = int(remaining.total_seconds() % 60)
                    time_str = f"{minutes}:{seconds:02}"
                else:
                    elapsed = abs(remaining.total_seconds())
                    if elapsed <= 300:
                        minutes = int(elapsed // 60)
                        seconds = int(elapsed % 60)
                        time_str = f"-{minutes}:{seconds:02}"
                    else:
                        to_remove.append((mapa, entry))
                        continue

                kontenty.setdefault(entry["surowiec"], []).append(f"{mapa} – {time_str}")

        for mapa, entry in to_remove:
            if mapa in client.map_times:
                if entry in client.map_times[mapa]:
                    client.map_times[mapa].remove(entry)
                if not client.map_times[mapa]:
                    del client.map_times[mapa]

        client.save_data()

        if not kontenty:
            await interaction.response.send_message("Brak danych.")
            return

        result = ""
        for surowiec, miejsca in kontenty.items():
            result += f"**{surowiec}**\n"
            for line in miejsca:
                result += f"🗺️ {line}\n"
            result += "\n"

        await interaction.response.send_message(result)

    else:
        await interaction.response.send_message("Nieznany typ widoku.")



# ---------- Komenda /clear ----------

@client.tree.command(name="clear", description="Usuń konkretny kontent z danej mapy")
@app_commands.describe(mapa="Nazwa mapy", kontent="Nazwa kontentu do usunięcia")
async def clear(interaction: discord.Interaction, mapa: str, kontent: str):
    if mapa not in client.map_times:
        await interaction.response.send_message(f"❌ Mapa **{mapa}** nie istnieje!")
        return

    kontenty = client.map_times[mapa]
    kontenty_po_usunieciu = [k for k in kontenty if k["surowiec"] != kontent]

    if len(kontenty) == len(kontenty_po_usunieciu):
        await interaction.response.send_message(f"❌ Nie znaleziono kontentu **{kontent}** na mapie **{mapa}**.")
        return

    client.map_times[mapa] = kontenty_po_usunieciu

    if not client.map_times[mapa]:
        del client.map_times[mapa]

    client.save_data()
    await interaction.response.send_message(f"🗑️ Usunięto kontent **{kontent}** z mapy **{mapa}**.")




# ---------- Autouzupełnianie do /clear ----------

@clear.autocomplete("mapa")
async def clear_mapa_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=mapa, value=mapa)
        for mapa in client.map_times.keys()
        if current.lower() in mapa.lower()
    ]

@clear.autocomplete("kontent")
async def clear_kontent_autocomplete(interaction: discord.Interaction, current: str):
    mapa = interaction.namespace.mapa
    kontenty = []

    if mapa in client.map_times:
        kontenty = list({entry["surowiec"] for entry in client.map_times[mapa]})

    return [
        app_commands.Choice(name=surowiec, value=surowiec)
        for surowiec in kontenty
        if current.lower() in surowiec.lower()
    ]




#--------- Autouzupełnianie do /droplist ----------

@droplist.autocomplete("type")
async def droplist_type_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name="bymap", value="bymap"),
        app_commands.Choice(name="kontent list", value="kontent list"),
    ]




# ---------- Start bota ----------

@client.event
async def on_ready():
    print(f"Zalogowano jako {client.user}")
    client.load_data()
    try:
        synced = await client.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend.")
    except Exception as e:
        print(f"Błąd synchronizacji: {e}")

if __name__ == '__main__':
    if not DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not found in environment variables!")
        print("Please set your Discord bot token in the environment variables.")
    else:
        client.run(DISCORD_TOKEN)