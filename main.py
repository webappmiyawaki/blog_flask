from app import Post
from app import User

posts = Post.query.all()
users = User.query.all()

for user in users:
    print(user)

for post in posts:
    print(post)


