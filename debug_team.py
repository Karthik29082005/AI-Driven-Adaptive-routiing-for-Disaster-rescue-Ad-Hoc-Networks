from auth import login_user
from admin_user_mgmt import get_team_members

user = login_user("team1@gmail.com", "team123")
print("Login result:", user)
print("Team Members:", get_team_members())
