from redis.asyncio import Redis
from typing import Optional


redis = Redis(host="localhost", port=6379, decode_responses=True)

# redis = Redis(
#   host='redis-19175.c14.us-east-1-2.ec2.redns.redis-cloud.com',
#   port=19175,
#   password='SUgs1JXtonLW8gV35QmNCNSOfKDq00gt')
# redis=Redis(host="red-cper8mtds78s73flic1g",port=6379)
 
async def set_user_in_redis(user_id: str, user_data: dict):
    await redis.hmset(user_id, mapping=user_data)

async def get_user_from_redis(user_id: str) -> Optional[dict]:
    user_data = await redis.hgetall(user_id)
    return user_data if user_data else None

async def delete_user_from_redis(user_id: str):
    await redis.delete(user_id)

async def user_exists_in_redis(user_id: str) -> bool:
    return await redis.exists(user_id)
