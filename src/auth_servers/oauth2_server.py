from .base_server import BaseServer
from flask import request, Response, jsonify
import datetime
import jwt


class OAuth2Server(BaseServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    data = jwt.decode(
                        token, self.secret_key, algorithms=["HS256"]
                    )
                    if data['client_id'] == self.client_id:
                        return jsonify(self.json_data)
                    else:
                        return self.error_401('Invalid client ID in token.')
                except jwt.ExpiredSignatureError:
                    return self.error_401('Token has expired.')
                except jwt.InvalidTokenError:
                    return self.error_401('Invalid token.')
            return self.error_401('Token is missing.')

        @self._app.route('/token', methods=['POST'])
        def token():
            client_id = request.form.get('client_id')
            client_secret = request.form.get('client_secret')
            grant_type = request.form.get('grant_type')

            if grant_type == self.grant_type:
                if (
                    client_id == self.client_id
                    and client_secret == self.client_secret
                ):
                    expiration_time = (
                        datetime.datetime.utcnow()
                        + datetime.timedelta(minutes=self.expiration_time)
                    )
                    token = jwt.encode(
                        {
                            'client_id': client_id,
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
                return Response('Invalid client ID or secret.', 401)
            return Response('Unsupported grant type.', 400)

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
                            'client_id': data['client_id'],
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

    def check_oauth2(self, token):
        try:
            data = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return data['client_id'] == self.client_id
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
