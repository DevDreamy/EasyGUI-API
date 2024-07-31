from .base_server import BaseServer
from flask import request, Response, jsonify
import datetime
import jwt


class JwtAuthServer(BaseServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            auth_header = request.headers.get('Authorization')

            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                if self.check_jwt(token):
                    return jsonify(self.json_data)
                else:
                    return self.error_401('Invalid or expired token.')
            return self.error_401('Token is missing.')

        @self._app.route('/token', methods=['POST'])
        def token():
            auth = request.authorization

            if (
                auth
                and auth.username == self.username
                and auth.password == self.password
            ):
                expiration_time = (
                    datetime.datetime.utcnow()
                    + datetime.timedelta(minutes=self.expiration_time)
                )
                token = jwt.encode(
                    {
                        'user': auth.username,
                        'exp': expiration_time,
                    },
                    self.secret_key,
                    algorithm="HS256",
                )
                expires_in = (
                    expiration_time - datetime.datetime.utcnow()
                ).total_seconds()
                return jsonify(
                    {
                        'access_token': token,
                        'token_type': 'bearer',
                        'expires_in': expires_in,
                    }
                )
            return Response(
                'Incorrect username or password.\n'
                'Expected: user | password\n'
                f'Received: {auth.username} | {auth.password}',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )

        @self._app.route('/refresh', methods=['POST'])
        def refresh():
            auth_header = request.headers.get('Authorization')

            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

                try:
                    data = jwt.decode(
                        token,
                        self.secret_key,
                        algorithms=["HS256"],
                        options={"verify_exp": False},
                    )
                    new_expiration_time = (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=self.expiration_time)
                    )
                    new_token = jwt.encode(
                        {
                            'user': data['user'],
                            'exp': new_expiration_time,
                        },
                        self.secret_key,
                        algorithm="HS256",
                    )
                    new_expires_in = (
                        new_expiration_time - datetime.datetime.utcnow()
                    ).total_seconds()
                    return jsonify(
                        {
                            'access_token': new_token,
                            'token_type': 'bearer',
                            'expires_in': new_expires_in,
                        }
                    )
                except jwt.ExpiredSignatureError:
                    return self.error_401('Token has expired.')
                except jwt.InvalidTokenError:
                    return self.error_401('Invalid token.')
            return self.error_401('Token is missing.')

    def check_jwt(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return data['user'] == self.username
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
