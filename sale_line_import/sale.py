# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    
#    Migrated from v6 to v5 by Daniel Inglés Andreu (danielingle@gmail.com)
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import time
from osv import osv, fields
from tools.translate import _
from tools import config
import base64
import csv
import cStringIO
import tools

_logger = logging.getLogger(__name__)

class sale_order(osv.osv):
    _inherit='sale.order'

    def get_update(self, cr, uid, ids2, context={}):
         order_line_obj = self.pool.get('sale.order.line')
         order_line_obj.create(cr, uid, ids2, context)
         return True

    def import_data_line1(self, cr, uid, ids, fdata, favalidate, context={}):
        order=self.browse(cr, uid, ids)

        try:

             vals = {
                        'order_id': int(order.id),
                        'name': u'[P00001CA0101] P00001/REGENT - BARCELONA UNIVERSITY BL. M/C - Talla:S - Color:Blanco',
                        'delay': 7.0,
                        'product_id': 2792,
                        'price_unit': 4.8,
                        'tax_id': 18,
                        'type':  u'make_to_order',
                        'product_uom_qty': 222,
                        'product_uom': 1,
                        'product_uos_qty': 222,
                        'product_uos': False,
                        'discount': 20.0,
                        'th_weight': 0.0,
             }

             #self.pool.get('sale.order.line').create(cr, uid,  {'order_id':int(order.id), 
             #                                                    'name':u'[P00001CA0101] P00001/REGENT - BARCELONA UNIVERSITY BL. M/C - Talla:S - Color:Blanco',
             #                                                    'delay': float(7.0), 'price_unit': 4.8, 'product_id': 2792, 'product_uom_qty': 222, 'product_uom': 1 }, context)
             #self.pool.get('sale.order.line').create(cr, uid,  vals, context)
             ids_tax = []
             ids_tax.append(int(18))
             contador = 0
             while contador < 4:
                 contador = contador + 1
                 _logger.error("contador : %r", contador)
                 self.pool.get('sale.order.line').create(cr, uid,  {'order_id':int(order.id), 
                                                                 'name':u'[P00001CA0101] P00001/REGENT - BARCELONA UNIVERSITY BL. M/C - Talla:S - Color:Blanco',
                                                                 'delay': float(7.0), 'price_unit': 4.8, 'product_id': 2792, 'product_uom_qty': 222, 'product_uom': 1,
                                                                 'tax_id':[(6, 0, ids_tax)]}, context)
       

        except Exception, e:
             _logger.error("Exception : %r", Exception)
             _logger.error("e : %r", e)
             return False
 
    def import_data_line2(self, cr, uid, ids, fdata, favalidate, context={}):
        order=self.browse(cr, uid, ids)
        #order=self.pool.get('sale.order').browse(cr,uid,ids)
        input=cStringIO.StringIO(fdata)
        input.seek(0)
        data = list(csv.reader(input, quotechar='"' or '"', delimiter=';'))
        data[0].append('order_id.id')
        
        try:
            list_prod=data[0].index('product_id')
        except: 
            list_prod=[]
        msg=''
        pmsg=''
        not_products=[]
        new_products_prices=[]

        for dat in data[1:]:
            datas=[]
            data2=list(data[0])
            dat.append(ids)
            _logger.error("data: %r", data)
            _logger.error("entra bucle dat: %r", dat)
            _logger.error("list_prod: %r", list_prod)
            _logger.error("len(data): %r", len(data))
            _logger.error("data[0]: %r", data[0])
            _logger.error("data[1]: %r", data[1])
            _logger.error("data[2]: %r", data[2])
            try:
                prod_name=dat[list_prod]
                _logger.error("prod_name: %r", prod_name)
            except:
                prod_name=False
            context.update({'partner_id':order.partner_id.id})
            #if not prod_name and 'name' in data2:
            #prod_name = dat[data2.index('name')]
            uom_name = 'product_uom' in data2 and dat[data2.index('product_uom')] or ''
            uom_name_search=uom_name and self.pool.get('product.uom').name_search(cr,uid,uom_name,context=context) or False
            uom_id = uom_name_search and uom_name_search[0][0] or False
            prod_name_search=prod_name and self.pool.get('product.product').name_search(cr,uid,prod_name,context=context) or False
            prod_id = prod_name_search and prod_name_search[0][0] or False
            lines=prod_id and self.pool.get('sale.order.line').product_id_change(cr, uid, [], order.pricelist_id.id,prod_id,                       
                                            qty='product_uom_qty' in data2 and float(dat[data2.index('product_uom_qty')]) or 0,uom=uom_id, 
                                            qty_uos=0, uos=False, name='', partner_id=order.partner_id.id,
                                            lang=False, update_tax=True, date_order=order.date_order, packaging=False, fiscal_position=False).get('value',False) or {}

            #prod_id and lines.update({'product_id': prod_name_search[0][1], 'product_uos': lines['product_uos'] and self.pool.get('product.uom').browse(cr,uid,lines['product_uos']).name or False})
            prod_id and lines.update({'product_id': prod_name_search[0][0], 'product_uos': lines['product_uos'] and self.pool.get('product.uom').browse(cr,uid,lines['product_uos']).name or False})

            if not lines and prod_name:
                not_products.append(prod_name)
            if not prod_name:
                _logger.error("Entra if not prod_name: %r", prod_name)
                #self.pool.get('sale.order.line').import_data(cr, uid, data2, [dat], 'init', '')

            for lin in range(len(lines.keys())):
                if lines.keys()[lin] not in data[0]:
                    if lines.keys()[lin] in ('tax_id','product_uom','product_packaging'):
                        field_val=str(lines.keys()[lin])
                        field_val=field_val+'.id'
                        data2.append(field_val)
                        vals_many =str( lines[lines.keys()[lin]] ).replace('[','').replace(']','').replace('False','')
                        dat.append( vals_many )
                    else:
                        data2.append(lines.keys()[lin])
                        dat.append(lines[lines.keys()[lin]])

                else:
                    val_str=dat[data[0].index(lines.keys()[lin])]
                    val_str_2=lines[lines.keys()[lin]]
                    if lines.keys()[lin] in ('product_uom','product_uos'): 
                        val_str_2=self.pool.get('product.uom').browse(cr,uid,val_str_2).name
                        val_str=dat[data[0].index(lines.keys()[lin])]
                    if lines.keys()[lin]=='price_unit':
                        product_price=[]
                        product_price.append(prod_name)
                        val_str=float(dat[data[0].index(lines.keys()[lin])])
                        val_str_2=float(lines[lines.keys()[lin]])
                        if tools.ustr(val_str) <> tools.ustr(val_str_2):
                            product_price.append(val_str)
                            product_price.append(val_str_2)
                            new_products_prices.append(product_price)
                    try:
                        val_str = float(val_str)
                        val_str_2 = float(val_str_2)
                    except:
                        pass
                    if val_str <> val_str_2:
                        if not lines.keys()[lin]=='price_unit':
                            pmsg+=_('%s , Field: %s, CSV: %s, OPEN: %s \n') % (tools.ustr(prod_name),lines.keys()[lin],tools.ustr(dat[data[0].index(lines.keys()[lin])]),tools.ustr(val_str_2))
                        if favalidate:
                            dat[data[0].index(lines.keys()[lin])] = val_str_2
                        else:
                            dat[data[0].index(lines.keys()[lin])] = val_str or val_str_2
            datas.append(dat)

            try:

                lines['order_id'] = order.id
                _logger.error("lines: %r", lines)
                self.pool.get('sale.order.line').create(cr, uid, lines, context)
                  
                #lines and self.pool.get('sale.order.line').import_data(cr, uid, data2, datas, 'init', '',context=context) or False
            except Exception, e:
                _logger.error("e : %r", e)
                return False
            data2=[]
            _logger.error("fin bucle : %r", dat)
        
        msg+=_('Do not you find reference:')
        msg+='\n'
        for p in not_products:
            msg+='%s \n'% (tools.ustr(p))
        msg+='\n'
        msg+=_('Warning of price difference, CSV VS System in the following products:')
        msg+='\n'
        for p in new_products_prices:
            p2=(','.join(map(str,p)))
            msg+='%s \n'%(p2)
        msg+='\n'
        msg+=_('Warning differences in other fields, CSV VS System in the following products and fields:')
        msg+='\n %s '%(pmsg)
        msg2=tools.ustr(pmsg)
        msg=tools.ustr(msg)+'%s '%(msg2)
        return msg

    def import_data_line(self, cr, uid, ids, fdata, favalidate, context={}):
        partner_obj = self.pool.get('res.partner')
        order=self.browse(cr, uid, ids)
        res_partner = partner_obj.browse(cr, uid, order.partner_id.id)
        fiscalPosition = res_partner.property_account_position and res_partner.property_account_position.id or False
        fpos = fiscalPosition and self.pool.get('account.fiscal.position').browse(cr, uid, fiscalPosition) or False
        _logger.error("res_partner.name: %r", res_partner.name)
        _logger.error("fiscalPosition : %r", fiscalPosition)
        _logger.error("fpos : %r", fpos)
        #order=self.pool.get('sale.order').browse(cr,uid,ids)
        input=cStringIO.StringIO(fdata)
        input.seek(0)
        data = list(csv.reader(input, quotechar='"' or '"', delimiter=';'))
        data[0].append('order_id.id')
        try:
            list_prod=data[0].index('product_id')
        except: 
            list_prod=[]
        msg=''
        pmsg=''
        not_products=[]
        new_products_prices=[]

        _logger.error("DATA_data : %r", data)

        for dat in data[1:]:
            datas=[]
            data2=list(data[0])
            dat.append(ids)
            try:
                prod_name=dat[list_prod]
            except:
                prod_name=False
            context.update({'partner_id':order.partner_id.id})
            #if not prod_name and 'name' in data2:
            #prod_name = dat[data2.index('name')]
            uom_name = 'product_uom' in data2 and dat[data2.index('product_uom')] or ''
            uom_name_search=uom_name and self.pool.get('product.uom').name_search(cr,uid,uom_name,context=context) or False
            uom_id = uom_name_search and uom_name_search[0][0] or False
            prod_name_search=prod_name and self.pool.get('product.product').name_search(cr,uid,prod_name,context=context) or False
            prod_id = prod_name_search and prod_name_search[0][0] or False
            lines=prod_id and self.pool.get('sale.order.line').product_id_change(cr, uid, [], order.pricelist_id.id,prod_id,                       
                                            qty='product_uom_qty' in data2 and float(dat[data2.index('product_uom_qty')]) or 0,uom=uom_id, 
                                            qty_uos=0, uos=False, name='', partner_id=order.partner_id.id,
                                            lang=False, update_tax=True, date_order=order.date_order, packaging=False, fiscal_position=False).get('value',False) or {}

            _logger.error("lines: %r", lines)
            #prod_id and lines.update({'product_id': prod_name_search[0][1], 'product_uos': lines['product_uos'] and self.pool.get('product.uom').browse(cr,uid,lines['product_uos']).name or False})
            prod_id and lines.update({'product_id': prod_name_search[0][0], 'product_uos': lines['product_uos'] and self.pool.get('product.uom').browse(cr,uid,lines['product_uos']).name or False})

            if not lines and prod_name:
                not_products.append(prod_name)
            if not prod_name:
                self.pool.get('sale.order.line').import_data(cr, uid, data2, [dat], 'init', '')
            for lin in range(len(lines.keys())):
                if lines.keys()[lin] not in data[0]:
                    if lines.keys()[lin] in ('tax_id','product_uom','product_packaging'):
                        field_val=str(lines.keys()[lin])
                        field_val=field_val+'.id'
                        data2.append(field_val)
                        vals_many =str( lines[lines.keys()[lin]] ).replace('[','').replace(']','').replace('False','')
                        dat.append( vals_many )
                    else:
                        data2.append(lines.keys()[lin])
                        dat.append(lines[lines.keys()[lin]])

                else:
                    val_str=dat[data[0].index(lines.keys()[lin])]
                    val_str_2=lines[lines.keys()[lin]]
                    if lines.keys()[lin] in ('product_uom','product_uos'): 
                        val_str_2=self.pool.get('product.uom').browse(cr,uid,val_str_2).name
                        val_str=dat[data[0].index(lines.keys()[lin])]
                    if lines.keys()[lin]=='price_unit':
                        product_price=[]
                        product_price.append(prod_name)
                        val_str=float(dat[data[0].index(lines.keys()[lin])])
                        val_str_2=float(lines[lines.keys()[lin]])
                        if tools.ustr(val_str) <> tools.ustr(val_str_2):
                            product_price.append(val_str)
                            product_price.append(val_str_2)
                            new_products_prices.append(product_price)
                    try:
                        val_str = float(val_str)
                        val_str_2 = float(val_str_2)
                    except:
                        pass
                    if val_str <> val_str_2:
                        if not lines.keys()[lin]=='price_unit':
                            pmsg+=_('%s , Field: %s, CSV: %s, OPEN: %s \n') % (tools.ustr(prod_name),lines.keys()[lin],tools.ustr(dat[data[0].index(lines.keys()[lin])]),tools.ustr(val_str_2))
                        if favalidate:
                            dat[data[0].index(lines.keys()[lin])] = val_str_2
                        else:
                            dat[data[0].index(lines.keys()[lin])] = val_str or val_str_2
            #dat[data2.index('product_id')] = prod_id
            datas.append(dat)
            _logger.error("DATA_datas: %r", datas)
            try:
                #lines and self.pool.get('sale.order.line').import_data(cr, uid, data2, datas, 'init', '',context=context) or False
                ids_tax = []
                tax_many =str(lines['tax_id']).replace('[','').replace(']','').replace('False','')
                ids_tax.append(tax_many)
                #a = {'tax_id': [(6, 0, ids_tax)]}
                #result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, a)
                #result = self.pool.get('account.fiscal.position').map_tax(cr, uid, fiscalPosition, ids_tax)
                #_logger.error("result: %r", result)
                if fiscalPosition == 2:  #Si tiene recargo de equivalencia
                   ids_tax.append(21)

                _logger.error("tax_many: %r", tax_many)
                lines['tax_id'] = [(6, 0, ids_tax)]
                lines['order_id'] = int(order.id)
                lines['product_uom_qty'] = lines['product_uos_qty']
                _logger.error("lines: %r", lines)
                lines and self.pool.get('sale.order.line').create(cr, uid, lines, context) or False
            except Exception, e:
                _logger.error("Exception e: %r", e)
                return False
            data2=[]
        
        msg+=_('Do not you find reference:')
        msg+='\n'
        for p in not_products:
            msg+='%s \n'% (tools.ustr(p))
        msg+='\n'
        msg+=_('Warning of price difference, CSV VS System in the following products:')
        msg+='\n'
        for p in new_products_prices:
            p2=(','.join(map(str,p)))
            msg+='%s \n'%(p2)
        msg+='\n'
        msg+=_('Warning differences in other fields, CSV VS System in the following products and fields:')
        msg+='\n %s '%(pmsg)
        msg2=tools.ustr(pmsg)
        msg=tools.ustr(msg)+'%s '%(msg2)
        return msg
      
sale_order()
