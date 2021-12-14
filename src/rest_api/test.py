import asyncio


async def go():
    print('go started')
    await asyncio.sleep(2)
    print('go finished')
    return 42


async def fun():
    print('fun started')
    await asyncio.sleep(1)
    print('fun finished')
    return 'smth'


async def main():
    t = asyncio.create_task(go())
    t2 = asyncio.create_task(fun())
    print(await t2)
    print(await t)


if __name__ == '__main__':
    asyncio.run(main())
