from marshmallow import Schema, fields


class ArchivedPageSchema(Schema):
    id = fields.Int(dump_only=True)
    url = fields.URL(required=True)
    html = fields.Str(required=True)
    timestamp = fields.DateTime(dump_only=True)


class DomainInfoSchema(Schema):
    id = fields.Int(dump_only=True)
    domain = fields.Str(required=True)
    ip_address = fields.Str(required=True)
    whois_protocol = fields.Str(required=True)
    network_info = fields.Str(required=True)
    archived_page_id = fields.Int(required=True)
