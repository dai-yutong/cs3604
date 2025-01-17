from models import *
from app import *
import unittest
from extensions import db
app=create_app("development")
context = app.test_request_context()
context.push()
class ModelsTest(unittest.TestCase):
    client = app.test_client()
    user_reg1=User()
    def setUp(self): 
        app.config.update( 
            TESTING=True , 
            WTF_CSRF_ENABLED=False, 
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
        )
        db.create_all()
    # 测试添加user
    def test_register(self):
        # 添加user
        user = User(
            username="test_reg1", password=123, email="test_reg1@123.com",about="test_reg1",image='#'
        )
        db.session.add(user)
        db.session.commit()
        user_reg1 = User.query.filter(User.username == "test_reg1").first()
        self.assertIsNotNone(user_reg1)
        self.assertEqual(user_reg1.password, "123")
        self.assertEqual(user_reg1.email, "test_reg1@123.com")
        self.assertEqual(user_reg1.about, "test_reg1")
        flag = user_reg1.is_admin
        self.assertEqual(flag, False)       

        db.session.delete(user_reg1)
        db.session.commit()
        
    # 测试删除user
    def test_delete_user(self):
        user = User(
            username="test_del1", password=123, email="test_del1@123.com",about="test_del1",image='#'
        )
        db.session.add(user)
        db.session.commit()
        user_del1 = User.query.filter(User.username == "test_del1").first()
        self.assertIsNotNone(user_del1)

        # 删除user
        db.session.delete(user_del1)
        db.session.commit()
        user_del1 = User.query.filter(User.username == "test_del1").first()
        self.assertIsNone(user_del1)

    # 测试关注功能
    def test_follow_user(self):
        user = User(
            username="test_follow_user1", password=123, email="test_follow_user1@123.com",about="test_follow_user1",image='#'
        )
        db.session.add(user)
        db.session.commit()
        user = User(
            username="test_follow_user2", password=123, email="test_follow_user2@123.com",about="test_follow_user2",image='#'
        )
        db.session.add(user)
        db.session.commit()
        user_follow = User.query.filter(User.username == "test_follow_user1").first()
        user_followed = User.query.filter(User.username == "test_follow_user2").first()
        # 关注user
        flag = user_follow.follow(user_followed)
        self.assertEqual(flag, True)
        flag = user_follow.is_following(user_followed)
        self.assertEqual(flag, True)
        flag = user_followed.is_followed_by(user_follow)
        self.assertEqual(flag, True)

    # 测试关注，但是关注的用户已关注（此时关注应该失败）
        flag = user_follow.follow(user_followed)
        self.assertEqual(flag, False)
        
        db.session.delete(user_follow)
        db.session.delete(user_followed)
        db.session.commit()

    # 测试取消关注功能
    def test_unfollow_user(self):
        user = User(
            username="test_unfollow_user1", password=123, email="test_unfollow_user1@123.com",about="test_unfollow_user1",image='#'
        )
        db.session.add(user)
        db.session.commit()
        user = User(
            username="test_unfollow_user2", password=123, email="test_unfollow_user2@123.com",about="test_unfollow_user2",image='#'
        )
        db.session.add(user)
        db.session.commit()
        # 关注user
        user_unfollow = User.query.filter(User.username == "test_unfollow_user1").first()
        user_unfollowed = User.query.filter(User.username == "test_unfollow_user2").first()
        user_unfollow.follow(user_unfollowed)
        flag = user_unfollow.is_following(user_unfollowed)
        self.assertEqual(flag, True)
        # 取消关注 刚刚关注的user
        user_unfollow = User.query.filter(User.username == "test_unfollow_user1").first()
        user_unfollowed = User.query.filter(User.username == "test_unfollow_user2").first()
        flag = user_unfollow.unfollow(user_unfollowed)
        self.assertEqual(flag, True)

    # 测试取消关注，但是取消关注的用户并不是已关注的用户（此时取消关注应该失败）
        wronguser = User.query.filter(User.id == 1).first()
        flag = user_unfollow.is_following(wronguser)
        self.assertEqual(flag, False)
        # 取消关注不存在的user
        flag = user_unfollow.unfollow(wronguser)
        self.assertEqual(flag, False)

    # 测试取消关注，但是取消关注的用户不存在（此时取消关注应该失败）
        wronguser = User(
            username="wronguser", password=123, email="wronguser@123.com",about="wronguser",image='#'
        )
        # 取消关注不存在的user
        flag = user_unfollow.unfollow(wronguser)
        self.assertEqual(flag, False)

        db.session.delete(user_unfollow)
        db.session.delete(user_unfollowed)
        db.session.commit()
    
    # 测试收藏功能
    def test_favor(self):

        user = User(
            username="test_favor", password=123, email="test@123.com",about="test",image='#'
        )
        # 测试user创建收藏夹功能
        new_name = "新的收藏夹"
        collection = FavoriteCollection(user=user, name=new_name)
        db.session.add(collection)
        db.session.commit()
        # 把post加入相应收藏夹
        post_id=1
        post = Post.query.get(post_id)
        user.add_favorite(post, collection)
        # 测试post是否在收藏夹中
        flag=user.in_favorite(post, collection=collection)
        self.assertEqual(flag, True)
        # 删除收藏夹中的post
        user.remove_favorite(post, collection=collection)
        flag=user.in_favorite(post, collection=collection)
        self.assertEqual(flag, False)
        # 再次加入收藏夹
        post_id=1
        post = Post.query.get(post_id)
        user.add_favorite(post, collection)
        # 测试是否在收藏夹中，但是没有collection参数
        flag = user.in_favorite(post)
        self.assertEqual(flag, True)
        # 测试收藏已收藏的post
        flag = user.add_favorite(post, collection)
        self.assertEqual(flag, False)
        # 测试删除post，但是没有collection参数
        flag = user.remove_favorite(post)
        self.assertEqual(flag, True)
        flag = user.in_favorite(post)
        self.assertEqual(flag, False)


        db.session.delete(user)
        db.session.commit()

if __name__ == '__main__':
    unittest.main()