import collections
from fastapi import Request

_TEST_PUBLIC_KEY_BASE58 = '56NjiE3vSnGWmu4Cmq4k5dA6oL4ZkAvD1TRdizxxXrnW'
_TEST_SIGNATURE_BASE58 = '22HtMFY949th2gno5BRXov2ZDtmmPgns1DeeottgYfGy1x63uDWX7KaZqVQvYc3X3ooAmYPMP7GyX4ju9QYe61uB'

_MOCK_REQUEST = collections.namedtuple('Request', ['headers'])(headers={
    'Authorization': f'Base58 {_TEST_PUBLIC_KEY_BASE58}:{_TEST_SIGNATURE_BASE58}'
})
