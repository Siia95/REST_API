from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
        Settings for the FastAPI application.

        - `mail_username`: The username for the email server.
        - `mail_password`: The password for the email server.
        - `mail_from`: The sender email address.
        - `mail_port`: The port number for the email server.
        - `mail_server`: The address of the email server.

        - `postgres_db`: The name of the PostgreSQL database.
        - `postgres_user`: The username for the PostgreSQL database.
        - `postgres_password`: The password for the PostgreSQL database.
        - `postgres_port`: The port number for the PostgreSQL database.

        - `sqlalchemy_database_url`: The URL for connecting to the PostgreSQL database.

        - `secret_key`: The secret key for hashing and encoding.
        - `algorithm`: The algorithm to use for hashing and encoding.

        - `redis_host`: The address of the Redis server.
        - `redis_port`: The port number for the Redis server.

        - `env_file`: The path to the environment file.
        - `env_file_encoding`: The encoding of the environment file.
        """
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int

    sqlalchemy_database_url: str

    secret_key: str
    algorithm: str

    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
