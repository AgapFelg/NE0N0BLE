from datetime import datetime, timedelta
import random
from models import db, User, Post, Like, Follow, Comment
from app import create_app
from werkzeug.security import generate_password_hash
import shutil
import os


def seed_database():
    app = create_app()

    with app.app_context():
        # очистка тех данных, которые есть сейчас
        # Меняем порядок удаления из-за ограничений внешних ключей
        print("Cleaning database...")
        db.session.query(Like).delete()
        db.session.query(Comment).delete()
        db.session.query(Post).delete()
        db.session.query(Follow).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("Database cleaned")

        # создание юзеров
        users = [
            User(id=1, username='taro_yamada', email='taro@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_1.jpg', biography='こんにちは、山田太郎です。写真を撮るのが好きです。'),
            User(id=2, username='hanako_sato', email='hanako@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_2.jpg', biography='佐藤花子と申します。旅行と料理が趣味です。'),
            User(id=3, username='alex_smith', email='alex@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_3.jpg', biography='Photography enthusiast and travel lover'),
            User(id=4, username='emma_jones', email='emma@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_4.jpg', biography='Digital artist and coffee addict'),
            User(id=5, username='mike_wilson', email='mike@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_5.jpg', biography='Software developer and gamer'),
            User(id=6, username='sara_miller', email='sara@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_6.jpg', biography='Book lover and amateur photographer'),
            User(id=7, username='john_doe', email='john@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_7.jpg', biography='Fitness coach and nutrition expert'),
            User(id=8, username='lisa_brown', email='lisa@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_8.jpg', biography='Marketing specialist and yoga practitioner'),
            User(id=9, username='david_clark', email='david@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_9.jpg', biography='Music producer and DJ'),
            User(id=10, username='amy_taylor', email='amy@example.com', password_hash=generate_password_hash('12345678'),
                 avatar='avatar_10.jpg', biography='Teacher and adventure seeker')
        ]

        # добавляем пользователей по одному и сразу коммитим
        print("Creating users...")
        for i, user in enumerate(users, 1):
            db.session.add(user)
            db.session.commit()
            print(f"Created user {i}: {user.username} with ID {user.id}")

        # Проверяем, что пользователи действительно созданы
        existing_users = User.query.all()
        print(f"Total users in DB: {len(existing_users)}")
        for user in existing_users:
            print(f"User ID: {user.id}, Username: {user.username}")

        # создание постов
        posts_data = [
            # taro_yamada (10 японских постов)
            {'id': 1, 'text': '今日の夕焼けがとても綺麗でした。', 'user_id': 1, 'image': '1_0000000001.jpg'},
            {'id': 2,'text': '新しいカメラを買いました。', 'user_id': 1, 'image': '1_0000000002.jpg'},
            {'id': 3,'text': '散歩中に見つけた可愛い猫。', 'user_id': 1, 'image': '1_0000000003.jpg'},
            {'id': 4,'text': '美味しいラーメンを食べました。', 'user_id': 1, 'image': '1_0000000004.jpg'},
            {'id': 5,'text': '読書の時間が至福の時。', 'user_id': 1, 'image': '1_0000000005.jpg'},
            {'id': 6,'text': '桜の季節が待ち遠しい。', 'user_id': 1, 'image': '1_0000000006.jpg'},
            {'id': 7,'text': '今日も一日頑張ろう。', 'user_id': 1, 'image': '1_0000000007.jpg'},
            {'id': 8,'text': 'コーヒーが美味しい朝。', 'user_id': 1, 'image': '1_0000000008.jpg'},
            {'id': 9,'text': '雨の日は静かに過ごしたい。', 'user_id': 1, 'image': '1_0000000009.jpg'},
            {'id': 10,'text': '友達と楽しい時間を過ごしました。', 'user_id': 1, 'image': '1_0000000010.jpg'},

            # hanako_sato (10 японских постов)
            {'id': 11,'text': 'お花見の準備をしています。', 'user_id': 2, 'image': '2_0000000001.jpg'},
            {'id': 12,'text': '手作りのケーキが完成！', 'user_id': 2, 'image': '2_0000000002.jpg'},
            {'id': 13,'text': '京都旅行の思い出。', 'user_id': 2, 'image': '2_0000000003.jpg'},
            {'id': 14,'text': '温泉が最高でした。', 'user_id': 2, 'image': '2_0000000004.jpg'},
            {'id': 15,'text': '新しいレシピに挑戦中。', 'user_id': 2, 'image': '2_0000000005.jpg'},
            {'id': 16,'text': '晴れた日は洗濯日和。', 'user_id': 2, 'image': '2_0000000006.jpg'},
            {'id': 17,'text': '猫と一緒にお昼寝。', 'user_id': 2, 'image': '2_0000000007.jpg'},
            {'id': 18,'text': '映画を観て泣きました。', 'user_id': 2, 'image': '2_0000000008.jpg'},
            {'id': 19,'text': '明日は晴れるかな？', 'user_id': 2, 'image': '2_0000000009.jpg'},
            {'id': 20,'text': '美味しいお茶と和菓子。', 'user_id': 2, 'image': '2_0000000010.jpg'},

            # Остальные пользователи по 3 поста каждый
            {'id': 21,'text': 'Beautiful sunset today!', 'user_id': 3, 'image': '3_0000000001.jpg'},
            {'id': 22,'text': 'New camera arrived!', 'user_id': 3, 'image': '3_0000000002.jpg'},
            {'id': 23,'text': 'Coffee break time.', 'user_id': 3, 'image': '3_0000000003.jpg'},

            {'id': 24,'text': 'Working on new art project.', 'user_id': 4, 'image': '4_0000000001.jpg'},
            {'id': 25,'text': 'Inspired by nature today.', 'user_id': 4, 'image': '4_0000000002.jpg'},
            {'id': 26,'text': 'Digital painting progress.', 'user_id': 4, 'image': '4_0000000003.jpg'},

            {'id': 27,'text': 'Coding marathon continues.', 'user_id': 5, 'image': '5_0000000001.jpg'},
            {'id': 28,'text': 'New game release!', 'user_id': 5, 'image': '5_0000000002.jpg'},
            {'id': 29,'text': 'Debugging time...', 'user_id': 5, 'image': '5_0000000003.jpg'},

            {'id': 30,'text': 'Reading a great book.', 'user_id': 6, 'image': '6_0000000001.jpg'},
            {'id': 31,'text': 'Photography session today.', 'user_id': 6, 'image': '6_0000000002.jpg'},
            {'id': 32,'text': 'Library visit was productive.', 'user_id': 6, 'image': '6_0000000003.jpg'},

            {'id': 33,'text': 'Morning workout complete.', 'user_id': 7, 'image': '7_0000000001.jpg'},
            {'id': 34,'text': 'Healthy meal prep done.', 'user_id': 7, 'image': '7_0000000002.jpg'},
            {'id': 35,'text': 'Client training session went well.', 'user_id': 7, 'image': '7_0000000003.jpg'},

            {'id': 36,'text': 'Marketing campaign launched.', 'user_id': 8, 'image': '8_0000000001.jpg'},
            {'id': 37,'text': 'Yoga class was amazing.', 'user_id': 8, 'image': '8_0000000002.jpg'},
            {'id': 38,'text': 'Client meeting success.', 'user_id': 8, 'image': '8_0000000003.jpg'},

            {'id': 39,'text': 'Studio session today.', 'user_id': 9, 'image': '9_0000000001.jpg'},
            {'id': 40,'text': 'New track almost finished.', 'user_id': 9, 'image': '9_0000000002.jpg'},
            {'id': 41,'text': 'DJ set tonight!', 'user_id': 9, 'image': '9_0000000003.jpg'},

            {'id': 42,'text': 'Great class today!', 'user_id': 10, 'image': '10_0000000001.jpg'},
            {'id': 43,'text': 'Planning next adventure.', 'user_id': 10, 'image': '10_0000000002.jpg'},
            {'id': 44,'text': 'Students did amazing work.', 'user_id': 10, 'image': '10_0000000003.jpg'}
        ]

        # добавляем посты по одному
        print("Creating posts...")
        posts = []
        for i, post_data in enumerate(posts_data):
            # Проверяем, существует ли пользователь
            user = User.query.get(post_data['user_id'])
            if not user:
                print(f"ERROR: User with ID {post_data['user_id']} not found! Skipping post.")
                continue

            post = Post(
                id=post_data['id'],
                text=post_data['text'],
                user_id=post_data['user_id'],
                image=post_data['image'],
                created_at=datetime.now() - timedelta(hours=len(posts_data) - i)
            )
            db.session.add(post)
            db.session.commit()
            posts.append(post)
            print(f"Created post {i + 1} for user ID {post_data['user_id']}")

        # рандомное проставление лайков
        print("Creating likes...")
        for user in users:
            # каждый пользователь лайкает 3 случайных поста
            random_posts = random.sample(posts, min(3, len(posts)))
            for post in random_posts:
                # проверяем, не лайкнул ли уже этот пост
                existing_like = Like.query.filter_by(user_id=user.id, post_id=post.id).first()
                if not existing_like:
                    like = Like(user_id=user.id, post_id=post.id)
                    db.session.add(like)
        db.session.commit()
        print("Likes created")

        # рандомные подписки
        print("Creating follows...")
        follow_combinations = [
            (3, 1), (4, 1), (5, 2), (6, 2), (1, 3), (2, 4),
            (7, 5), (8, 6), (9, 7), (10, 8), (1, 9), (2, 10)
        ]

        for follower_id, followed_id in follow_combinations:
            # проверка наличия подписки
            existing_follow = Follow.query.filter_by(
                follower_id=follower_id, followed_id=followed_id
            ).first()
            if not existing_follow:
                follow = Follow(follower_id=follower_id, followed_id=followed_id)
                db.session.add(follow)
        db.session.commit()
        print("Follows created")

        # создание комментариев
        print("Creating comments...")
        comments_data = [
            # комментарии к японским постам (на японском)
            {'text': '素敵な写真ですね！', 'user_id': 2, 'post_id': 1},
            {'text': '夕焼けが綺麗ですね！', 'user_id': 3, 'post_id': 1},
            {'text': 'また見せてください！', 'user_id': 4, 'post_id': 1},
        ]

        for i, comment_data in enumerate(comments_data):
            # Проверяем существование пользователя и поста
            user = User.query.get(comment_data['user_id'])
            post = Post.query.get(comment_data['post_id'])

            if not user:
                print(f"ERROR: User with ID {comment_data['user_id']} not found! Skipping comment.")
                continue
            if not post:
                print(f"ERROR: Post with ID {comment_data['post_id']} not found! Skipping comment.")
                continue

            comment = Comment(
                text=comment_data['text'],
                user_id=comment_data['user_id'],
                post_id=comment_data['post_id'],
                created_at=datetime.now() - timedelta(minutes=len(comments_data) - i)
            )
            db.session.add(comment)
        db.session.commit()
        print("Comments created")


def copy_images():
    print("Copying images...")
    # Создаем целевые директории, если они не существуют
    os.makedirs('static/uploads/avatars', exist_ok=True)
    os.makedirs('static/uploads/posts', exist_ok=True)

    avatars_source_dir = 'IMAGES_FOR_CONTENT_FILLING/avatars_images'
    avatars_target_dir = 'static/uploads/avatars'

    if os.path.exists(avatars_source_dir):
        file_names = os.listdir(avatars_source_dir)
        for file_name in file_names:
            source_path = os.path.join(avatars_source_dir, file_name)
            target_path = os.path.join(avatars_target_dir, file_name)
            shutil.copy(source_path, target_path)
        print(f"Copied {len(file_names)} avatar images")

    post_images_source_dir = 'IMAGES_FOR_CONTENT_FILLING/posts_images'
    post_images_target_dir = 'static/uploads/posts'

    if os.path.exists(post_images_source_dir):
        file_names = os.listdir(post_images_source_dir)
        for file_name in file_names:
            source_path = os.path.join(post_images_source_dir, file_name)
            target_path = os.path.join(post_images_target_dir, file_name)
            shutil.copy(source_path, target_path)
        print(f"Copied {len(file_names)} post images")


if __name__ == '__main__':
    seed_database()
    print("Database seeded successfully!")
    copy_images()
    print("Images copied successfully!")