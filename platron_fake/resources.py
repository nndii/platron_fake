import typing
import uuid


class Transaction(typing.NamedTuple):
    pg_order_id: int
    pg_merchant_id: str
    pg_request_method: str
    pg_success_url: str
    pg_failure_url: str
    pg_success_url_method: str
    pg_failure_url_method: str
    pg_testing_mode: str
    pg_amount: str
    pg_check_url: str
    pg_result_url: str
    pg_encoding: str
    pg_description: str
    pg_user_phone: str
    pg_user_contact_email: str
    pg_language: str
    pg_payment_system: str
    pg_user_email: str
    pg_user_ip: str
    tc_order: str
    tc_payment: str
    tc_tickets: str
    tc_event: str
    tc_org: str
    tc_vendor: str
    pg_lifetime: str
    pg_currency: str = 'RUB'
    pg_redirect_url: str = 'http://example.com'
    pg_redirect_url_type: str = 'payment system'
    pg_payment_id: str = str(uuid.uuid4())
    pg_card_brand: str = 'Visa'

    def jsonify(self, required=None):
        if required is None:
            required = set(self._fields)

        result = {}
        for field in required:
            result[field] = getattr(self, field, '')

        return result
