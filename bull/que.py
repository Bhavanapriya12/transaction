from bullmq import Queue
import json
import asyncio
from routers.redis_function import redis
# "redis://redis-19175.c14.us-east-1-2.ec2.redns.redis-cloud.com:19175"
queue = Queue("myQueue")
async def add(type,data, priority):
    try:
        print(data)
        data['type'] = type
        print(data)
        print(data["type"])
        data= json.dumps(data)
        # priority={"priority": priority, "removeOnComplete": True, "removeOnFail": True}
        priority={"connection":"redis://red-cper8mtds78s73flic1g:6379","priority": priority, "removeOnComplete": True, "removeOnFail": True}
        # Add job to the queue
        r = await queue.add(type,data,priority)
        print('Queue add response:', r)
        return r
    except Exception as e:
        print("Error adding job to queue:", str(e))
