import asyncpg
from datetime import datetime
import asyncio
import os
import json
from decimal import Decimal


class DatabaseManager:
    def __init__(self):
        self.user = 'user'
        self.password = 'password'
        self.host = 'postgres'
        self.port = '5432'
        self.database = 'database'
        self.connection = None

        # self.user = 'postgres'
        # self.password = '1'
        # self.host = 'localhost'
        # self.port = '5432'
        # self.database = 'postgres'
        # self.connection = None

    async def connect(self):
        self.connection = await asyncpg.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def execute_query(self, query, *args):
        return await self.connection.fetch(query, *args)

    async def execute_write_query(self, query, *args):
        await self.connection.execute(query, *args)


class AuthDataBase(DatabaseManager):
    def __init__(self):
        super().__init__()

    async def create_db(self):
        await self.connect()
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS auth (
                id SERIAL PRIMARY KEY,
                phone_number TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                fio TEXT NOT NULL
            )
        ''')
        await self.close()

    async def drop_db(self):
        await self.connect()
        await self.execute_write_query('DROP TABLE IF EXISTS auth')
        await self.close()

    async def get_all_users(self):
        await self.connect()
        query = 'SELECT * FROM auth'
        result = await self.execute_query(query)
        await self.close()
        return result

    async def signin_user(self, phone_number, password):
        await self.connect()
        query = 'SELECT id, phone_number, fio FROM auth WHERE phone_number = $1 AND password = $2'
        result = await self.execute_query(query, phone_number, password)
        await self.close()
        
        if result:
            # Возвращаем словарь с данными пользователя
            return {
                'id': result[0]['id'],
                'phone_number': result[0]['phone_number'],
                'fio': result[0]['fio']
            }
        else:
            # Возвращаем None, если пользователь не найден
            return None

    async def signup_user(self, phone_number, password, fio):
        try:
            await self.connect()
            query = 'INSERT INTO auth (phone_number, password, fio) VALUES ($1, $2, $3) RETURNING id'
            result = await self.execute_query(query, phone_number, password, fio)
            await self.close()
            return result[0]['id']
        
        except:
            return None

    async def edit_user(self, phone_number: str, parameter: str, parameter_value: str):
        await self.connect()
        query = f'UPDATE auth SET {parameter} = $1 WHERE phone_number = $2'
        await self.execute_write_query(query, parameter_value, phone_number)
        await self.close()

    async def delete_user(self, phone_number: str):
        await self.connect()
        query = 'DELETE FROM auth WHERE phone_number = $1'
        await self.execute_write_query(query, phone_number)
        await self.close()

class OrderProductDatabase(DatabaseManager):
    def __init__(self):
        super().__init__()

    async def create_db(self):
        auth = AuthDataBase()
        await auth.create_db()

        await self.connect()
        
        # Создание таблицы "Заказы"
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                customer_name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                comment TEXT,
                source TEXT,
                mp_order_number TEXT,
                order_total DECIMAL(10, 2),
                payment_amount DECIMAL(10, 2),
                lift_fee DECIMAL(10, 2),
                qr_code TEXT
            )
        ''')

        # Создание таблицы "Товары"
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                package_name TEXT NOT NULL,
                package_barcode TEXT NOT NULL,
                package_quantity INTEGER NOT NULL
            )
        ''')


        # Создание связующей таблицы "Заказ-Товар" с каскадным удалением
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(product_id),
                PRIMARY KEY (order_id, product_id)
            )
        ''')

        # Изменение таблицы "Курьеры"
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS couriers (
                courier_id INTEGER PRIMARY KEY
            )
        ''')

        # Создание связующей таблицы "Курьер-Заказ"
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS courier_orders (
                courier_id INTEGER REFERENCES couriers(courier_id),
                order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
                PRIMARY KEY (courier_id, order_id)
            )
        ''')

        # Создание таблицы "Доставленные заказы"
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS delivered_orders (
                order_id INTEGER PRIMARY KEY,
                courier_id INTEGER,
                photo TEXT,
                delivery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        ''')


        # Создание таблицы "Недоставленные заказы"
        await self.execute_write_query('''
            CREATE TABLE IF NOT EXISTS undelivered_orders (
                order_id INTEGER PRIMARY KEY,
                courier_id INTEGER,
                delivery_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        ''')

        await self.close()

    async def drop_db(self):
        auth = AuthDataBase()
        await auth.drop_db()
        
        await self.connect()
        await self.execute_write_query('DROP TABLE IF EXISTS courier_orders')
        await self.execute_write_query('DROP TABLE IF EXISTS couriers')
        await self.execute_write_query('DROP TABLE IF EXISTS order_items')
        await self.execute_write_query('DROP TABLE IF EXISTS orders')
        await self.execute_write_query('DROP TABLE IF EXISTS products')
        await self.execute_write_query('DROP TABLE IF EXISTS couriers')
        await self.execute_write_query('DROP TABLE IF EXISTS courier_orders')
        await self.execute_write_query('DROP TABLE IF EXISTS delivered_orders')
        await self.execute_write_query('DROP TABLE IF EXISTS undelivered_orders')

        await self.close()

    async def get_all_orders(self):
        """Получает все заказы"""
        await self.connect()
        query = 'SELECT * FROM orders'
        result = await self.execute_query(query)
        await self.close()
        return [dict(row) for row in result]

    async def get_all_products(self):
        """Получает все товары"""
        await self.connect()
        query = 'SELECT * FROM products'
        result = await self.execute_query(query)
        await self.close()
        return [dict(row) for row in result]

    async def get_all_courier_orders(self):
        """Получает все назначения заказов курьерам"""
        await self.connect()
        query = '''
            SELECT co.courier_id, co.order_id, o.customer_name, o.address, o.phone
            FROM courier_orders co
            JOIN orders o ON co.order_id = o.order_id
        '''
        result = await self.execute_query(query)
        await self.close()
        return [dict(row) for row in result]

    # Методы для работы с заказами
    async def create_order(self, customer_name, address, phone, comment, source, mp_order_number, order_total, payment_amount, lift_fee, qr_code):
        await self.connect()
        query = '''
            INSERT INTO orders (customer_name, address, phone, comment, source, mp_order_number, order_total, payment_amount, lift_fee, qr_code)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING order_id
        '''
        result = await self.execute_query(query, customer_name, address, phone, comment, source, mp_order_number, order_total, payment_amount, lift_fee, qr_code)
        await self.close()
        return result[0]['order_id']

    async def get_order(self, order_id):
        await self.connect()
        query = 'SELECT * FROM orders WHERE order_id = $1'
        result = await self.execute_query(query, order_id)
        await self.close()
        return result[0] if result else None

    async def create_product(self, package_name, package_barcode, package_quantity):
        await self.connect()
        query = '''
            INSERT INTO products (package_name, package_barcode, package_quantity)
            VALUES ($1, $2, $3)
            RETURNING product_id
        '''
        result = await self.execute_query(query, package_name, package_barcode, package_quantity)
        await self.close()
        return result[0]['product_id']


    async def get_product(self, product_id):
        await self.connect()
        query = 'SELECT * FROM products WHERE product_id = $1'
        result = await self.execute_query(query, product_id)
        await self.close()
        return result[0] if result else None

    async def add_products_to_order(self, order_id, products):
        """
        Добавляет несколько товаров к заказу.
        :param order_id: ID заказа
        :param products: список product_id
        """
        await self.connect()
        async with self.connection.transaction():
            for product_id in products:
                query = '''
                    INSERT INTO order_items (order_id, product_id)
                    VALUES ($1, $2)
                    ON CONFLICT (order_id, product_id) 
                    DO NOTHING
                '''
                await self.execute_write_query(query, order_id, product_id)
        await self.close()

    # Метод для получения всех товаров в заказе
    async def get_order_with_items(self, order_id):
        """
        Получает информацию о заказе вместе со всеми связанными товарами.
        """
        await self.connect()
        query = '''
            SELECT o.*, 
                   json_agg(json_build_object(
                       'product_id', p.product_id, 
                       'package_name', p.package_name, 
                       'package_barcode', p.package_barcode, 
                       'package_quantity', p.package_quantity
                   )) as items
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE o.order_id = $1
            GROUP BY o.order_id
        '''
        result = await self.execute_query(query, order_id)
        await self.close()
        return dict(result[0]) if result else None

    
    async def delete_order(self, order_id: int):
        """
        Удаляет заказ по его ID. Связанные записи в таблице order_items
        будут удалены автоматически благодаря каскадному удалению.
        """
        await self.connect()
        query = 'DELETE FROM orders WHERE order_id = $1 RETURNING order_id'
        result = await self.execute_query(query, order_id)
        await self.close()
        return result[0]['order_id'] if result else None
    
    async def create_courier(self, courier_id: int):
        """Создает нового курьера, используя id из таблицы auth"""
        await self.connect()
        try:
            query = '''
                INSERT INTO couriers (courier_id)
                VALUES ($1)
                RETURNING courier_id
            '''
            result = await self.execute_query(query, courier_id)
            await self.close()
            return result[0]['courier_id']
        except asyncpg.exceptions.UniqueViolationError:
            await self.close()
            raise ValueError("Курьер с таким ID уже существует")
        except Exception as e:
            await self.close()
            raise e
    
    async def assign_order_to_courier(self, courier_id: int, order_id: int):
        """Назначает заказ курьеру"""
        await self.connect()
        query = '''
            INSERT INTO courier_orders (courier_id, order_id)
            VALUES ($1, $2)
        '''
        await self.execute_write_query(query, courier_id, order_id)
        await self.close()

    async def get_courier_orders(self, courier_id: int):
        """Получает все заказы курьера вместе с товарами"""
        await self.connect()
        query = '''
            SELECT o.*, 
                   json_agg(json_build_object(
                       'product_id', p.product_id, 
                       'package_name', p.package_name, 
                       'package_barcode', p.package_barcode, 
                       'package_quantity', p.package_quantity
                   )) as items
            FROM courier_orders co
            JOIN orders o ON co.order_id = o.order_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE co.courier_id = $1
            GROUP BY o.order_id
        '''
        result = await self.execute_query(query, courier_id)
        await self.close()
        orders = []
        for row in result:
            order = dict(row)
            order['items'] = json.loads(order['items']) if order['items'] else []
            orders.append(order)
        return orders

    
    async def remove_order_from_courier(self, courier_id: int, order_id: int):
        """Удаляет заказ у курьера"""
        await self.connect()
        try:
            query = '''
                DELETE FROM courier_orders
                WHERE courier_id = $1 AND order_id = $2
                RETURNING order_id
            '''
            result = await self.execute_query(query, courier_id, order_id)
            await self.close()
            return result[0]['order_id'] if result else None
        except asyncpg.exceptions.ForeignKeyViolationError:
            await self.close()
            raise ValueError("Заказ или курьер не существует")
        except Exception as e:
            await self.close()
            raise e
    
    async def mark_order_as_delivered(self, order_id: int, courier_id: int, photo: str, reason: str):
        await self.connect()
        try:
            async with self.connection.transaction():
                # Проверяем, существует ли заказ
                order_query = 'SELECT * FROM orders WHERE order_id = $1'
                order_data = await self.execute_query(order_query, order_id)

                if not order_data:
                    raise ValueError(f"Заказ с ID {order_id} не найден")

                # Проверяем, назначен ли заказ курьеру
                check_query = 'SELECT * FROM courier_orders WHERE order_id = $1 AND courier_id = $2'
                assigned = await self.execute_query(check_query, order_id, courier_id)

                if not assigned:
                    raise ValueError(f"Заказ с ID {order_id} не назначен курьеру с ID {courier_id}")

                # Вставляем новую запись в таблицу delivered_orders
                insert_query = '''
                    INSERT INTO delivered_orders (order_id, courier_id, photo, reason, delivery_time)
                    VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP)
                '''
                await self.execute_write_query(insert_query, order_id, courier_id, photo, reason)

                # Удаляем заказ из courier_orders
                delete_query = 'DELETE FROM courier_orders WHERE order_id = $1 AND courier_id = $2'
                await self.execute_write_query(delete_query, order_id, courier_id)

            print(f"Заказ {order_id} успешно отмечен как доставленный")
            return True
        except Exception as e:
            print(f"Ошибка при отметке заказа как доставленного: {str(e)}")
            return False
        finally:
            await self.close()
    
    async def mark_order_as_undelivered(self, order_id: int, courier_id: int, reason: str):
        await self.connect()
        try:
            # Проверяем, существует ли заказ
            order_query = 'SELECT * FROM orders WHERE order_id = $1'
            order_data = await self.execute_query(order_query, order_id)
            
            if not order_data:
                raise ValueError(f"Заказ с ID {order_id} не найден")

            # Проверяем, назначен ли заказ курьеру
            check_query = 'SELECT * FROM courier_orders WHERE order_id = $1 AND courier_id = $2'
            assigned = await self.execute_query(check_query, order_id, courier_id)
            
            if not assigned:
                raise ValueError(f"Заказ с ID {order_id} не назначен курьеру с ID {courier_id}")

            # Вставляем данные в таблицу undelivered_orders
            insert_query = '''
                INSERT INTO undelivered_orders (order_id, courier_id, reason)
                VALUES ($1, $2, $3)
                ON CONFLICT (order_id) DO UPDATE
                SET courier_id = $2, delivery_time = CURRENT_TIMESTAMP, reason = $3
            '''
            await self.execute_write_query(insert_query, order_id, courier_id, reason)

            # Удаляем заказ из courier_orders
            delete_query = 'DELETE FROM courier_orders WHERE order_id = $1 AND courier_id = $2'
            await self.execute_write_query(delete_query, order_id, courier_id)

        except Exception as e:
            await self.close()
            raise e

        await self.close()

    
    async def get_delivered_orders(self):
        """Получает все доставленные заказы"""
        await self.connect()
        query = '''
            SELECT d.order_id, d.courier_id, d.delivery_time, 
                   o.customer_name, o.address, o.phone, o.order_total
            FROM delivered_orders d
            JOIN orders o ON d.order_id = o.order_id
        '''
        result = await self.execute_query(query)
        await self.close()
        return [dict(row) for row in result]

    async def get_undelivered_orders(self):
        """Получает все недоставленные заказы"""
        await self.connect()
        query = '''
            SELECT u.order_id, u.courier_id, u.delivery_time, u.reason,
                   o.customer_name, o.address, o.phone, o.order_total
            FROM undelivered_orders u
            JOIN orders o ON u.order_id = o.order_id
        '''
        result = await self.execute_query(query)
        await self.close()
        return [dict(row) for row in result]
    
    async def clear_orders(self):
        await self.connect()
        try:
            await self.execute_write_query('DELETE FROM orders')
            print("Все записи успешно удалены из таблицы orders.")
        except Exception as e:
            print(f"Произошла ошибка при очистке таблицы orders: {str(e)}")
        finally:
            await self.close()

    async def clear_products(self):
        await self.connect()
        try:
            await self.execute_write_query('DELETE FROM products')
            print("Все записи успешно удалены из таблицы products.")
        except Exception as e:
            print(f"Произошла ошибка при очистке таблицы products: {str(e)}")
        finally:
            await self.close()

    async def clear_order_items(self):
        await self.connect()
        try:
            await self.execute_write_query('DELETE FROM order_items')
            print("Все записи успешно удалены из таблицы order_items.")
        except Exception as e:
            print(f"Произошла ошибка при очистке таблицы order_items: {str(e)}")
        finally:
            await self.close()

    async def clear_delivered_order(self, order_id: int):
        await self.connect()
        try:
            query = 'DELETE FROM delivered_orders WHERE order_id = $1'
            result = await self.execute_write_query(query, order_id)
            # if result == 'DELETE 1':
            return f"Запись с order_id {order_id} успешно удалена из таблицы delivered_orders."
            # else:
            #     return f"Запись с order_id {order_id} не найдена в таблице delivered_orders."
        except Exception as e:
            return f"Произошла ошибка при удалении записи из таблицы delivered_orders: {str(e)}"
        finally:
            await self.close()

    async def clear_undelivered_order(self, order_id: int):
        await self.connect()
        try:
            query = 'DELETE FROM undelivered_orders WHERE order_id = $1'
            result = await self.execute_write_query(query, order_id)
            # if result == 'DELETE 1':
            return f"Запись с order_id {order_id} успешно удалена из таблицы undelivered_orders."
            # else:
            #     print(f"Запись с order_id {order_id} не найдена в таблице undelivered_orders.")
        except Exception as e:
            return f"Произошла ошибка при удалении записи из таблицы undelivered_orders: {str(e)}"
        finally:
            await self.close()

    async def clear_all_delivered_orders(self):
        await self.connect()
        try:
            await self.execute_write_query('DELETE FROM delivered_orders')
            return "Все записи успешно удалены из таблицы delivered_orders."
        except Exception as e:
            return f"Произошла ошибка при очистке таблицы delivered_orders: {str(e)}"
        finally:
            await self.close()

    async def clear_all_undelivered_orders(self):
        await self.connect()
        try:
            await self.execute_write_query('DELETE FROM undelivered_orders')
            return "Все записи успешно удалены из таблицы undelivered_orders."
        except Exception as e:
            return f"Произошла ошибка при очистке таблицы undelivered_orders: {str(e)}"
        finally:
            await self.close()



    
# async def main():
#     db = OrderProductDatabase()
#     a = await db.mark_order_as_delivered(order_id=1, courier_id=1, photo='test.jpg', reason='test2')
#     print(a)
# # #     print(await db.get_delivered_orders())
    
#     # Пересоздаем базу данных с новой структурой
    # await db.drop_db()
    # await db.create_db()
    
# # # #     # Создаем заказы
# # # #     order_id1 = await db.create_order("Иван Иванов", "ул. Пушкина, д. 10", "+79001234567", 
# # # #                                       "Позвонить перед доставкой", "Сайт", "MP-123456", 
# # # #                                       1000.00, 950.00, 50.00, "QR12345")
# # # #     order_id2 = await db.create_order("Петр Петров", "ул. Лермонтова, д. 20", "+79009876543", 
# # # #                                       "Оставить у двери", "Приложение", "MP-789012", 
# # # #                                       1500.00, 1450.00, 50.00, "QR67890")
    
# # # #     # Создаем товары и добавляем их к заказам
# # # #     product_id1 = await db.create_product("Набор посуды", "Коробка 1", "1234567890", 1)
# # # #     product_id2 = await db.create_product("Столовые приборы", "Коробка 2", "0987654321", 2)
# # # #     await db.add_products_to_order(order_id1, [(product_id1, 2), (product_id2, 1)])
# # # #     await db.add_products_to_order(order_id2, [(product_id1, 1), (product_id2, 2)])
    
# # # #     # Создаем курьера (предполагается, что courier_id=1 уже существует в таблице auth)
# # # #     courier_id = await db.create_courier(1)
    
# # # #     # Назначаем заказы курьеру
# # # #     await db.assign_order_to_courier(courier_id, order_id1)
# # # #     await db.assign_order_to_courier(courier_id, order_id2)
    
# # # #     # Получаем все заказы курьера
# # # #     print("Заказы курьера:")
# # # #     courier_orders = await db.get_courier_orders(courier_id)
# # # #     for order in courier_orders:
# # # #         print(f"Заказ ID: {order['order_id']}, Клиент: {order['customer_name']}")
    
# # # #     # # Удаляем один заказ у курьера
# # # #     # removed_order_id = await db.remove_order_from_courier(courier_id, order_id1)
# # # #     # print(f"\nУдален заказ с ID: {removed_order_id}")
    
# # # #     # Снова получаем все заказы курьера
# # # #     print("\nЗаказы курьера после удаления:")
# # # #     courier_orders = await db.get_courier_orders(courier_id)
# # # #     for order in courier_orders:
# # # #         print(f"Заказ ID: {order['order_id']}, Клиент: {order['customer_name']}")

# if __name__ == '__main__':
#     asyncio.run(main())