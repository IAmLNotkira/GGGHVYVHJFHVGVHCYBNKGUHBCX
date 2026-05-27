import minecraft_launcher_lib


def login_microsoft(game_dir):
    auth = minecraft_launcher_lib.microsoft_account.get_microsoft_account(
        game_dir
    )

    return {
        "username": auth["name"],
        "uuid": auth["id"],
        "token": auth["access_token"]
    }