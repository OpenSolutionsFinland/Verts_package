import time
from report import report_sxw

class package_invoice_reports(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(package_invoice_reports, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time':time,
            'get_information':self.get_information,
            'get_supplier_information':self.get_supplier_information,
            'get_total_product_qty':self.get_total_product_qty,
            'get_bank_detail':self.get_bank_detail
            })
        
    def get_supplier_information(self,obj):
        result = []
        vals = {}
        vals['name']=vals['phone']=vals['street']=vals['street2']=vals['city']=vals['zip']=vals['mobile']=vals['state_id']=vals['country_id']=''
        for line in obj.invoice_line:
            for supplier in line.product_id.seller_ids:
                    vals['name']=supplier.name.name
                    vals['phone']=supplier.name.phone
                    vals['street']=supplier.name.street
                    vals['street2']=supplier.name.street2
                    vals['city']=supplier.name.city
                    vals['zip']=supplier.name.zip
                    vals['mobile']=supplier.name.mobile
                    vals['state_id']=supplier.name.state_id.name
                    vals['country_id']=supplier.name.country_id.name
                    break
                        
            result.append(vals)
        return result
    def get_bank_detail(self,obj):
        result = []
        dict = {}
        dict['bank']=dict['acc_number']=''
        for company in obj.company_id.bank_ids:
            dict['bank'] = company.bank_name
            dict['acc_number'] = company.acc_number
            break
        result.append(dict)
        return result
         
    def get_total_product_qty(self,obj):
        result = []
        dict = {}
        total_qty = 0
        total_price = 0
        dict['total_qty']=dict['total_price']=''
        for line_id in obj.invoice_line:
           if line_id.quantity:
               total_qty = total_qty+ line_id.quantity
           if line_id.price_unit:
               total_price = total_price+ line_id.price_unit
           dict['total_qty'] = total_qty
           dict['total_price'] = total_price
           result.append(dict)
        return result
        
    def get_information(self,o):
        result = []
        total_net_weight = total_gross_weight = total_excluding_vat = 0
        for line_id in o.invoice_line:
            total_excluding_vat+= o.amount_untaxed
            dic={}
            dic['product_id'] =dic['default_code'] =dic['amount_pcs'] =dic['unit_price'] =dic['price_subtotal'] =dic['tax']=dic['total_excluding_vat']=''
            dic['net_weight'] = dic['gross_weight']= dic['total_net_weight'] = dic['total_product_qty'] = dic['total_gross_weight'] = dic['total_pallet'] = '' 
            dic['total_tray'] = dic['total_can'] =''
            dic['total_excluding_vat'] = total_excluding_vat 
            for val in o.package_list_lines:
                if line_id.product_id == val.product_id :
                    dic['net_weight'] = val.net_weight
                    dic['gross_weight'] = val.grass_weight
                if val.name=='Total':
                    dic['total_net_weight'] = val.net_weight
                    dic['total_product_qty'] = val.product_qty
                    dic['total_gross_weight'] = val.grass_weight 
                    dic['total_pallet'] = val.pallet 
                    dic['total_tray'] = val.tray 
                    dic['total_can'] = val.can    
            tax=','.join([ str(lt.amount) or '' for lt in line_id.invoice_line_tax_id])
            dic['product_id'] = line_id.product_id.name
            dic['default_code'] = line_id.product_id.default_code
            dic['amount_pcs'] = line_id.quantity
            dic['unit_price'] = line_id.price_unit
            dic['price_subtotal'] = line_id.price_subtotal
            dic['tax'] = tax
            result.append(dic)
        return result
         
report_sxw.report_sxw('report.package_invoice_reports', 'account.invoice', 'addons/verts_package/package_invoice.rml', parser=package_invoice_reports, header = False)

class package_preview_list(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(package_preview_list, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time':time,
            'packing_information':self.packing_information,
            'packing_supplier_information':self.packing_supplier_information,
            'packing_bank_detail':self.packing_bank_detail
            })
        
    def packing_bank_detail(self,obj):
        result = []
        dict = {}
        dict['bank']=dict['acc_number']=''
        for company in obj.company_id.bank_ids:
            dict['bank'] = company.bank_name
            dict['acc_number'] = company.acc_number
            break
        result.append(dict)
        return result
    
    def packing_supplier_information(self,obj):
        result = []
        vals = {}
        vals['name']=vals['phone']=vals['street']=vals['street2']=vals['city']=vals['zip']=vals['state_id']=vals['country_id']=''
        for line in obj.move_lines:
            for supplier in line.product_id.seller_ids:
                    vals['name']=supplier.name.name
                    vals['phone']=supplier.name.phone
                    vals['street']=supplier.name.street
                    vals['street2']=supplier.name.street2
                    vals['city']=supplier.name.city
                    vals['zip']=supplier.name.zip
                    vals['state_id']=supplier.name.state_id.name
                    vals['country_id']=supplier.name.country_id.name
                    break            
            result.append(vals)
        return result
         
    def packing_information(self,obj):
        result = []
        total_volume=0
        for line_id in obj.move_lines:
            dic={}
            total_volume+= line_id.product_qty*line_id.product_id.volume
            dic['net_weight'] = dic['gross_weight'] = dic['total_volume'] =dic['total_net_weight'] = dic['total_product_qty'] =dic['total_gross_weight'] =dic['total_pallet'] = '' 
            dic['total_tray'] = dic['total_can'] = dic['product_id'] = dic['default_code'] = dic['amount_pcs'] = dic['volume'] = dic['ean13'] = dic['custom_code']= ''
            for val in obj.package_list_lines:
                if line_id.product_id == val.product_id :
                    dic['net_weight'] = val.net_weight
                    dic['gross_weight'] = val.grass_weight
                if val.name=='Total':
                    dic['total_volume'] = total_volume
                    dic['total_net_weight'] = val.net_weight
                    dic['total_product_qty'] = val.product_qty
                    dic['total_gross_weight'] = val.grass_weight 
                    dic['total_pallet'] = val.pallet 
                    dic['total_tray'] = val.tray 
                    dic['total_can'] = val.can       
            dic['product_id'] = line_id.product_id.name
            dic['default_code'] = line_id.product_id.default_code
            dic['amount_pcs'] = line_id.product_qty
            dic['volume'] = line_id.product_qty*line_id.product_id.volume
            dic['ean13'] = line_id.product_id.ean13
            dic['custom_code'] = line_id.product_id.custom_code
            result.append(dic)
        return result
        
report_sxw.report_sxw('report.stock.picking.package_list', 'stock.picking', 'addons/verts_package/package_preview.rml', parser=package_preview_list, header = False)


