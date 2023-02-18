from flask_restx import Namespace, Resource, fields
from ..models.order import Order
from ..models.user import User
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils import db

order_namespace = Namespace("order", description="name space for order")

# @order_namespace.route("/")
# class HelloOrder(Resource):
#     def get(self):
#         return {"message":"hello order nice to meet you."}

view_model = order_namespace.model(
    "Order", {
        "id":fields.Integer(),
        "size":fields.String(description="Size of order",required =True,
        enum = ["SMALL","MEDIUM", "LARGE","EXTRA_LARGE"] 
        ),
        "order_status": fields.String(required =True, description = "The status of the Order",
        enum=["PENDING", "IN_TRANSIT", "DELIVERED"]
        ),
        "flavour": fields.String(description= "Flavour of pizza", required=True),
        "quantity":fields.Integer(description="Quantity of pizza", required=True)
    })

@order_namespace.route('/orders')
class OrderGetCreate(Resource):
    @order_namespace.marshal_with(view_model)
    @jwt_required()
    def get(self):
        """
            Get all orders
        """
        orders = Order.query.all()
        return orders, HTTPStatus.OK

    @order_namespace.expect(view_model)
    @jwt_required()
    def post(self):
        """
            Place an order
        """
        username = get_jwt_identity()

        current_user = User.query.filter_by(username=username).first()
        data = order_namespace.payload

        new_order = Order(
            size = data["size"],
            quantity = data["quantity"],
            flavour = data["flavour"]
        )
        new_order.user = current_user

        new_order.save()
        return data, HTTPStatus.CREATED


@order_namespace.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):
    @order_namespace.marshal_with(view_model)
    @jwt_required()

    def get(self, order_id):
        """
            Retrieve an order by ID
        """
        order = Order.get_by_id(order_id)
        return order, HTTPStatus.OK

    @order_namespace.expect(view_model)
    @order_namespace.marshal_with(view_model)
    @jwt_required()
    def put(self, order_id):
        """
            Update an order )by ID
        """
        order_to_update = Order.get_by_id(order_id)
        data = order_namespace.payload
        # payload takes the schema and convert it to json

        order_to_update.quantity = data["quantity"]
        order_to_update.size = data["size"]
        order_to_update.flavour = data["flavour"]

        db.session.commit()

        return order_to_update, HTTPStatus.OK

    @order_namespace.expect(view_model)
    # @order_namespace.marshal_with(view_model)
    @jwt_required()
    def delete(self, order_id):
        """
            Delete an order by ID
        """
        delete_order = Order.get_by_id(order_id)
        db.session.delete(delete_order)
        db.session.commit()

        return {"message":"order successfully deleted"}, HTTPStatus.OK

@order_namespace.route('/user/<int:user_id>/order/<int:order_id>')
class GetSpecificOrderByUser(Resource):
    @order_namespace.marshal_list_with(view_model)
    @jwt_required()
    def get(self, user_id, order_id):
        """
            Get a user's specific order
        """
        user = User.get_by_id(user_id)
        order = Order.query.filter_by(id=order_id).filter_by(user=user).first()

        return order, HTTPStatus.OK

@order_namespace.route('/user/<int:user_id>/orders')
class UserOrders(Resource):
    @order_namespace.marshal_list_with(view_model)
    @jwt_required()
    def get(self, user_id):
        """
            Get all orders by a user
        """
        user = User.get_by_id(user_id)
        orders = user.orders

        return orders, HTTPStatus.OK

@order_namespace.route('/order/status/<int:order_id>')
class UpdateOrderStatus(Resource):
    def patch(self, order_id):
        """
            Update an order's status
        """
        pass