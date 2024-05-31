from models.user import User
from utils import document_to_model, mongo_client
from bson import ObjectId
import constants as api_c


class UserController:
    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        """
        Retrieve a user by their email address.
        Args:
            username (str): Email address of the user.
        Returns:
            User: User details.
        """
        try:
            user_data = mongo_client.db.users.find_one({"username": username})
            if user_data:
                return document_to_model(User, user_data)
            return None
        except Exception as e:
            return None

    @staticmethod
    def create_user(user: User) -> User | None:
        """
        Create a new user in the database.
        Args:
            user (User): User data.
        Returns:
            User: Newly created user details.
        """
        user_data = user.dict()
        user_already_exist = UserController.get_user_by_username(user_data.get("email"))
        if user_already_exist:
            return None
        mongo_client.db.users.insert_one(user_data)
        return document_to_model(User, user_data)

    @staticmethod
    def get_user_by_id(user_id: str) -> User | None:
        """
        Get user in the database.
        Args:
            user_id (str): User ID.
        Returns:
            User: User details.
        """

        try:
            user_data = mongo_client.db.users.find_one({api_c.ID: ObjectId(user_id)})
            if user_data:
                return User(**user_data)
            return None
        except Exception as e:
            return None

    @staticmethod
    def update_user(user_id: str, user: User) -> User | None:
        """
        Update user in the database
        Args:
            user_id (str): user id
            user (User): update user details
        Returns:
             user (User): Updated user
        """
        result = mongo_client.db.users.replace_one(
            {api_c.ID: ObjectId(user_id)}, user.dict()
        )
        if result.modified_count > 0:
            return UserController.get_user_by_id(user_id)
        else:
            return None

    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        Delete a user
        Args:
            user_id (str): user id
        Returns:
             None
        """
        result = mongo_client.db.users.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0