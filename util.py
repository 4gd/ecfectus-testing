import os
from dotenv import load_dotenv


load_dotenv()
API_URL = os.environ.get("API_URL")

def interp_to(current, target, dt, speed):
    if speed <= 0:
        return target
    dist = target - current
    if dist**2 < 1:
        return target
    # avoid overshoot - def not confusing in the slightest...
    if dist <= 0:
        dx = max(dt * -speed, dist)
    else:
        dx = min(dt * speed, dist)
    return current + dx


async def send_mutation(session, document, variables):
    """Send mutation via websocket and don't wait for reply

    Work around for the fact that ecfectus api doesn't respond to queries/mutations
    but gql library expects one
    """
    await session.fetch_and_validate(document)
    await session.transport._send_query(document, variable_values=variables)
