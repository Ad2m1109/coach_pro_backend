import redis.asyncio as redis
import json
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

class RedisNotifier:
    def __init__(self, host: str = None, port: int = None):
        self.host = host or os.environ.get("REDIS_HOST", "football-redis")
        self.port = port or int(os.environ.get("REDIS_PORT", 6379))
        self.redis = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            # Test connection
            await self.redis.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
            raise

    async def subscribe_to_analysis(self, analysis_id: str, callback):
        """
        Subscribe to segment notifications for a specific analysis.
        
        Args:
            analysis_id: The ID of the analysis run.
            callback: Async function to call with segment data.
        """
        if not self.redis:
            try:
                await self.connect()
            except Exception:
                return

        channel = f"analysis:{analysis_id}:segment"
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        
        logger.info(f"Subscribed to Redis channel: {channel}")
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await callback(data)
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid JSON on channel {channel}")
        except asyncio.CancelledError:
            logger.info(f"Subscription task for {analysis_id} cancelled.")
        except Exception as e:
            logger.error(f"Error in Redis subscription for {analysis_id}: {e}")
        finally:
            try:
                await pubsub.unsubscribe(channel)
                await pubsub.close()
            except Exception:
                pass
            logger.info(f"Cleaned up Redis subscription for {analysis_id}")
