def process_event(event_type, details):
    # 예시: 이동, 공격, 힐 등 처리
    if event_type == "move":
        # 위치 갱신 로직
        return {"type": "move_result", "details": details}
    elif event_type == "logs_attack":
        # 딜량 계산 등
        return {"type": "attack_result", "details": details}
    elif event_type == "logs_heal":
        # 힐 처리
        return {"type": "heal_result", "details": details}
    else:
        return {"type": "unknown_event", "details": details}