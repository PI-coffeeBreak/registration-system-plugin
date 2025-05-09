def get_user_id(user: dict) -> str:
    return user.get("sub")