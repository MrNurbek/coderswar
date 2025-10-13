





import instaloader
from getpass import getpass

# 1. Instaloader obyektini yaratish
L = instaloader.Instaloader()

# 2. Login
username = "_x_a_m_r_a_y_e_v_"
password = "Nurbeknurbek2"
L.login(username, password)

# 3. Profil olish
profile = instaloader.Profile.from_username(L.context, username)

# 4. Followers va Following ro‘yxatlari
followers = set()
followees = set()

print("Followersni yuklayapti...")
for follower in profile.get_followers():
    followers.add(follower.username)

print("Followingni yuklayapti...")
for followee in profile.get_followees():
    followees.add(followee.username)

# 5. Faqat sizga obuna bo‘lganlar
not_followed_back = followers - followees

# 6. Natijani chiqarish
print(f"\nSizga obuna bo‘lgan, lekin siz obuna bo‘lmagan foydalanuvchilar soni: {len(not_followed_back)}")
print("Ularning ro‘yxati:")
for user in sorted(not_followed_back):
    print(user)
