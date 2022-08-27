import typing

from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket
from .game import Game


class GameActions:
    """
    Type of action
    """
    CREATE = 'create'
    NEW = 'new'
    JOIN = 'join'
    CLOSE = 'close'
    MOVE = 'move'

    ITEMS = (
        'create',
        'new',
        'join',
        'close',
        'move',
    )

    CHOICES = (
        (CREATE, 'create'),
        (NEW, 'new'),
        (JOIN, 'join'),
        (CLOSE, 'close'),
        (MOVE, 'move'),
    )


class WSGame(WebSocketEndpoint):
    encoding = 'json'
    users = []
    games = []
    current_games = []

    async def create_game(self, ws: WebSocket) -> Game:
        game = await Game.create(ws, len(self.games) + 1)
        self.games.append(game)
        return game

    async def join_game(self, ws: WebSocket, number: int) -> Game:
        game = self.games.pop(number - 1)
        self.current_games.append(game)
        await game.join_player(ws)
        return game

    async def get_game(self, ws: WebSocket) -> Game:
        for game in self.current_games:
            if await game.check_player_ws(ws):
                return game

    async def move_game(self, ws: WebSocket) -> None:
        game = await self.get_game(ws)
        return await game.player_1.get_ws(), await game.player_2.get_ws()

    async def delete_game(self, ws: WebSocket) -> tuple:
        game = await self.get_game(ws)
        self.current_games.remove(game)
        pl1, pl2 = await game.player_1.get_ws(), await game.player_2.get_ws()
        del game
        return pl1, pl2

    async def add_user(self, ws: WebSocket) -> None:
        self.users.append(ws)

    async def delete_user(self, ws: WebSocket):
        self.users.pop(self.users.index(ws))

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await self.add_user(websocket)

    async def on_receive(self, websocket: WebSocket, data: typing.Any) -> None:
        if data['action'] in GameActions.ITEMS:
            if data['action'] == GameActions.NEW:
                await websocket.send_json(
                    {
                        'action': GameActions.NEW,
                        'games': len(self.games),
                    }
                )

            elif data['action'] == GameActions.CREATE:
                game = await self.create_game(websocket)
                await websocket.send_json(
                    {
                        'action': GameActions.CREATE,
                        'player': await game.player_1.get_state(),
                        'game_id': game.id,
                    }
                )
                await self.delete_user(websocket)

                for ws in self.users:
                    await ws.send_json(
                        {
                            'action': GameActions.NEW,
                            'games': len(self.games),
                        }
                    )

            elif data['action'] == GameActions.JOIN:
                number_of_game = int(data['game'])
                game = await self.join_game(websocket, number_of_game)
                await self.delete_user(websocket)

                await websocket.send_json(
                    {
                        'action': GameActions.JOIN,
                        'other_player': await game.player_1.get_state(),
                        'player': await game.player_2.get_state(),
                        'game_id': game.id,
                    }
                )

                ws = await game.player_1.get_ws()
                await ws.send_json(
                    {
                        'action': GameActions.JOIN,
                        'other_player': await game.player_2.get_state(),
                        'player': await game.player_1.get_state(),
                        'game_id': game.id,
                    }
                )

                for ws in self.users:
                    await ws.send_json(
                        {
                            'action': GameActions.NEW,
                            'games': len(self.games),
                        }
                    )

            elif data['action'] == GameActions.MOVE:
                players_ws = await self.move_game(websocket)
                for ws in players_ws:
                    ws.send_json(
                        {
                            'action': GameActions.MOVE,
                            'cell': data['cell'],
                            'move': True if ws == websocket else False,
                        }
                    )

            elif data['action'] == GameActions.CLOSE:
                await self.add_user(websocket)
                players_ws = await self.delete_game(websocket)
                for ws in players_ws:
                    await ws.send_json(
                        {
                            'action': GameActions.NEW,
                            'games': len(self.games),
                        }
                    )





    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        pass

