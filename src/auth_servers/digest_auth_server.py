from .base_server import BaseServer
from flask import request, Response, jsonify
from hashlib import md5
from werkzeug.http import parse_dict_header
import os


class DigestAuthServer(BaseServer):
    def __init__(self, port):
        super().__init__(port)

        @self._app.route('/', methods=['GET'])
        def jsonResponse():
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_type, auth_info = auth_header.split(' ', 1)
                if auth_type.lower() == 'digest':
                    auth_info_dict = parse_dict_header(auth_info)
                    if self.check_digest(auth_info_dict):
                        return jsonify(self.json_data)
                    else:
                        return self.error_401_digest_invalid_response()
            nonce = self.generate_nonce()
            return self.error_401_digest(self.realm, nonce)

    def generate_nonce(self):
        return md5(os.urandom(16)).hexdigest()

    def check_digest(self, auth_info_dict):
        ha1 = md5(
            f'{self.username}:{self.realm}:{self.password}'.encode()
        ).hexdigest()
        ha2 = md5(f'GET:{auth_info_dict["uri"]}'.encode()).hexdigest()
        valid_response = md5(
            (
                f'{ha1}:'
                f'{auth_info_dict["nonce"]}:'
                f'{auth_info_dict["nc"]}:'
                f'{auth_info_dict["cnonce"]}:'
                f'{auth_info_dict["qop"]}:'
                f'{ha2}'
            ).encode()
        ).hexdigest()
        return auth_info_dict['response'] == valid_response

    def error_401_digest(self, realm, nonce):
        return Response(
            'Digest authentication required. '
            'Please provide valid credentials.',
            401,
            {
                'WWW-Authenticate': (
                    f'Digest realm="{realm}", '
                    f'nonce="{nonce}", '
                    f'algorithm="{self.digest_algorithm}", '
                    'qop="{self.digest_qop}"'
                )
            },
        )

    def error_401_digest_invalid_response(self):
        return Response(
            'Invalid or expired digest response. '
            'Please check your credentials and try again.',
            401,
            {
                'WWW-Authenticate': (
                    f'Digest realm="{self.realm}", '
                    f'algorithm="{self.digest_algorithm}", '
                    f'qop="{self.digest_qop}"'
                )
            },
        )
