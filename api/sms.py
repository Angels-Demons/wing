from kavenegar import *

api = KavenegarAPI('4C736572316E776B5752717A596F50774D4473746E694E4A5652734F786C7961')


def verify(phone, password):
    try:
        params = {
            'receptor': str(phone),
            'token': password,
            'template': 'verify'
        }
        response = api.verify_lookup(params)
        return response
    except APIException as e:
        return e
    except HTTPException as e:
        return e


def lock_unlock(phone, lock, device_code):
    if lock:
        token = "lock"
    else:
        token = "unlock"
    try:
        params = {
            'receptor': str(phone),
            'token': token,
            'token2': device_code,
            'template': 'lock-unlock'
        }
        response = api.verify_lookup(params)
        return response
    except APIException as e:
        return e
    except HTTPException as e:
        return e


def send_sms(phone, message):
    try:
        params = {
            'receptor': str(phone),
            'message': message,
        }
        response = api.sms_send(params)
        return response
    except APIException as e:
        return e
    except HTTPException as e:
        return e


# lock_unlock(9120199974, True, 123456)
