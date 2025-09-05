import asyncio
import pprint
import rusty_req
from faker import Faker


async def single_request_example():
    """Demonstrates how to use fetch_single for a POST request."""
    print("🚀 Fetching a single POST request to httpbin.org...")

    # Enable debug mode to see detailed logs in the console
    rusty_req.set_debug(True)
    fake_zh = Faker('zh_CN')
    param = {
        "name": fake_zh.name(),
        "description":fake_zh.text(),
        "price": fake_zh.random_int(min=1, max=100),
        "is_offer": fake_zh.boolean()
    }
    response = await rusty_req.fetch_single(
        url="http://127.0.0.1:8000/api/v1/items/",
        method="POST",
        params=param,
        headers={"X-Client-Version": "1.0"},
        tag="my-single-post"
    )

    print("\n✅ Request finished. Response:")
    pprint.pprint(response)

if __name__ == "__main__":
    asyncio.run(single_request_example())
