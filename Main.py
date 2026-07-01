import asyncio
import json
import os
from telethon import TelegramClient, events

# ===== ТВОИ ДАННЫЕ =====
api_id = 33973346
api_hash = 'b83236740f2e3081c2ef1180c58184eb'
ADMIN_ID = 7984872192
# ========================

session_file = 'my_session'
muted_file = 'muted_users.json'

if os.path.exists(muted_file):
    with open(muted_file, 'r') as f:
        muted_users = set(json.load(f))
else:
    muted_users = set()

client = TelegramClient(session_file, api_id, api_hash)

def save_muted():
    with open(muted_file, 'w') as f:
        json.dump(list(muted_users), f)

@client.on(events.NewMessage(pattern=r'^/mute', func=lambda e: e.is_private or e.is_group))
async def mute_handler(event):
    if event.sender_id != ADMIN_ID:
        await event.reply('⛔ У вас нет прав.')
        return
    parts = event.message.text.split()
    if len(parts) > 1:
        target_arg = parts[1].strip()
        if target_arg.isdigit():
            target = int(target_arg)
        else:
            if target_arg.startswith('@'):
                target_arg = target_arg[1:]
            try:
                entity = await client.get_entity(target_arg)
                target = entity.id
            except Exception:
                await event.reply('❌ Не удалось найти пользователя по username.')
                return
    else:
        if not event.message.reply_to_msg_id:
            await event.reply('❌ Ответь на сообщение человека или укажи username/ID.')
            return
        replied = await event.message.get_reply_message()
        if not replied:
            await event.reply('❌ Не удалось найти сообщение.')
            return
        target = replied.sender_id

    try:
        entity = await client.get_entity(target)
        name = entity.first_name or str(target)
    except:
        name = str(target)

    if target in muted_users:
        await event.reply(f'⚠️ {name} уже в муте.')
        return

    muted_users.add(target)
    save_muted()
    await event.reply(f'🔇 {name} замьючен. Сообщения будут удаляться.')

@client.on(events.NewMessage(pattern=r'^/unmute', func=lambda e: e.is_private or e.is_group))
async def unmute_handler(event):
    if event.sender_id != ADMIN_ID:
        await event.reply('⛔ У вас нет прав.')
        return
    parts = event.message.text.split()
    if len(parts) > 1:
        target_arg = parts[1].strip()
        if target_arg.isdigit():
            target = int(target_arg)
        else:
            if target_arg.startswith('@'):
                target_arg = target_arg[1:]
            try:
                entity = await client.get_entity(target_arg)
                target = entity.id
            except Exception:
                await event.reply('❌ Не удалось найти пользователя по username.')
                return
    else:
        if not event.message.reply_to_msg_id:
            await event.reply('❌ Ответь на сообщение человека или укажи username/ID.')
            return
        replied = await event.message.get_reply_message()
        if not replied:
            await event.reply('❌ Не удалось найти сообщение.')
            return
        target = replied.sender_id

    try:
        entity = await client.get_entity(target)
        name = entity.first_name or str(target)
    except:
        name = str(target)

    if target not in muted_users:
        await event.reply(f'⚠️ {name} не в муте.')
        return

    muted_users.remove(target)
    save_muted()
    await event.reply(f'🔊 {name} размьючен.')

@client.on(events.NewMessage(func=lambda e: e.is_private or e.is_group))
async def delete_muted(event):
    if event.message.out:
        return
    if event.sender_id in muted_users:
        try:
            await event.delete()
            print(f'🗑️ Удалено сообщение от {event.sender_id}')
        except Exception as e:
            print(f'⚠️ Ошибка удаления: {e}')

async def main():
    await client.start()
    print('✅ Telethon-скрипт запущен.')
    print('📌 Команды: /mute [@username или ID] (или ответом на сообщение)')
    print('📌 /unmute [@username или ID] (или ответом на сообщение)')
    print('🔒 Только админ может использовать команды.')
    print('👥 Поддерживаются личные чаты и группы.')
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
