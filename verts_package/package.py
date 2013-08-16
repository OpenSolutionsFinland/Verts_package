from osv import osv , fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import pooler
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import decimal_precision as dp
import netsvc

class packing_list_line(osv.osv):
    _name = 'packing.list.line'
    _columns = {
        'can':fields.integer('Can'),
        'tray':fields.integer('Tray'),
        'pallet':fields.integer('Pallet'),
        'product_id':fields.many2one('product.product','Product'),
        'name':fields.char('Product',size=512),
        'product_qty':fields.float('Product Qty'),
        'order_id':fields.many2one('sale.order','Order Id'),
        'picking_id':fields.many2one('stock.picking','Picking Id'),
        'invoice_id':fields.many2one('account.invoice','Invoice Id'),
        'grass_weight':fields.float('Gross Weight'),
        'net_weight':fields.float('Net Weight'),
        
 }
packing_list_line()

class product_product(osv.osv):
    _inherit = 'product.product'
    _columns = {
       'custom_code':fields.char('Custom Code',size=256),
    }
 
product_product()   

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
       'package_list_lines': fields.one2many('packing.list.line', 'picking_id', 'Package Lines',),
    }
    
    def generate_packing_list(self, cr, uid, ids, context=None):
        packing_list_line_obj = self.pool.get('packing.list.line')
        for picking in self.browse(cr, uid, ids, context):
          total_product_qty=total_pallet_qty=total_tray_qty=total_can_qty=0
          total_net_weight=total_gross_weight=0  
          all_packing_list_line_ids=packing_list_line_obj.search(cr,uid,[('picking_id','=',picking.id)])
          packing_list_line_obj.unlink(cr,uid,all_packing_list_line_ids)  
          for line in picking.move_lines:
             reminder=pallet_qty=tray_qty=can_qty=0
             pallet=tray=can=p_weight=t_weight=c_weight=0 
             for package in line.product_id.packaging:
                 if package.ul.type=='pallet':
                     pallet=package.qty
                     p_weight=package.weight
                 if package.ul.type=='box':
                     tray=package.qty
                     t_weight=package.weight
                 if package.ul.type=='unit':
                    can=package.qty
                    c_weight=package.weight     
             if pallet:
                pallet_qty=line.product_qty/pallet
                reminder=line.product_qty%pallet
                if tray and reminder: 
                   tray_qty=reminder/tray
                   reminder=reminder%tray
                if can and reminder:  
                   can_qty=reminder/can
             elif tray:
                tray_qty=line.product_qty/tray
                reminder=line.product_qty%tray 
                if can and reminder:  
                   can_qty=reminder/can
             elif can:
                can_qty=line.product_qty/can
             
             if line.product_id.packaging:
                 total_product_qty+=(line.product_qty)  
                 total_net_weight+=c_weight*line.product_qty
             total_pallet_qty+=int(pallet_qty) 
             total_tray_qty+=int(tray_qty)
             total_can_qty+=int(can_qty) 
             total_gross_weight+=pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             vals={}
             vals['product_id'] = line.product_id.id
             vals['name'] = line.product_id.name
             vals['product_qty']=line.product_qty
             vals['pallet'] = pallet_qty
             vals['tray'] = tray_qty
             vals['can'] = can_qty
             vals['net_weight'] =c_weight*line.product_qty
             vals['grass_weight'] =pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             vals['picking_id']=picking.id
             if pallet_qty or tray_qty or can_qty:
               packing_list_line_obj.create(cr,uid,vals)
          
          if total_pallet_qty or total_tray_qty or total_can_qty:
              vals={}
              vals['name'] ='Total'
              vals['product_qty']=total_product_qty
              vals['pallet'] = total_pallet_qty
              vals['tray'] = total_tray_qty
              vals['can'] = total_can_qty
              vals['net_weight'] =total_net_weight
              vals['grass_weight'] =total_gross_weight
              vals['picking_id']=picking.id
              packing_list_line_obj.create(cr,uid,vals)
        return True
stock_picking()

class stock_picking_out(osv.osv):
    _inherit = 'stock.picking.out'
    _columns = {
       'package_list_lines': fields.one2many('packing.list.line', 'picking_id', 'Package Lines',),
    }
    
    def generate_packing_list(self, cr, uid, ids, context=None):
        packing_list_line_obj = self.pool.get('packing.list.line')
        for picking in self.browse(cr, uid, ids, context):
          total_product_qty=total_pallet_qty=total_tray_qty=total_can_qty=0
          total_net_weight=total_gross_weight=0  
          all_packing_list_line_ids=packing_list_line_obj.search(cr,uid,[('picking_id','=',picking.id)])
          packing_list_line_obj.unlink(cr,uid,all_packing_list_line_ids)  
          for line in picking.move_lines:
             reminder=pallet_qty=tray_qty=can_qty=0
             pallet=tray=can=p_weight=t_weight=c_weight=0 
             for package in line.product_id.packaging:
                 if package.ul.type=='pallet':
                     pallet=package.qty
                     p_weight=package.weight
                 if package.ul.type=='box':
                     tray=package.qty
                     t_weight=package.weight
                 if package.ul.type=='unit':
                    can=package.qty
                    c_weight=package.weight     
             
             if pallet:
                pallet_qty=line.product_qty/pallet
                reminder=line.product_qty%pallet
                if tray and reminder: 
                   tray_qty=reminder/tray
                   reminder=reminder%tray
                if can and reminder:  
                   can_qty=reminder/can
             elif tray:
                tray_qty=line.product_qty/tray
                reminder=line.product_qty%tray 
                if can and reminder:  
                   can_qty=reminder/can
             elif can:
                can_qty=line.product_qty/can
             
             if line.product_id.packaging:
                 total_product_qty+=(line.product_qty)  
                 total_net_weight+=c_weight*line.product_qty
             total_pallet_qty+=int(pallet_qty) 
             total_tray_qty+=int(tray_qty)
             total_can_qty+=int(can_qty) 
             total_gross_weight+=pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             vals={}
             vals['product_id'] = line.product_id.id
             vals['name'] = line.product_id.name
             vals['product_qty']=line.product_qty
             vals['pallet'] = pallet_qty
             vals['tray'] = tray_qty
             vals['can'] = can_qty
             vals['net_weight'] =c_weight*line.product_qty
             vals['grass_weight'] =pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             vals['picking_id']=picking.id
             if pallet_qty or tray_qty or can_qty:
               packing_list_line_obj.create(cr,uid,vals)
          
          if total_pallet_qty or total_tray_qty or total_can_qty:
              vals={}
              vals['name'] ='Total'
              vals['product_qty']=total_product_qty
              vals['pallet'] = total_pallet_qty
              vals['tray'] = total_tray_qty
              vals['can'] = total_can_qty
              vals['net_weight'] =total_net_weight
              vals['grass_weight'] =total_gross_weight
              vals['picking_id']=picking.id
              packing_list_line_obj.create(cr,uid,vals)
        return True
stock_picking_out()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
       'package_list_lines': fields.one2many('packing.list.line', 'invoice_id', 'Package Lines',) ,
       'sale_id':fields.many2one('sale.order','Order Id'),
       'trademark':fields.char('Trade Mark',size=512),
    }
    
    def generate_packing_list(self, cr, uid, ids, context=None):
        packing_list_line_obj = self.pool.get('packing.list.line')
        for invoice in self.browse(cr, uid, ids, context):
          total_product_qty=total_pallet_qty=total_tray_qty=total_can_qty=0
          total_net_weight=total_gross_weight=0  
          all_packing_list_line_ids=packing_list_line_obj.search(cr,uid,[('invoice_id','=',invoice.id)])
          packing_list_line_obj.unlink(cr,uid,all_packing_list_line_ids)  
          for line in invoice.invoice_line:
             reminder=pallet_qty=tray_qty=can_qty=0
             pallet=tray=can=p_weight=t_weight=c_weight=0 
             for package in line.product_id.packaging:
                 if package.ul.type=='pallet':
                     pallet=package.qty
                     p_weight=package.weight
                 if package.ul.type=='box':
                     tray=package.qty
                     t_weight=package.weight
                 if package.ul.type=='unit':
                    can=package.qty
                    c_weight=package.weight     
             
             if pallet:
                pallet_qty=line.quantity/pallet
                reminder=line.quantity%pallet
                if tray and reminder: 
                   tray_qty=reminder/tray
                   reminder=reminder%tray
                if can and reminder:  
                   can_qty=reminder/can
             elif tray:
                tray_qty=line.quantity/tray
                reminder=line.quantity%tray 
                if can and reminder:  
                   can_qty=reminder/can
             elif can:
                can_qty=line.quantity/can
             
             if line.product_id.packaging:
                 total_product_qty+=(line.quantity)  
                 total_net_weight+=c_weight*line.quantity
             total_pallet_qty+=int(pallet_qty) 
             total_tray_qty+=int(tray_qty)
             total_can_qty+=int(can_qty) 
             total_gross_weight+=pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             vals={}
             vals['product_id'] = line.product_id.id
             vals['name'] = line.product_id.name
             vals['product_qty']=line.quantity
             vals['pallet'] = pallet_qty
             vals['tray'] = tray_qty
             vals['can'] = can_qty
             vals['net_weight'] =c_weight*line.quantity
             vals['grass_weight'] =pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             vals['invoice_id']=invoice.id
             if pallet_qty or tray_qty or can_qty:
               packing_list_line_obj.create(cr,uid,vals)
          
          if total_pallet_qty or total_tray_qty or total_can_qty:
              vals={}
              vals['name'] ='Total'
              vals['product_qty']=total_product_qty
              vals['pallet'] = total_pallet_qty
              vals['tray'] = total_tray_qty
              vals['can'] = total_can_qty
              vals['net_weight'] =total_net_weight
              vals['grass_weight'] =total_gross_weight
              vals['invoice_id']=invoice.id
              packing_list_line_obj.create(cr,uid,vals)
        
        return True
   
account_invoice()

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'package_list_lines': fields.one2many('packing.list.line', 'order_id', 'Package Lines',) , 
        'trademark':fields.char('Trade Mark',size=512),
    }
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sale order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
            [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'sale_id':order.id,
            'trademark':order.trademark,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals

    
    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_obj = self.pool.get('account.invoice')
        obj_invoice_line = self.pool.get('account.invoice.line')
        if context is None:
            context = {}
        invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
        from_line_invoice_ids = []
        for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
            for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                    from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
        for preinv in order.invoice_ids:
            if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                for preline in preinv.invoice_line:
                    inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
                    lines.append(inv_line_id)
        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
        inv_id = inv_obj.create(cr, uid, inv, context=context)
        for package_line in order.package_list_lines:
            self.pool.get('packing.list.line').write(cr, uid, [package_line.id], {'invoice_id':inv_id})
        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
        if data.get('value', False):
            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
        inv_obj.button_compute(cr, uid, [inv_id])
        return inv_id


    def _prepare_order_picking(self, cr, uid, order, context=None):
        pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.out')
        return {
            'name': pick_name,
            'origin': order.name,
            'date': order.date_order,
            'type': 'out',
            'state': 'auto',
            'move_type': order.picking_policy,
            'sale_id': order.id,
            'partner_id': order.partner_shipping_id.id,
            'note': order.note,
            'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
            'company_id': order.company_id.id,
        }
        
    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        location_id = order.shop_id.warehouse_id.lot_stock_id.id
        output_id = order.shop_id.warehouse_id.lot_output_id.id
        for package_line in order.package_list_lines:
            self.pool.get('packing.list.line').write(cr, uid, [package_line.id], {'picking_id':picking_id})
        
        return {
            'name': line.name.split('\n')[0][:250],
            'picking_id': picking_id,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                             or line.product_uom.id,
            'product_packaging': line.product_packaging.id,
            'partner_id': line.address_allotment_id.id or order.partner_shipping_id.id,
            'location_id': location_id,
            'location_dest_id': output_id,
            'sale_line_id': line.id,
            'tracking_id': False,
            'state': 'draft',
            #'state': 'waiting',
            'note': '\n'.join(line.name.split('\n')[1:]),
            'company_id': order.company_id.id,
            'price_unit': line.product_id.standard_price or 0.0
        }
        
    def generate_packing_list(self, cr, uid, ids, context=None):
        packing_list_line_obj = self.pool.get('packing.list.line')
        for order in self.browse(cr, uid, ids, context):
          total_product_qty=total_pallet_qty=total_tray_qty=total_can_qty=0
          total_net_weight=total_gross_weight=0  
          all_packing_list_line_ids=packing_list_line_obj.search(cr,uid,[('order_id','=',order.id)])
          packing_list_line_obj.unlink(cr,uid,all_packing_list_line_ids)  
          for line in order.order_line:
             reminder=pallet_qty=tray_qty=can_qty=0
             pallet=tray=can=p_weight=t_weight=c_weight=0 
             for package in line.product_id.packaging:
                 if package.ul.type=='pallet':
                     pallet=package.qty
                     p_weight=package.weight
                 if package.ul.type=='box':
                     tray=package.qty
                     t_weight=package.weight
                 if package.ul.type=='unit':
                    can=package.qty
                    c_weight=package.weight     
             
             if pallet:
                pallet_qty=line.product_uom_qty/pallet
                reminder=line.product_uom_qty%pallet
                if tray and reminder: 
                   tray_qty=reminder/tray
                   reminder=reminder%tray
                if can and reminder:  
                   can_qty=reminder/can
             elif tray:
                tray_qty=line.product_uom_qty/tray
                reminder=line.product_uom_qty%tray 
                if can and reminder:  
                   can_qty=reminder/can
             elif can:
                can_qty=line.product_uom_qty/can
             
             if line.product_id.packaging:
                 total_product_qty+=(line.product_uom_qty)  
                 total_net_weight+=c_weight*line.product_uom_qty
             total_pallet_qty+=int(pallet_qty) 
             total_tray_qty+=int(tray_qty)
             total_can_qty+=int(can_qty) 
             total_gross_weight+=pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             
             vals={}
             vals['product_id'] = line.product_id.id
             vals['name'] = line.product_id.name
             vals['product_qty']=line.product_uom_qty
             vals['pallet'] = pallet_qty
             vals['tray'] = tray_qty
             vals['can'] = can_qty
             vals['net_weight'] =c_weight*line.product_uom_qty
             vals['grass_weight'] =pallet_qty*p_weight+tray_qty*t_weight+can_qty*c_weight
             vals['order_id']=order.id
             if pallet_qty or tray_qty or can_qty:
               packing_list_line_obj.create(cr,uid,vals)
          if total_pallet_qty or total_tray_qty or total_can_qty:
              vals={}
              vals['name'] ='Total'
              vals['product_qty']=total_product_qty
              vals['pallet'] = total_pallet_qty
              vals['tray'] = total_tray_qty
              vals['can'] = total_can_qty
              vals['net_weight'] =total_net_weight
              vals['grass_weight'] =total_gross_weight
              vals['order_id']=order.id
              packing_list_line_obj.create(cr,uid,vals)
        return True
   
sale_order()# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    
