from redis.asyncio import Redis
from typing import Optional


redis = Redis(host="localhost", port=6379, decode_responses=True)
 
async def set_user_in_redis(user_id: str, user_data: dict):
    await redis.hmset(user_id, mapping=user_data)

async def get_user_from_redis(user_id: str) -> Optional[dict]:
    user_data = await redis.hgetall(user_id)
    return user_data if user_data else None

async def delete_user_from_redis(user_id: str):
    await redis.delete(user_id)

async def user_exists_in_redis(user_id: str) -> bool:
    return await redis.exists(user_id)
