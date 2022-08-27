from starlette.websockets import WebSocket


class Player:

    def __init__(self, ws: WebSocket, state: str = 'X') -> None:
        self.__ws = ws
        self.__state = state

    async def get_state(self):
        return self.__state

    async def get_ws(self):
        return self.__ws

    async def check_ws(self, ws: WebSocket) -> bool:
        return ws == self.__ws


class Game:

    id = 0
    player_1 = None
    player_2 = None
    current_player = ''
    active_game = False

    @classmethod
    async def create(cls, ws: WebSocket, game_id: int):
        self = cls()
        self.id = game_id
        player = await self.create_player(ws)
        self.player_1 = player
        self.current_player = await player.get_state()
        return self

    async def create_player(self, ws: WebSocket) -> Player:
        return Player(ws, 'X')

    async def join_player(self, ws: WebSocket):
        player = Player(ws, 'O')
        if player != self.player_1 and player != self.player_2:
            self.player_2 = player
            self.active_game = True

    async def check_player_ws(self, ws: WebSocket) -> bool:
        return await self.player_1.check_ws(ws) or await self.player_2.check_ws(ws)

