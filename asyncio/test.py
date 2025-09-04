import asyncio

async def say_hello(name, delay):
    await asyncio.sleep(delay)
    print(f"Hello, {name}!")

async def main():
    await asyncio.gather(
        say_hello("Alice", 2),
        say_hello("Bob", 1)
    )

asyncio.run(main())