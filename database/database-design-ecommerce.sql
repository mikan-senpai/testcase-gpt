-- Simple E-commerce POC Database Design
-- Minimal structure similar to the provided example

users {
	id int pk
	user_type_id int > user_types.id
	stripe_id varchar
	email varchar
	password varchar
	is_active boolean
	token_google varchar
	token_facebook varchar
	user_token varchar
	token_expiration datetime
}

user_types {
	id int pk
	type varchar -- 'customer', 'admin', 'vendor'
}

user_addresses {
	id int pk
	user_id int > users.id
	title varchar -- 'Home', 'Work', 'Other'
	address varchar
	city varchar
	postal_code varchar
}

user_carts {
	id int pk
	user_id int > users.id
	product_id int > products.id
	quantity int
	cart_session_id varchar
}

products {
	id int pk
	category_id int > categories.id
	name varchar
	description varchar
	price decimal
	stock int
	image_url varchar
}

categories {
	id int pk
	name varchar
	parent_id int > categories.id
}

orders {
	id int pk
	user_id int > users.id
	address_id int > user_addresses.id
	total decimal
	status varchar -- 'pending', 'paid', 'shipped', 'delivered'
	payment_token varchar
	created_at datetime
}

order_items {
	id int pk
	order_id int > orders.id
	product_id int > products.id
	quantity int
	added_at datetime
}

reviews {
	id int pk
	customer_id int > customers.id
	product_id int > products.id
	order_item_id int > order_items.id
	rating int
	title varchar
	comment text
	is_verified_purchase boolean
	helpful_count int
	created_at datetime
	updated_at datetime
}

wishlists {
	id int pk
	customer_id int > customers.id
	name varchar
	is_public boolean
	created_at datetime
}

wishlist_items {
	id int pk
	wishlist_id int > wishlists.id
	product_id int > products.id
	added_at datetime
	priority int
}

notifications {
	id int pk
	user_id int
	user_type varchar -- 'customer', 'vendor'
	notification_type_id int > notification_types.id
	title varchar
	message text
	is_read boolean
	action_url varchar
	created_at datetime
}

notification_types {
	id int pk
	type varchar -- 'order_placed', 'order_shipped', 'payment_received', 'review_posted'
	icon varchar
	priority varchar
}
