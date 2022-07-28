# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, SUPERUSER_ID
import werkzeug.urls
import base64
import qrcode
from PIL import Image
import io
from barcode import EAN13
from barcode.writer import ImageWriter
from odoo.exceptions import UserError
import os


class ResPartner(models.Model):
    _inherit = 'res.partner'

    province_id = fields.Many2one('res.country.province', string='Province')
    district_id = fields.Many2one('res.country.district', string='District')
    ward_id = fields.Many2one('res.country.ward', string='Ward')
    barcode_img = fields.Binary('Barcode Image')
    qrcode_img = fields.Binary('QRCode Image')

    def google_map_img(self, zoom=8, width=298, height=298):
        google_maps_api_key = self.env['website'].get_current_website().google_maps_api_key
        if not google_maps_api_key:
            return False
        ward = self.ward_id.name if self.ward_id else ''
        district = self.district_id.name if self.district_id else ''
        province = self.province_id.name if self.province_id else ''
        country = self.country_id and self.country_id.display_name or ''
        params = {
            'center': '%s, %s, %s, %s, %s' % (self.street or '', ward, district, province, country),
            'size': "%sx%s" % (width, height),
            'zoom': zoom,
            'sensor': 'false',
            'key': google_maps_api_key,
        }
        return '//maps.googleapis.com/maps/api/staticmap?'+werkzeug.urls.url_encode(params)

    def google_map_link(self, zoom=10):
        ward = self.ward_id.name if self.ward_id else ''
        district = self.district_id.name if self.district_id else ''
        province = self.province_id.name if self.province_id else ''
        country = self.country_id and self.country_id.display_name or ''
        params = {
            'q': '%s, %s, %s, %s, %s' % (self.street or '', ward, district, province, country),
            'z': zoom,
        }
        return 'https://maps.google.com/maps?' + werkzeug.urls.url_encode(params)

    def generate_barcode_im(self):
        if not self.barcode:
            raise UserError("Please input barcode number")
        if self.barcode and len(self.barcode) != 13:
            raise UserError("Barcode number must to have length is 13")
        # co them thong tin number code phia duoi
        my_code = EAN13(self.barcode, writer=ImageWriter())
        img_barcode = my_code.save("img_barcode")
        image = open(img_barcode, 'rb')
        image_read = image.read()
        image_64_encode = base64.encodestring(image_read)
        self.barcode_img = image_64_encode
        return

    def generate_qrcode_im(self):
        # Logo_link = os.path.join(os.path.dirname(__file__), 'nature-logo.png')
        logo = Image.open(io.BytesIO(base64.b64decode(self.image_1920)))
        basewidth = 100
        wpercent = (basewidth / float(logo.size[0]))
        hsize = int((float(logo.size[1]) * float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
        QRcode = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        url = 'https://thanhkoi.vn'
        QRcode.add_data(url)
        QRcode.make()
        QRcolor = 'Black'
        QRimg = QRcode.make_image(
            fill_color=QRcolor, back_color="white").convert('RGB')
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
               (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)
        QRimg.save(os.path.join(os.path.dirname(__file__), '%s.png' % self.name))
        image = open(os.path.join(os.path.dirname(__file__), '%s.png' % self.name), 'rb')
        image_read = image.read()
        image_64_encode = base64.encodestring(image_read)
        self.qrcode_img = image_64_encode
        self.env['ir.attachment'].create({
            'datas': image_64_encode,
            'res_id': self.id,
            'name': self.name,
            'res_model': 'res.partner'
        })
        print('QR code generated!')
        os.remove(os.path.join(os.path.dirname(__file__), '%s.png' % self.name))
        return