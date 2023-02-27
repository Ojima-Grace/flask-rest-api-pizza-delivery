from flask_restx import Namespace, Resource, fields
from ..models.orders import Order
from ..models.users import User
from ..utils import db
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity

order_namespace = Namespace('orders', description='Name Space For Order')

order_model = order_namespace.model(
    'Order', {
        'id': fields.Integer(description='An ID'),
        'size': fields.String(description='Size of Pizza', required=True,
                              enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']
        ),
        'order_status': fields.String(description='The Status Of Our Order', required=True,
                                       enum=['PENDING', 'IN_TRANSIT', 'DELIVERED']
        ),
        'flavour': fields.String(description='Flavour Of Pizza', required=True),
        'quantity': fields.Integer(description='Quantity of Pizza', required=True)
    }
)

order_status_model = order_namespace.model(
    'OrderStatus', {
        'order_status': fields.String(required=True, description='Order Status',
        enum = ['PENDING', 'IN_TRANSIT', 'DELIVERED'])
    }
)

@order_namespace.route('/orders')
class OrderGetCreate(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description='Get All Orders'
    )
    @jwt_required()
    def get(self):
        """

           Get All Orders

        """
        orders = Order.query.all()

        return orders, HTTPStatus.OK
    
    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description='Place An Order'
    )
    @jwt_required()
    def post(self):
        """
           Place All Orders

        """
        username = get_jwt_identity()

        current_user = User.query.filter_by(username=username).first()

        data = order_namespace.payload

        new_order = Order(
            size = data['size'],
            quantity = data['quantity'],
            flavour = data['flavour']
        )

        new_order.user = current_user
        new_order.save()

        return new_order, HTTPStatus.CREATED

@order_namespace.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = 'Retrieve An Order By ID',
        params = {'order_id': 'An ID For An Order'}
    )
    @jwt_required()
    def get(self, order_id):
        """

           Retrieving an order by id

        """
        order = Order.get_by_id(order_id)

        return order, HTTPStatus.OK

    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = 'Update An Order By ID',
        params = {'order_id': 'An ID For An Order'}
    )
    @jwt_required()
    def put(self, order_id):
        """

           Update an order by id

        """
        order_to_update = Order.get_by_id(order_id)

        data = order_namespace.payload

        order_to_update.quantity = data["quantity"]
        order_to_update.size = data["size"]
        order_to_update.flavour = data["flavour"]

        db.session.commit()

        return order_to_update, HTTPStatus.OK
    
    @order_namespace.doc(
            description = 'Delete An Order By ID',
            params = {'order_id': 'An ID For An Order'}
    )
    @jwt_required()
    def delete(self, order_id):
        """

           Delete an order by id

        """
        order_to_delete = Order.get_by_id(order_id)
        order_to_delete.delete()

        return {"message": "Deleted Successfully!"}, HTTPStatus.OK

@order_namespace.route('/user/<int:user_id>/order/<int:order_id>')
class GetSpecificOrderByUser(Resource):
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = 'Get A SPecific Order By User ID And Order ID',
        params = {'user_id': 'An ID For A User',
                  'order_id': 'An ID For An Order'}
    )
    @jwt_required()
    def get(self, user_id, order_id):
        """

           Get a User Specific Order

        """
        user = User.get_by_id(user_id)
        order = Order.query.filter_by(id=order_id).filter_by(user=user).first()

        return order, HTTPStatus.OK

@order_namespace.route('/user/<int:user_id>/order')
class UserOrder(Resource):
    @order_namespace.marshal_list_with(order_model)
    @order_namespace.doc(
        description = 'Get All User Orders',
        params = {'user_id': 'An ID For A User'}
    )
    @jwt_required()
    def get(self, user_id):
        """

           Get all user Orders

        """
        user = User.get_by_id(user_id)
        orders = user.orders

        return orders, HTTPStatus.OK

@order_namespace.route('/order/status/<int:order_id>')
class UpdateOrdersStatus(Resource):
    @order_namespace.expect(order_status_model)
    @order_namespace.marshal_with(order_model)
    @order_namespace.doc(
        description = 'Update An Order\'s Status',
        params = {'order_id': 'An ID For An Order'}
    )
    @jwt_required()
    def patch(self, order_id):
        """

           Update an order's Status

        """
        data = order_namespace.payload
        order_to_update = Order.get_by_id(order_id)
        order_to_update.order_status = data["order_status"]
        db.session.commit()

        return order_to_update, HTTPStatus.OK