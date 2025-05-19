import asyncio
import logging
from typing import Dict, Set
from app.websocket.game.multi.multi_game_loop import MultiGameLoop

class MultiGameManager:
    def __init__(self):
        self.active_games: Dict[str, MultiGameLoop] = {}  # game_id -> MultiGameLoop
        logging.info(f"[MultiGameManager] Initializing")
        self.player_games: Dict[str, str] = {}  # user_id -> game_id
        self.ready_players: Set[str] = set()  # ready한 플레이어들
        self.lock = asyncio.Lock()
        self.running = False
        self.manager_task = None

    async def start(self):
        """멀티게임 매니저 시작"""
        self.running = True
        logging.info("[MultiGameManager] Started")
        # 필요한 초기화 작업 수행
        self.active_games.clear()
        self.player_games.clear()
        self.ready_players.clear()

    async def stop(self):
        """멀티게임 매니저 중지"""
        self.running = False
        # 모든 게임 종료
        for game_id in list(self.active_games.keys()):
            await self.end_game(game_id)
        logging.info("[MultiGameManager] Stopped")

    async def add_ready_player(self, user_id: str) -> bool:
        """플레이어를 ready 상태로 추가하고, 모든 플레이어가 준비되었는지 확인"""
        async with self.lock:
            self.ready_players.add(user_id)
            # TODO: 실제 게임에서는 여기서 모든 플레이어가 준비되었는지 확인하는 로직 추가
            return len(self.ready_players) >= 2  # 예시로 2명 이상이면 시작

    async def start_game(self, players: list) -> str:
        """새로운 멀티게임을 시작"""
        self.start()
        if not self.running:
            logging.error("[MultiGameManager] Cannot start game - manager is not running")
            return None
        
        logging.info(f"[MultiGameManager] Starting game with players: {players}")
        
        return  f"game_multigame"
        
        async with self.lock:
            game_id = f"game_{len(self.active_games)}"
            game_loop = MultiGameLoop(game_id, players)
            game_loop.set_manager(self)  # Set this manager instance
            self.active_games[game_id] = game_loop
            
            # 플레이어들을 게임에 연결
            for player in players:
                self.player_games[player['user']] = game_id
            
            # 게임 루프 시작
            asyncio.create_task(game_loop.run())
            logging.info(f"[MultiGameManager] Started new game: {game_id} with players: {[p['user'] for p in players]}")
            
            return game_id

    async def remove_player(self, user_id: str):
        """플레이어를 게임에서 제거"""
        async with self.lock:
            if user_id in self.ready_players:
                self.ready_players.remove(user_id)
            
            if user_id in self.player_games:
                game_id = self.player_games[user_id]
                if game_id in self.active_games:
                    game = self.active_games[game_id]
                    await game.remove_player(user_id)
                    if game.is_empty():
                        await self.end_game(game_id)
                del self.player_games[user_id]

    async def end_game(self, game_id: str):
        """게임 종료 및 정리"""
        async with self.lock:
            if game_id in self.active_games:
                game = self.active_games[game_id]
                await game.cleanup()
                del self.active_games[game_id]
                # 관련된 플레이어들 정리
                for user_id, gid in list(self.player_games.items()):
                    if gid == game_id:
                        del self.player_games[user_id]
                logging.info(f"[MultiGameManager] Ended game: {game_id}")

    def get_game(self, user_id: str) -> MultiGameLoop:
        """플레이어의 게임 루프 반환"""
        game_id = self.player_games.get(user_id)
        return self.active_games.get(game_id) if game_id else None

    async def send_to_player(self, user_id: str, message: dict):
        """플레이어에게 메시지 전송"""
        game = self.get_game(user_id)
        if game:
            # TODO: 실제 웹소켓 연결을 통해 메시지 전송
            # 현재는 로깅만 수행
            logging.debug(f"[MultiGameManager] Sending message to {user_id}: {message}")

    async def broadcast(self, message: dict):
        """모든 플레이어에게 메시지 브로드캐스트"""
        for user_id in self.player_games.keys():
            await self.send_to_player(user_id, message)

multi_game_manager = MultiGameManager()