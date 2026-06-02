from flask import Flask, render_template, request, redirect, url_for
import database
import os
from werkzeug.utils import secure_filename
from admin_setup import init_admin

UPLOAD_FOLDER = os.path.join("static", "product_images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

database.create_tables()
init_admin(app)


# --- DASHBOARD ---

@app.route("/")
def dashboard():
    total_orders  = database.total_orders_count()
    revenue       = database.total_revenue()
    total_cust    = len(database.get_all_customers())
    cancelled     = database.total_canceled_orders()
    recent_orders = database.get_all_orders()[:5]
    return render_template("dashboard.html",
        total_orders=total_orders,
        revenue=revenue,
        total_cust=total_cust,
        cancelled=cancelled,
        recent_orders=recent_orders,
        top_products=database.top_selling_products(5)
    )


# --- CUSTOMERS ---

@app.route("/customers")
def customers():
    keyword   = request.args.get("keyword", "")
    filter_by = request.args.get("filter_by", "name")
    if keyword:
        data = database.search_customer(keyword, filter_by)
    else:
        data = database.get_all_customers()
    return render_template("customers.html", customers=data, keyword=keyword, filter_by=filter_by)

@app.route("/customers/add", methods=["POST"])
def add_customer():
    database.add_customer(
        request.form["name"],
        request.form["email"],
        request.form["phone"],
        request.form["street"],
        request.form["city"],
        request.form["state"],
        request.form["pincode"],
        request.form["country"]
    )
    return redirect(url_for("customers"))


# --- PRODUCTS ---

@app.route("/products")
def products():
    keyword   = request.args.get("keyword", "")
    filter_by = request.args.get("filter_by", "name")
    if keyword:
        data = database.search_product(keyword, filter_by)
    else:
        data = database.get_all_products()
    return render_template("products.html", products=data, keyword=keyword, filter_by=filter_by)

@app.route("/products/add", methods=["POST"])
def add_product():
    image_path = None
    image_file = request.files.get("image")

    if image_file and image_file.filename != "":
        filename = secure_filename(f"{request.form['sku']}_{image_file.filename}")
        image_file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_path = filename

    database.add_product(
        request.form["sku"], request.form["name"],
        request.form["category"], request.form["price"],
        request.form["stock"], image_path
    )
    return redirect(url_for("products"))


@app.route("/products/update-image", methods=["POST"])
def update_product_image():
    sku        = request.form["sku"]
    image_file = request.files.get("image")

    if image_file and image_file.filename != "":
        filename = secure_filename(f"{sku}_{image_file.filename}")
        image_file.save(os.path.join(UPLOAD_FOLDER, filename))
        database.update_product_image(sku, filename)

    return redirect(url_for("products"))






@app.route("/products/update-stock", methods=["POST"])
def update_stock():
    database.update_product_stock(request.form["sku"], request.form["new_stock"])
    return redirect(url_for("products"))

@app.route("/products/update-price", methods=["POST"])
def update_price():
    database.update_product_price(request.form["sku"], request.form["new_price"])
    return redirect(url_for("products"))

@app.route("/products/delete", methods=["POST"])
def delete_product():
    database.delete_product(request.form["sku"])
    return redirect(url_for("products"))


# --- ORDERS ---

@app.route("/orders")
def orders():
    keyword   = request.args.get("keyword", "")
    filter_by = request.args.get("filter_by", "order_id")
    if keyword:
        data = database.search_orders(keyword, filter_by)
    else:
        data = database.get_all_orders()
    all_customers = database.get_all_customers()
    return render_template("orders.html", orders=data, keyword=keyword,
                           filter_by=filter_by, all_customers=all_customers)




@app.route("/orders/<order_id>")
def order_details(order_id):
    items = database.get_order_details(order_id)
    return render_template("order_details.html", order_id=order_id, items=items)



@app.route("/customers/update", methods=["POST"])
def update_customer():
    database.update_customer(
        request.form["customer_id"],
        request.form["phone"],
        request.form["street"],
        request.form["city"],
        request.form["state"],
        request.form["pincode"],
        request.form["country"]
    )
    return redirect(url_for("customers"))





@app.route("/customers/delete", methods=["POST"])
def delete_customer():
    success = database.delete_customer(request.form["customer_id"])
    if not success:
        return redirect(url_for("customers", msg="Cannot delete — customer has existing orders.", msg_type="error"))
    return redirect(url_for("customers", msg="Customer deleted successfully.", msg_type="success"))




@app.route("/orders/place", methods=["POST"])
def place_order():
    customer_id = request.form["customer_id"]
    address_id  = database.get_address_id(customer_id)
    if not address_id:
        return redirect(url_for("orders"))
    skus       = request.form.getlist("sku")
    quantities = request.form.getlist("quantity")
    items = [{"sku": int(skus[i]), "quantity": int(quantities[i])} for i in range(len(skus))]
    database.place_order(customer_id, address_id, items)
    return redirect(url_for("orders"))

@app.route("/orders/update-status", methods=["POST"])
def update_order_status():
    database.update_order_status(request.form["order_id"], request.form["new_status"])
    return redirect(url_for("orders"))


# --- REPORTS ---

@app.route("/reports")
def reports():
    return render_template("reports.html",
        total_orders  = database.total_orders_count(),
        revenue       = database.total_revenue(),
        cancelled     = database.total_canceled_orders(),
        top_products  = database.top_selling_products(),
        city_orders   = database.orders_by_city()
    )


if __name__ == "__main__":
    app.run(debug=True)