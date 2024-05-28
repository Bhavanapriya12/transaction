from bullmq import Queue
import json
import asyncio

queue = Queue("myQueue", {"connection": "redis://127.0.0.1:6379"})

async def add(type,data,priority):
    try:
        data['type'] = type
        data_json = json.dumps(data)
        priority={"priority": priority, "removeOnComplete": True, "removeOnFail": True}
        # Add job to the queue
        r = await queue.add(type, data_json,priority)
        print('Queue add response:', r)
    except Exception as e:
        print("Error adding job to queue:", str(e))
