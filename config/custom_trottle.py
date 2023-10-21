from rest_framework import throttling


class ExtendedAnonRateThrottle(throttling.AnonRateThrottle):
    def parse_rate(self, rate):

        if rate is None:
            return None, None
        num, period = rate.split('/')
        num_requests = int(num)
        number, period = self.get_number_in_period(period)

        duration = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[period[0]] * int(number)
        return num_requests, duration

    @staticmethod
    def get_number_in_period(arg):
        number = ''
        period = ''
        flag = False
        for char in arg:
            if char.isdigit():
                if flag is False:
                    number += char
                else:
                    flag = None
            elif char.isalpha() and flag is not None:
                period += char
                flag = True
        if len(number) == 0:
            number = "1"

        return number, period


class ResetPasswordRateThrottle(ExtendedAnonRateThrottle):
    scope = "reset_password"


class SetPasswordRateThrottle(ExtendedAnonRateThrottle):
    scope = "set_password"


class VerifyAccountRateThrottle(ExtendedAnonRateThrottle):
    scope = "verify_account"
