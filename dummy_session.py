"""
Dummy session with 4 soldiers, 2 targets, drone

Soldiers patrol back and forth on edge of area at varying speeds
Target1 rotates back and forth
Target2 is a flip target that subscribes to hit detection
Subcribed to recevie drone positions

NB: 
- Currently all framework stuff is in one file, can split out if ever make more
test scripts.
- A lot of the stuff is hardcoded atm, should be getting all info from session
query ideally.
"""
import asyncio
import logging
import math
import random
import sys
import time
import uuid
from collections import namedtuple
from datetime import datetime
from pprint import pformat

from gql import Client, WebsocketsTransport, AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from gql.transport.websockets import log as websocket_logger

from documents import *
from util import API_URL, interp_to, send_mutation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
websocket_logger.setLevel(level=logging.WARNING)

Vec2 = namedtuple('Vec2', ['x', 'y'])
MIN_POS = Vec2(80, 80)  # @HARDCODE
MAX_POS = Vec2(1240, 760)  # @HARDCODE
UPDATE_FREQUENCY = 5.0  # Hz


class Entity:
    def __init__(self, id_):
        self.id_ = id_

    def __repr__(self):
        return f'<{type(self).__name__}: {self.id_}>'


class Target(Entity):
    document = update_target

    def __init__(self, id_, flip=False, twist=None, target_twist=None):
        super().__init__(id_)
        self.twist = twist if twist else random.randint(0, 360)  # [0, 360)
        self.flip = flip
        self.target_twist = target_twist if target_twist else 0
        self.twist_rate = 25  # degrees / sec

    def update(self, dt):
        if self.flip:
            return None
        if self.target_twist == self.twist:
            self.target_twist = 0 if self.twist == 2 * math.pi else 2 * math.pi
        self.twist = interp_to(self.twist, self.target_twist, dt, self.twist_rate)

        output = {}
        measurement_id = str(uuid.uuid4())
        measurement_time = datetime.utcnow().isoformat() + "Z"
        deviceId = self.id_
        states = ["Idle", "Alert", "Attacking", "Killed"]

        output["targetTwist"] = {
            "actuationId": measurement_id,
            "time": measurement_time,
            "deviceId": self.id_,
            "radians": math.radians(self.twist)
        }
        output["targetOrientation"] = {
            "measurementId": measurement_id,
            "time": measurement_time,
            "deviceId": deviceId,
            "radians": math.radians(self.twist)
        }
        if random.randint(0, 100) < 20:
            output["targetHitDetection"] = {
                "measurementId": measurement_id,
                "time": measurement_time,
                "deviceId": deviceId,
                "zone": random.randint(1, 5)
            }
        if random.randint(0, 100) < 5:
            output["targetStateChange"] = {
                "measurementId": measurement_id,
                "time": measurement_time,
                "deviceId": deviceId,
                "state": states[random.randint(0, 3)]
            }

        return output


class Soldier(Entity):
    document = update_soldier
    # @HARDCODED
    username_to_wearable_id = {
        "frodo": "warpac1",
        "sam": "warpac2",
        "merry": "warpac3",
        "pippin": "warpac4"
    }

    def __init__(self, username, pos, vel):
        super().__init__(username)
        self.username = username  # duplicated with id
        self.pos = Vec2(*pos)
        self.vel = Vec2(*vel)
        self.head_position = random.randint(0, 360)  # [0, 360) world space
        self.head_target_position = 0
        self.head_speed = 50  # degrees / sec
        
        self.gun_pitch_yaw = Vec2(random.uniform(-90, 90), random.uniform(-180, 180))

    def update(self, dt):
        """Update state and return new mutation variables"""
        # If devices have differnt update rates will want to split this stuff out
        # This will break if initital position outside of limits
        x = self.pos.x + self.vel.x * dt
        vx, vy = self.vel
        if x > MAX_POS.x:
            x = MAX_POS.x - (x - MAX_POS.x)
            vx = -abs(vx)
        elif x < MIN_POS.x:
            x = MIN_POS.x + (MIN_POS.x - x)
            vx = abs(vx)
        y = self.pos.y + self.vel.y * dt
        if y > MAX_POS.y:
            y = MAX_POS.y - (y - MAX_POS.y)
            vy = -abs(vy)
        elif y < MIN_POS.y:
            y = MIN_POS.y + (MIN_POS.y - y)
            vy = abs(vy)
        self.pos = Vec2(x, y)
        self.vel = Vec2(vx, vy)

        if self.head_target_position == self.head_position:
            self.head_target_position = 0 if self.head_position == 360 else 360
        self.head_position = interp_to(self.head_position, self.head_target_position, dt, self.head_speed)

        new_pitch = 60 * math.sin(time.time())
        new_yaw = 45 * math.sin(time.time()) + self.head_position
        self.gun_pitch_yaw = Vec2(new_pitch, new_yaw)

        output = {}
        measurement_id = str(uuid.uuid4())
        measurement_time = datetime.utcnow().isoformat() + "Z"
        deviceId = self.username_to_wearable_id[self.username]

        output["soldierPosition"] = {
            "measurementId": measurement_id,
            "time": measurement_time,
            "deviceId": deviceId + ".pozyx",
            "x": self.pos.x * 10,  # convert to mm - should probs just do simulation in mm
            "y": self.pos.y * 10,
            "z": 0
        }
        output["headOrientation"] = {
            "measurementId": measurement_id,
            "time": measurement_time,
            "deviceId": deviceId + ".pupil",
            "radians": math.radians(self.head_position)
        }
        output["gazeDirection"] = {
            "measurementId": measurement_id,
            "time": measurement_time,
            "deviceId": deviceId + ".pupil",
            "x": random.randint(0, 1088),
            "y": random.randint(0, 1080)
        }
        output["instantaneousHeartRate"] = {
            "measurementId": measurement_id,
            "time": measurement_time,
            "deviceId": deviceId + ".bodytrak",
            "hr": random.randint(69, 100)
        }
        output["coreBodyTemperature"] = {
            "measurementId": measurement_id,
            "time": measurement_time,
            "deviceId": deviceId + ".bodytrak",
            "cbt": random.randint(36, 39)
        }
        output["gunOrientation"] = {
            "measurementId": measurement_id,
            "time": measurement_time,
            "deviceId": deviceId + ".arcm4",
            "radians": math.radians(self.gun_pitch_yaw[1])
        }
        if random.randint(0, 100) < 20:
            output["dischargeDetection"] = {
                "measurementId": measurement_id,
                "time": measurement_time,
                "deviceId": deviceId + ".arcm4"
            }

        return output


async def handle_subscriptions(session):
    logger.info("Listening for subscriptions")
    async for result in session.subscribe(subscriptions):
        logger.info(f'<-- {result}')


async def handle_entities(session):
    # @TODO create from session info
    frodo = Soldier("frodo", MIN_POS, (100, 0))
    pippin = Soldier("pippin", Vec2(MIN_POS.x, MAX_POS.y), (0, 200))
    sam = Soldier("sam", MAX_POS, (-300, 0))
    merry = Soldier("merry", Vec2(MAX_POS.x, MIN_POS.y), (0, -400))
    target_1 = Target("target1")
    target_2 = Target("target2", flip=True)
    entities = [frodo, sam, merry, pippin, target_1, target_2]
    logger.info(f'Updating entity info for: {entities}')
    dt = 1 / UPDATE_FREQUENCY

    async def update():
        for entity in entities:
            variables = entity.update(dt)
            if variables is None:
                continue
            await send_mutation(session, entity.document, variables)

    while True:
        await asyncio.sleep(dt)
        asyncio.create_task(update())


async def main():
    # Set up required api stuff via http
    transport = AIOHTTPTransport(url=API_URL)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    async with client as session:
        logger.info("Checking for currenlty running session")
        result = await session.execute(get_sessions)
        logger.debug(f'<-- {pformat(result)}')
        prev_session_id = None if not result["sessions"] else result["sessions"][0]["sessionId"]
        if prev_session_id:
            logger.info(f'Found previous session with ID: {prev_session_id}, ending it')
            variables = {"sessionId": prev_session_id}
            result = await session.execute(end_session, variables)
            logger.debug(f"<-- {pformat(result)}")
        new_session_id = str(uuid.uuid4())
        logger.info(f'Creating new session with ID: {new_session_id}')
        result = await session.execute(create_all_and_start_session,
                                       variable_values={"sessionId": new_session_id})
        logger.debug(f'<-- {pformat(result)}')

    # Connect via websocket to handle real time mutations/subscriptions
    # NB API doesnt respond to messages sent via websocket. Maybe this is just normal?
    # Either way it's probably fine as errors should still be thrown
    transport = WebsocketsTransport(url=API_URL)
    client = Client(transport=transport, fetch_schema_from_transport=False)
    async with client as session:
        # await asyncio.gather(
        #     handle_subscriptions(session),
        #     handle_soldiers(session),
        #     return_exceptions=False
        # )
        asyncio.create_task(handle_entities(session))
        await handle_subscriptions(session)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        UPDATE_FREQUENCY = float(sys.argv[1])
        logger.info(f'Update frequency overriden. New : {UPDATE_FREQUENCY}')
    asyncio.run(main())
