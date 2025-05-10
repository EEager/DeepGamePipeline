from typing import List, Dict, Type, Self
from objects.base_object import BaseObject
import pygame

class ObjectManager:
    _instance: Self | None = None

    def __new__(cls):
        raise RuntimeError("Use ObjectManager.get_instance() instead.")

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.__init__()  
            cls._instance = instance
        return cls._instance

    def __init__(self):
        self.objects: Dict[str, List[BaseObject]] = {
            "player": [],
            "boss": [],
            "bullet": [],
            "heal_item": []
        }

    def add_object(self, obj: BaseObject, object_type: str = None) -> None:
        """게임 오브젝트 추가"""
        obj_type = object_type if object_type else obj.object_type
        if obj_type in self.objects:
            self.objects[obj_type].append(obj)

    def remove_object(self, obj: BaseObject) -> None:
        """게임 오브젝트 제거"""
        if obj.object_type in self.objects and obj in self.objects[obj.object_type]:
            self.objects[obj.object_type].remove(obj)

    def get_objects(self, object_type: str) -> List[BaseObject]:
        """특정 타입의 모든 오브젝트 반환"""
        return self.objects.get(object_type, [])

    def update(self, delta_time: float) -> None:
        """모든 오브젝트 업데이트"""
        for object_list in self.objects.values():
            for obj in object_list[:]:  # 복사본으로 순회
                if obj.active:
                    obj.update(delta_time)
                    # 화면 밖으로 나간 오브젝트 제거
                    if obj.is_out_of_screen():
                        self.remove_object(obj)

    def render(self, screen: pygame.Surface) -> None:
        """모든 오브젝트 렌더링"""
        for object_list in self.objects.values():
            for obj in object_list:
                if obj.active:
                    obj.render(screen)

    def check_collisions(self) -> None:
        """충돌 체크"""
        # 플레이어와 보스 충돌
        for player in self.objects["player"]:
            for boss in self.objects["boss"]:
                if player.get_rect().colliderect(boss.get_rect()):
                    # 충돌 처리 로직
                    player.take_damage(1)
                    boss.take_damage(1)

        # 총알과 오브젝트 충돌
        for bullet in self.objects["bullet"][:]:
            # 플레이어 총알과 보스 충돌
            if bullet.owner == "player":
                for boss in self.objects["boss"]:
                    if bullet.get_rect().colliderect(boss.get_rect()):
                        boss.take_damage(1)
                        self.remove_object(bullet)
                        break
            # 보스 총알과 플레이어 충돌
            elif bullet.owner in ("boss", "boss_homing"):
                for player in self.objects["player"]:
                    if bullet.get_rect().colliderect(player.get_rect()):
                        player.take_damage(1)
                        self.remove_object(bullet)
                        break

        # 힐 아이템과 플레이어 충돌
        for heal in self.objects["heal_item"][:]:
            for player in self.objects["player"]:
                if heal.get_rect().colliderect(player.get_rect()):
                    player.heal(1)
                    self.remove_object(heal) 