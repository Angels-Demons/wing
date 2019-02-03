from kavenegar import *


def send_sms(phone=9367498998, message='null'):
    try:

        # maman bahar:
        # api = KavenegarAPI('3453544B6A61554251426B2B6D5934676845744A4D546C4234617A346131374C')

        # baba feri:
        api = KavenegarAPI('4C736572316E776B5752717A596F50774D4473746E694E4A5652734F786C7961')

        # khodam hf
        # api = KavenegarAPI('536C7A34554A375354324B594E7A682F51426D324E7046347169366C704A3455')
        params = {
            'sender': '',  # optional
            'receptor': str(phone),  # multiple mobile number, split by comma
            'message': message,
        }
        response = api.sms_send(params)
        # print(response)
        return response
    except APIException as e:
        # print(e)
        return e
    except HTTPException as e:
        # print(e)
        return e

# send_sms(9367498998, 'سلام45')
