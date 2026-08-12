from app import db
from app.models import Product, Sale, SaleItem
import uuid
from app.utils.logger import Logger

class SaleService:
    @staticmethod
    def process_sale(items, total_amount, payment_method, user_id, tenant_id, customer_id=None):
        """
        Backend logic to process a sale, update stock, and record inventory movements.
        """
        try:
            # 1. Validation: Check stock levels before processing
            for item in items:
                product = Product.query.get(item['id'])
                if not product or product.stock_quantity < int(item['qty']):
                    raise Exception(f"Alaabta {product.name if product else 'Unknown'} stock-geedu kuma filna!")

            # 2. Create the Sale record
            new_sale = Sale(
                invoice_no='INV-' + str(uuid.uuid4())[:8].upper(),
                total_amount=total_amount,
                payment_method=payment_method,
                user_id=user_id,
                tenant_id=tenant_id,
                customer_id=customer_id
            )
            db.session.add(new_sale)
            db.session.flush()

            # 3. Create items and update stock
            for item in items:
                product = Product.query.get(item['id'])
                qty = int(item['qty'])
                
                # Update Stock
                product.stock_quantity -= qty
                
                # Record SaleItem
                sale_item = SaleItem(
                    sale_id=new_sale.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=float(item['price']),
                    buy_price=product.buy_price
                )
                db.session.add(sale_item)

            # 4. Success Log
            Logger.log(user_id, "SALE_COMPLETED", f"Invoice {new_sale.invoice_no}: Total ${total_amount}", tenant_id)

            # 5. Professional Accounting Integration
            from app.services.accounting_service import AccountingService
            AccountingService.record_sale(new_sale)

            db.session.commit()
            return new_sale
        except Exception as e:
            db.session.rollback()
            raise e
